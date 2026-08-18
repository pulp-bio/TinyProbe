// Author: Soumyo Bhattacharjee
module tinyprobe_qspi_transport #(
    parameter int N_FIFOS = 16,
    parameter int IN_DATA_WIDTH = 20,
    parameter int READ_CNT_WIDTH = 12,
    parameter int REG_ADDR_W = 4
) (
    input logic spi_sclk_i, spi_cs_ni, spi_io0_i, spi_io1_i,
    output logic spi_io0_o, spi_io1_o,
    output logic [1:0] spi_pad_oe_o,
    input logic core_clk_i, rst_ni,
    input logic [N_FIFOS-1:0] fifos_empty_i,
    input logic [N_FIFOS*IN_DATA_WIDTH-1:0] fifos_data_i,
    input logic [N_FIFOS-1:0] fifos_en_i,
    input logic [READ_CNT_WIDTH-1:0] read_cnt_i,
    // Stage-3A capture diagnostics originate in the AFE frame-clock domain.
    // They are synchronized locally before being reported at status address F.
    input logic [7:0] stage3_frame_gray_i,
    input logic stage3_enable_meta_i, stage3_enable_sync_i,
    input logic [READ_CNT_WIDTH-1:0] stage3_wr_count_gray_i,
    input logic stage3_req_seen_i, stage3_start_asserted_i, stage3_wr_done_i,
    input logic stage3_lane0_nonempty_i,
    input logic [2:0] stage3_state_i,
    output logic [N_FIFOS-1:0] fifos_read_req_o,
    output logic capture_start_o,
    output logic fifo_reader_busy_o,
    // Scalar Stage-3A mode indication for the top-level frame-domain path.
    // Keep this separate from config_regs_o so both the transport status and
    // the capture controller use one canonical decoded signal.
    output logic stage3_enable_o,
    output logic [15:0][31:0] config_regs_o
);
    localparam logic [7:0] CMD_REG_READ = 8'h4c;
    localparam logic [7:0] CMD_STREAM_READ = 8'h6b;
    localparam logic [3:0] STATUS_ADDR = 4'hf;
    // Temporary mailbox-observability diagnostic. The serial response is a
    // status word so the QSPI pads remain independently proven while the
    // real request/response mailboxes execute in the background.
    // Keep the diagnostic instrumentation in the RTL, but use the normal
    // register-read datapath for the next hardware test.  Any individual
    // diagnostic below can be re-enabled without reconstructing the design.
    // Current focused hardware test: return the direct core snapshot.  This
    // bypasses only the response mailbox, while still proving the SPI-to-core
    // request mailbox and register-array selection.
    localparam bit DIAG_MAILBOX_OBSERVABILITY = 1'b0;
    // Second diagnostic stage: return the response payload captured in the
    // SPI clock domain, while retaining direct valid timing for the serial
    // transmitter.  This isolates mailbox data integrity from controller
    // valid/load timing.
    localparam bit DIAG_RETURN_MAILBOX_PAYLOAD = 1'b0;
    // Third diagnostic stage: snapshot the core-side address and selected
    // register data at the exact cycle that creates the response payload.
    localparam bit DIAG_CORE_READ_SNAPSHOT = 1'b0;
    // Fourth diagnostic stage: return the command and address captured by
    // the SPI controller itself. This is independent of both mailboxes.
    localparam bit DIAG_SPI_ADDRESS_SNAPSHOT = 1'b0;
    // Fifth diagnostic stage: fixed word used to calibrate MCU dual-data RX
    // edge, lane order, and dummy-boundary alignment before trusting captured
    // command/address diagnostics.
    localparam bit DIAG_FIXED_TX_PATTERN = 1'b0;
    // Sixth diagnostic stage: return a stable core-domain snapshot directly
    // through two SPI-clock synchronizer stages. This bypasses only the
    // response mailbox and therefore distinguishes core data generation from
    // response-arrival timing.
    localparam bit DIAG_DIRECT_CORE_SNAPSHOT = 1'b0;
    // Seventh diagnostic stage: retain the complete core-to-SPI snapshot
    // crossing, but remove register storage from the payload.  This isolates
    // a CDC/serial corruption from an unreset or overwritten register value.
    localparam bit DIAG_CORE_SNAPSHOT_FIXED_WORD = 1'b0;
    // Return the source-side data register of the write mailbox.  This is
    // temporary evidence that the final dual-data symbol was captured before
    // CS released; it does not depend on the 60 MHz destination side.
    localparam bit DIAG_RETURN_SPI_WRITE_CAPTURE = 1'b0;
    // Capture the final 0x32 payload candidate before the mailbox applies
    // ready.  This proves whether the controller reached DATA_RX and saw all
    // sixteen dual symbols, even when the mailbox source stays empty.
    localparam bit DIAG_RETURN_SPI_WRITE_CANDIDATE = 1'b0;
    // First write-path checkpoint: command decode plus all three address
    // bytes, captured precisely as the FSM enters DATA_RX.  This happens
    // before the payload and does not depend on a trailing SCLK edge.
    localparam bit DIAG_RETURN_SPI_WRITE_ENTRY = 1'b0;
    // Report the independently recorded number of dual payload symbols and
    // the lower sixteen received payload bits after CS has risen.  It is a
    // passive SPI-domain diagnostic; normal write behaviour is unaffected.
    localparam bit DIAG_RETURN_SPI_WRITE_PROGRESS = 1'b0;
    // Return the complete controller-assembled write word captured on the
    // final payload falling edge.  This bypasses both mailboxes and the
    // register bank, isolating SPI receive assembly alone.
    localparam bit DIAG_RETURN_SPI_WRITE_FULL = 1'b0;
    logic [31:0] core_wr_data, core_rd_data, reg_data_o;
    logic [3:0] core_pad_oe;
    logic [23:0] core_wr_addr;
    logic [7:0] latched_cmd;
    logic core_wr_valid, core_wr_ready, core_reg_rd_req, core_rd_valid, core_rd_ready;
    logic core_wr_begin;
    logic core_wr_data_active;
    logic [23:0] core_wr_begin_addr;
    logic [35:0] wr_mb_data, wr_mb_spi_data;
    logic wr_mb_valid, rd_req_mb_valid, rd_rsp_mb_valid, rd_rsp_mb_ready;
    logic [3:0] rd_req_mb_data, reg_addr_i;
    logic [31:0] rd_rsp_mb_data, rd_rsp_data_now, rd_rsp_hold_q;
    logic [31:0] dbg_spi_write_candidate_q, dbg_spi_write_entry_q;
    logic [31:0] dbg_spi_write_full_q;
    logic [31:0] dbg_spi_write_progress_data_q;
    logic [5:0]  dbg_spi_write_progress_count_q;
    logic rd_rsp_hold_valid_q;
    logic cmd_start_q, cmd_reset_q, cmd_stream_start_q;
    logic sw_rst_no, reader_valid, reader_ready, reader_busy;
    logic [7:0] reader_data;
    logic [1:0] pack_count_q;
    logic [31:0] pack_word_q;
    logic stream_full, stream_empty, stream_rd_valid, stream_rd_en;
    logic [31:0] stream_rd_data, stream_hold_q;
    logic stream_hold_valid_q, stream_fetch_pending_q, stream_ready_q, stream_started_q, stream_overflow_q, stream_underflow_q;
    logic stream_rst_ni;
    logic stream_seed_enable;
    logic stream_reader_test_enable;
    logic stream_stage3_enable;
    logic [4:0] stream_seed_count_q;
    logic [4:0] stream_reader_test_reads_q;
    logic stream_fifo_wr_en;
    logic [31:0] stream_fifo_wr_data;
    logic [N_FIFOS-1:0] reader_fifos_empty_i, reader_fifos_en_i, reader_fifos_read_req;
    logic [N_FIFOS*IN_DATA_WIDTH-1:0] reader_fifos_data_i;
    logic [7:0] stage3_frame_gray_meta_q, stage3_frame_gray_core_q;
    logic stage3_enable_meta_meta_q, stage3_enable_meta_core_q;
    logic stage3_enable_sync_meta_q, stage3_enable_sync_core_q;
    logic [READ_CNT_WIDTH-1:0] stage3_wr_count_gray_meta_q, stage3_wr_count_gray_core_q;
    logic stage3_req_seen_meta_q, stage3_req_seen_core_q;
    logic stage3_start_asserted_meta_q, stage3_start_asserted_core_q;
    logic stage3_wr_done_meta_q, stage3_wr_done_core_q;
    logic [2:0] stage3_state_meta_q, stage3_state_core_q;
    logic [READ_CNT_WIDTH-1:0] stage3_wr_count_bin;
    logic reg_write_valid;
    logic [7:0] dbg_core_count_q;
    logic [7:0] dbg_core_gray_q, dbg_core_gray_meta_q, dbg_core_gray_spi_q;
    logic dbg_req_seen_core_q, dbg_rsp_issued_core_q;
    logic dbg_req_seen_meta_q, dbg_req_seen_spi_q;
    logic dbg_rsp_issued_meta_q, dbg_rsp_issued_spi_q;
    logic dbg_rsp_seen_spi_q;
    logic [7:0] dbg_rise_cmd_q;
    logic [3:0] dbg_rise_cmd_count_q;
    logic [31:0] dbg_core_snapshot_q, dbg_core_snapshot_meta_q, dbg_core_snapshot_spi_q;
    logic [3:0] dbg_snapshot_addr_q;
    logic dbg_snapshot_pending_q;

    function automatic logic [READ_CNT_WIDTH-1:0] gray_to_bin(
        input logic [READ_CNT_WIDTH-1:0] gray_i
    );
        integer bit_idx;
        begin
            gray_to_bin[READ_CNT_WIDTH-1] = gray_i[READ_CNT_WIDTH-1];
            for (bit_idx = READ_CNT_WIDTH-2; bit_idx >= 0; bit_idx = bit_idx - 1)
                gray_to_bin[bit_idx] = gray_to_bin[bit_idx+1] ^ gray_i[bit_idx];
        end
    endfunction

    spi_quad_slave #(.ENABLE_DUAL(1'b1)) i_spi_quad_slave (
        .spi_sclk(spi_sclk_i), .spi_cs_n(spi_cs_ni),
        .spi_sdi0(spi_io0_i), .spi_sdi1(spi_io1_i), .spi_sdi2(1'b0), .spi_sdi3(1'b0),
        .spi_sdo0(spi_io0_o), .spi_sdo1(spi_io1_o), .spi_sdo2(), .spi_sdo3(),
        .spi_pad_oe(core_pad_oe), .sys_clk(core_clk_i), .sys_rst_n(rst_ni),
        .wr_data(core_wr_data), .wr_valid(core_wr_valid),
        .wr_begin(core_wr_begin), .wr_begin_addr(core_wr_begin_addr),
        .wr_data_active(core_wr_data_active),
        .wr_ready(core_wr_ready), .wr_addr(core_wr_addr),
        .reg_rd_req(core_reg_rd_req), .rd_data(core_rd_data), .rd_valid(core_rd_valid),
        .rd_ready(core_rd_ready), .latched_cmd(latched_cmd)
    );
    assign spi_pad_oe_o = core_pad_oe[1:0];

    // This is deliberately in the SPI clock domain and survives CS release,
    // so the subsequent 0x4C transaction can report the exact final write
    // candidate without depending on either mailbox.
    always_ff @(negedge spi_sclk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            dbg_spi_write_candidate_q <= '0;
            dbg_spi_write_entry_q     <= '0;
            dbg_spi_write_full_q      <= '0;
            dbg_spi_write_progress_data_q  <= '0;
            dbg_spi_write_progress_count_q <= '0;
        end else begin
            if (core_wr_begin) begin
                // B1 | decoded command | complete low 16 address bits.
                // Expected for the current test: B1_32_000E.
                dbg_spi_write_entry_q <= {8'hb1, latched_cmd, core_wr_begin_addr[15:0]};
                dbg_spi_write_progress_data_q  <= '0;
                dbg_spi_write_progress_count_q <= '0;
            end else if (core_wr_data_active && !spi_cs_ni) begin
                // Independently sample the physical dual input pins.  This is
                // deliberately separate from shift_data_next/core_wr_valid, so
                // it exposes whether the final serial edge itself reaches FPGA.
                dbg_spi_write_progress_data_q <= {dbg_spi_write_progress_data_q[29:0],
                                                   spi_io1_i, spi_io0_i};
                if (dbg_spi_write_progress_count_q != 6'd63)
                    dbg_spi_write_progress_count_q <= dbg_spi_write_progress_count_q + 1'b1;
            end
            if (core_wr_valid) begin
                // B3 | captured command | address | payload[11:0]
                // Expected for this test: B3_32_E_FFF.
                dbg_spi_write_candidate_q <= {8'hb3, latched_cmd,
                                              core_wr_addr[3:0], core_wr_data[11:0]};
                dbg_spi_write_full_q <= core_wr_data;
            end
        end
    end

    tp_req_ack_mailbox #(.WIDTH(36), .SRC_ON_NEGEDGE(1'b1)) i_wr_mailbox (
        .src_clk_i(spi_sclk_i), .src_rst_ni(rst_ni), .src_data_i({core_wr_addr[3:0], core_wr_data}),
        .src_valid_i(core_wr_valid), .src_ready_o(core_wr_ready), .src_captured_data_o(wr_mb_spi_data),
        .dst_clk_i(core_clk_i),
        .dst_rst_ni(rst_ni), .dst_data_o(wr_mb_data), .dst_valid_o(wr_mb_valid)
    );
    tp_req_ack_mailbox #(.WIDTH(4)) i_rd_req_mailbox (
        .src_clk_i(spi_sclk_i), .src_rst_ni(rst_ni), .src_data_i(core_wr_addr[3:0]),
        .src_valid_i(core_reg_rd_req), .src_ready_o(), .dst_clk_i(core_clk_i),
        .dst_rst_ni(rst_ni), .dst_data_o(rd_req_mb_data), .dst_valid_o(rd_req_mb_valid)
    );
    tp_req_ack_mailbox #(.WIDTH(32)) i_rd_rsp_mailbox (
        .src_clk_i(core_clk_i), .src_rst_ni(rst_ni), .src_data_i(rd_rsp_data_now),
        // Launch the response on the same core edge that accepts the read
        // request.  The previous rd_pending_q -> rd_rsp_pending_q sequence
        // consumed two extra 20 MHz cycles, which is longer than the fixed
        // ten-dummy-clock response budget on the physical link.
        .src_valid_i(rd_req_mb_valid), .src_ready_o(rd_rsp_mb_ready), .dst_clk_i(spi_sclk_i),
        .dst_rst_ni(rst_ni), .dst_data_o(rd_rsp_mb_data), .dst_valid_o(rd_rsp_mb_valid)
    );

    assign reg_write_valid = wr_mb_valid && (wr_mb_data[35:32] != STATUS_ADDR);
    // The request mailbox data is stable for its complete valid pulse.  Make
    // it the register-bank address for the normal register-bank interface.
    assign reg_addr_i = rd_req_mb_valid ? rd_req_mb_data : wr_mb_data[35:32];
    // Do not sample reg_data_o on the request-valid edge: reg_data_o is the
    // output of an address mux, and that mux only sees reg_addr_i change
    // after the destination-mailbox flip-flops update.  Selecting the stable
    // raw register array with the already-stable mailbox payload gives the
    // response mailbox the correct word on that same edge.
    assign rd_rsp_data_now = DIAG_CORE_READ_SNAPSHOT ?
                             {8'ha1, 4'h0, rd_req_mb_data, config_regs_o[rd_req_mb_data][15:0]} :
                             (rd_req_mb_data == STATUS_ADDR) ?
                             // Status address 0xF is a transport status word, not the
                             // readable contents of config register 15.  Stage 3A has a
                             // dedicated diagnostic layout while its exclusive bit-28
                             // test mode is selected; all prior layouts remain unchanged.
                             (stream_stage3_enable ?
                              // Status[31:29] expose the exact enable path:
                              // core decode, first frame-clock synchronizer,
                              // second frame-clock synchronizer.  The lower
                              // five bits remain a live Gray frame count, so
                              // existing firmware's upper-byte-change test
                              // remains valid and the low 24-bit ready value
                              // is unchanged.
                              {stream_stage3_enable, stage3_enable_meta_core_q,
                               stage3_enable_sync_core_q, stage3_frame_gray_core_q[4:0], stage3_wr_count_bin,
                               stage3_req_seen_core_q, stage3_start_asserted_core_q,
                               stage3_wr_done_core_q, stage3_lane0_nonempty_i,
                                stage3_state_core_q, stream_stage3_enable,
                                stage3_req_seen_core_q, stream_overflow_q, reader_busy, stream_ready_q} :
                              {20'h0, stream_reader_test_reads_q, stream_reader_test_enable,
                               config_regs_o[13][30], config_regs_o[13][31], stream_underflow_q,
                               stream_overflow_q, reader_busy, stream_ready_q}) :
                             config_regs_o[rd_req_mb_data];
    mem_mapped_regs #(
        .ADDR_SIZE(REG_ADDR_W),
        .REG_WIDTH(32),
        // Register 14 is reserved for the firmware configuration shadow.
        .REG14_DEFAULT(32'h00000000)
    ) i_mem_mapped_regs (
        .clk_i(core_clk_i), .rst_ni(rst_ni), .addr_i(reg_addr_i), .data_o(reg_data_o),
        .data_i(wr_mb_data[31:0]), .wr_en_i(reg_write_valid), .raw_regs_o(config_regs_o)
    );

    // Frame-domain Stage-3A diagnostics cross into the 60 MHz transport
    // domain here. Counters are Gray encoded at their source; the write
    // count is decoded only after the two-flop synchronizer.
    always_ff @(posedge core_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            stage3_frame_gray_meta_q      <= '0;
            stage3_frame_gray_core_q      <= '0;
            stage3_enable_meta_meta_q     <= 1'b0;
            stage3_enable_meta_core_q     <= 1'b0;
            stage3_enable_sync_meta_q     <= 1'b0;
            stage3_enable_sync_core_q     <= 1'b0;
            stage3_wr_count_gray_meta_q   <= '0;
            stage3_wr_count_gray_core_q   <= '0;
            stage3_req_seen_meta_q        <= 1'b0;
            stage3_req_seen_core_q        <= 1'b0;
            stage3_start_asserted_meta_q  <= 1'b0;
            stage3_start_asserted_core_q  <= 1'b0;
            stage3_wr_done_meta_q         <= 1'b0;
            stage3_wr_done_core_q         <= 1'b0;
            stage3_state_meta_q           <= '0;
            stage3_state_core_q           <= '0;
        end else begin
            stage3_frame_gray_meta_q      <= stage3_frame_gray_i;
            stage3_frame_gray_core_q      <= stage3_frame_gray_meta_q;
            stage3_enable_meta_meta_q     <= stage3_enable_meta_i;
            stage3_enable_meta_core_q     <= stage3_enable_meta_meta_q;
            stage3_enable_sync_meta_q     <= stage3_enable_sync_i;
            stage3_enable_sync_core_q     <= stage3_enable_sync_meta_q;
            stage3_wr_count_gray_meta_q   <= stage3_wr_count_gray_i;
            stage3_wr_count_gray_core_q   <= stage3_wr_count_gray_meta_q;
            stage3_req_seen_meta_q        <= stage3_req_seen_i;
            stage3_req_seen_core_q        <= stage3_req_seen_meta_q;
            stage3_start_asserted_meta_q  <= stage3_start_asserted_i;
            stage3_start_asserted_core_q  <= stage3_start_asserted_meta_q;
            stage3_wr_done_meta_q         <= stage3_wr_done_i;
            stage3_wr_done_core_q         <= stage3_wr_done_meta_q;
            stage3_state_meta_q           <= stage3_state_i;
            stage3_state_core_q           <= stage3_state_meta_q;
        end
    end
    assign stage3_wr_count_bin = gray_to_bin(stage3_wr_count_gray_core_q);

    start_gen i_start_gen (.clk_i(core_clk_i), .rst_ni(rst_ni), .trig_in(cmd_start_q),
                           .start_o(capture_start_o), .busy_o());
    sw_rst_gen i_sw_rst_gen (.clk_i(core_clk_i), .rst_ni(rst_ni), .trig_in(cmd_reset_q),
                             .sw_rst_no(sw_rst_no), .sw_rst_o(), .busy_o());
    // Stage-2 smoke test: replace only the rx_fifo_v3 read interface with a
    // finite, request-driven lane-0 source.  The multi_fifo_reader,
    // fifo_h2l_reshaper, byte packer, generated QSPI_STREAM_FIFO and 0x6B
    // transmitter remain on their production connections.
    always_comb begin
        reader_fifos_empty_i = fifos_empty_i;
        reader_fifos_data_i  = fifos_data_i;
        reader_fifos_en_i    = fifos_en_i;
        if (stream_reader_test_enable) begin
            reader_fifos_empty_i = '1;
            reader_fifos_empty_i[0] = 1'b0;
            reader_fifos_data_i = '0;
            reader_fifos_data_i[0 +: IN_DATA_WIDTH] = 20'hA_53C9;
            reader_fifos_en_i = '0;
            // Retain the normal register-2 lane-enable control: lane 0 must
            // still be deliberately selected by firmware for this test.
            reader_fifos_en_i[0] = fifos_en_i[0];
        end
    end
    assign fifos_read_req_o = stream_reader_test_enable ? '0 : reader_fifos_read_req;

    multi_fifo_reader #(
        .N_FIFOS(N_FIFOS), .IN_DATA_WIDTH(IN_DATA_WIDTH), .OUT_DATA_WIDTH(8), .READ_CNT_WIDTH(READ_CNT_WIDTH)
    ) i_multi_fifo_reader (
        .clk_i(core_clk_i), .rst_ni(sw_rst_no), .start_i(cmd_stream_start_q && !stream_seed_enable), .read_cnt_i(read_cnt_i),
        .busy_o(reader_busy), .fifos_en_i(reader_fifos_en_i), .fifos_empty_i(reader_fifos_empty_i),
        .fifos_data_i(reader_fifos_data_i), .fifos_read_req_o(reader_fifos_read_req), .fifos_rst_o(),
        .data_o(reader_data), .valid_o(reader_valid), .ready_i(reader_ready)
    );
    assign fifo_reader_busy_o = reader_busy;
    assign stream_rst_ni = rst_ni & ~cmd_stream_start_q;
    assign stream_seed_enable = config_regs_o[13][30];
    assign stream_reader_test_enable = config_regs_o[13][29] && !stream_seed_enable;
    assign stream_stage3_enable = config_regs_o[13][28] &&
                                  !(|config_regs_o[13][31:29]);
    assign stage3_enable_o = stream_stage3_enable;
    assign reader_ready = !stream_full;

    // Stage-1 hardware smoke test: bypass capture and reader logic, but use
    // the actual generated asynchronous QSPI_STREAM_FIFO and the normal 0x6B
    // response path.  A stream-start command resets the FIFO first; after a
    // ten-core-clock reset-release delay, seed eight known words.  This
    // matches the reset-settle interval used by the generated CoreFIFO testbench.
    assign stream_fifo_wr_en = stream_seed_enable ?
                              ((stream_seed_count_q <= 5'd8) && (stream_seed_count_q != '0)) :
                              (reader_valid && reader_ready && (pack_count_q == 2'd3));
    assign stream_fifo_wr_data = stream_seed_enable ?
                               ((stream_seed_count_q == 5'd8) ? 32'hA53C_9A53 :
                                (stream_seed_count_q == 5'd7) ? 32'hC9A5_3C9A :
                                (stream_seed_count_q == 5'd6) ? 32'h3C9A_53C9 :
                                (stream_seed_count_q == 5'd5) ? 32'h9A53_C9A5 :
                                (stream_seed_count_q == 5'd4) ? 32'h0123_4567 :
                                (stream_seed_count_q == 5'd3) ? 32'h89AB_CDEF :
                                (stream_seed_count_q == 5'd2) ? 32'h55AA_55AA :
                                                                    32'hDEAD_BEEF) :
                                {pack_word_q[23:0], reader_data};
    tp_stream_corefifo i_stream_fifo (
        .rst_ni(stream_rst_ni), .wr_clk_i(core_clk_i),
        .wr_en_i(stream_fifo_wr_en), .wr_data_i(stream_fifo_wr_data), .wr_full_o(stream_full),
        .rd_clk_i(spi_sclk_i), .rd_en_i(stream_rd_en), .rd_data_o(stream_rd_data),
        .rd_valid_o(stream_rd_valid), .rd_empty_o(stream_empty)
    );

    always_ff @(posedge core_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            cmd_start_q <= 1'b0; cmd_reset_q <= 1'b0; cmd_stream_start_q <= 1'b0;
            pack_count_q <= '0; pack_word_q <= '0; stream_ready_q <= 1'b0; stream_started_q <= 1'b0; stream_overflow_q <= 1'b0;
            stream_seed_count_q <= '0;
            stream_reader_test_reads_q <= '0;
        end else begin
            cmd_start_q <= reg_write_valid && (wr_mb_data[35:32] == 4'd0) && (wr_mb_data[7:0] == 8'h01);
            cmd_reset_q <= reg_write_valid && (wr_mb_data[35:32] == 4'd0) && (wr_mb_data[7:0] == 8'h02);
            cmd_stream_start_q <= reg_write_valid && (wr_mb_data[35:32] == 4'd0) && (wr_mb_data[7:0] == 8'h03);
            if (cmd_stream_start_q) begin
                pack_count_q <= '0; pack_word_q <= '0; stream_ready_q <= 1'b0; stream_started_q <= 1'b0; stream_overflow_q <= 1'b0;
                // Counts 18 down to 1: ten reset-settle clocks followed by
                // the eight writes encoded above.
                stream_seed_count_q <= stream_seed_enable ? 5'd18 : '0;
                stream_reader_test_reads_q <= '0;
            end else begin
                if (stream_reader_test_enable && reader_fifos_read_req[0] &&
                    (stream_reader_test_reads_q != 5'd31))
                    stream_reader_test_reads_q <= stream_reader_test_reads_q + 1'b1;
                if (stream_seed_enable) begin
                    if (stream_seed_count_q != '0)
                        stream_seed_count_q <= stream_seed_count_q - 1'b1;
                    if (stream_seed_count_q == 5'd1)
                        stream_ready_q <= 1'b1;
                end else begin
                    if (reader_valid && reader_ready) begin
                        pack_word_q <= {pack_word_q[23:0], reader_data};
                        pack_count_q <= pack_count_q + 1'b1;
                    end
                    if (reader_busy) stream_started_q <= 1'b1;
                    if (stream_started_q && !reader_busy) stream_ready_q <= 1'b1;
                    if (reader_valid && stream_full) stream_overflow_q <= 1'b1;
                end
            end
        end
    end

    // Direct-snapshot diagnostic.  Capture one core edge after the request,
    // rather than on the mailbox destination-valid edge itself.  The latter
    // is a registered pulse, so sampling the indexed raw-register bus on
    // that exact edge is needlessly vulnerable to destination-register and
    // routing skew.  This one-cycle staging is diagnostic-only; the normal
    // response mailbox remains immediate-launch.
    always_ff @(posedge core_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            dbg_core_snapshot_q  <= '0;
            dbg_snapshot_addr_q  <= '0;
            dbg_snapshot_pending_q <= 1'b0;
        end else begin
            dbg_snapshot_pending_q <= rd_req_mb_valid;
            if (rd_req_mb_valid) begin
                dbg_snapshot_addr_q <= rd_req_mb_data;
            end
            if (dbg_snapshot_pending_q) begin
                dbg_core_snapshot_q <= DIAG_CORE_SNAPSHOT_FIXED_WORD ?
                                       32'ha10e5aa5 :
                                       {8'ha1, 4'h0, dbg_snapshot_addr_q,
                                        config_regs_o[dbg_snapshot_addr_q][15:0]};
            end
        end
    end

    // Diagnostic-only core-domain evidence.  The Gray count crosses safely
    // into the SPI domain and proves that core_clk_i is physically toggling.
    always_ff @(posedge core_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            dbg_core_count_q      <= '0;
            dbg_req_seen_core_q   <= 1'b0;
            dbg_rsp_issued_core_q <= 1'b0;
        end else begin
            dbg_core_count_q <= dbg_core_count_q + 1'b1;
            if (rd_req_mb_valid) dbg_req_seen_core_q <= 1'b1;
            if (rd_req_mb_valid && rd_rsp_mb_ready) dbg_rsp_issued_core_q <= 1'b1;
        end
    end
    assign dbg_core_gray_q = dbg_core_count_q ^ (dbg_core_count_q >> 1);

    // Synchronize diagnostic evidence back into the working SPI clock
    // domain.  These sticky flags deliberately survive CS deassertion so a
    // second read can inspect what happened during the first one.
    always_ff @(posedge spi_sclk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            dbg_core_gray_meta_q      <= '0;
            dbg_core_gray_spi_q       <= '0;
            dbg_req_seen_meta_q       <= 1'b0;
            dbg_req_seen_spi_q        <= 1'b0;
            dbg_rsp_issued_meta_q     <= 1'b0;
            dbg_rsp_issued_spi_q      <= 1'b0;
            dbg_rsp_seen_spi_q        <= 1'b0;
            dbg_core_snapshot_meta_q  <= '0;
            dbg_core_snapshot_spi_q   <= '0;
        end else begin
            dbg_core_gray_meta_q  <= dbg_core_gray_q;
            dbg_core_gray_spi_q   <= dbg_core_gray_meta_q;
            dbg_req_seen_meta_q   <= dbg_req_seen_core_q;
            dbg_req_seen_spi_q    <= dbg_req_seen_meta_q;
            dbg_rsp_issued_meta_q <= dbg_rsp_issued_core_q;
            dbg_rsp_issued_spi_q  <= dbg_rsp_issued_meta_q;
            dbg_core_snapshot_meta_q <= dbg_core_snapshot_q;
            dbg_core_snapshot_spi_q  <= dbg_core_snapshot_meta_q;
            if (rd_rsp_mb_valid) dbg_rsp_seen_spi_q <= 1'b1;
        end
    end

    // Edge-calibration sampler.  The production controller captures command
    // bits on falling SCLK edges for mode 1.  This independent sampler records
    // the first eight rising-edge IO0 samples without changing that logic.
    always_ff @(posedge spi_sclk_i or negedge rst_ni or posedge spi_cs_ni) begin
        if (!rst_ni || spi_cs_ni) begin
            dbg_rise_cmd_q       <= '0;
            dbg_rise_cmd_count_q <= '0;
        end else if (dbg_rise_cmd_count_q < 4'd8) begin
            dbg_rise_cmd_q       <= {dbg_rise_cmd_q[6:0], spi_io0_i};
            dbg_rise_cmd_count_q <= dbg_rise_cmd_count_q + 1'b1;
        end
    end

    // The generated pipelined/prefetch CoreFIFO consumes RE immediately but
    // its RAM Q output must settle through the read port before this transport
    // latches it.  Do not read until 0x6B has been decoded, then insert one
    // SPI-clock capture stage between RE and stream_hold_q.
    assign stream_rd_en = !spi_cs_ni && (latched_cmd == CMD_STREAM_READ) &&
                          !stream_empty && !stream_hold_valid_q && !stream_fetch_pending_q;
    always_ff @(posedge spi_sclk_i or negedge rst_ni or posedge spi_cs_ni) begin
        if (!rst_ni || spi_cs_ni) begin
            rd_rsp_hold_q <= '0; rd_rsp_hold_valid_q <= 1'b0; stream_hold_q <= '0;
            stream_hold_valid_q <= 1'b0; stream_fetch_pending_q <= 1'b0; stream_underflow_q <= 1'b0;
        end else begin
            if (rd_rsp_mb_valid && !rd_rsp_hold_valid_q) begin
                rd_rsp_hold_q <= rd_rsp_mb_data; rd_rsp_hold_valid_q <= 1'b1;
            end
            if (stream_rd_en) begin
                stream_fetch_pending_q <= 1'b1;
            end
            if (stream_fetch_pending_q) begin
                stream_hold_q <= stream_rd_data; stream_hold_valid_q <= 1'b1;
                stream_fetch_pending_q <= 1'b0;
            end
            if (core_rd_ready) begin
                if (latched_cmd == CMD_REG_READ) rd_rsp_hold_valid_q <= 1'b0;
                if (latched_cmd == CMD_STREAM_READ) begin
                    if (!stream_hold_valid_q) stream_underflow_q <= 1'b1;
                    stream_hold_valid_q <= 1'b0;
                end
            end
        end
    end
    assign core_rd_data = DIAG_MAILBOX_OBSERVABILITY ?
                          (DIAG_RETURN_SPI_WRITE_FULL ? dbg_spi_write_full_q :
                           DIAG_RETURN_SPI_WRITE_PROGRESS ?
                           {8'hb4, 3'b000, dbg_spi_write_progress_count_q[4:0],
                            dbg_spi_write_progress_data_q[15:0]} :
                           DIAG_RETURN_SPI_WRITE_ENTRY ? dbg_spi_write_entry_q :
                           DIAG_RETURN_SPI_WRITE_CANDIDATE ? dbg_spi_write_candidate_q :
                           DIAG_RETURN_SPI_WRITE_CAPTURE ?
                           {8'hb2, 4'h0, wr_mb_spi_data[35:32], wr_mb_spi_data[15:0]} :
                           DIAG_DIRECT_CORE_SNAPSHOT ? dbg_core_snapshot_spi_q :
                           DIAG_FIXED_TX_PATTERN ? 32'ha53c9669 :
                           DIAG_SPI_ADDRESS_SNAPSHOT ?
                           {8'ha3, dbg_rise_cmd_q, latched_cmd, core_wr_addr[7:0]} :
                           DIAG_RETURN_MAILBOX_PAYLOAD ? rd_rsp_hold_q :
                           {8'hd6, dbg_core_gray_spi_q, 13'h0,
                            dbg_rsp_seen_spi_q, dbg_rsp_issued_spi_q,
                            dbg_req_seen_spi_q}) :
                          (latched_cmd == CMD_REG_READ) ? rd_rsp_hold_q :
                          (latched_cmd == CMD_STREAM_READ) ? stream_hold_q : 32'h0;
    assign core_rd_valid = DIAG_MAILBOX_OBSERVABILITY ? 1'b1 :
                           (latched_cmd == CMD_REG_READ) ? rd_rsp_hold_valid_q :
                           (latched_cmd == CMD_STREAM_READ) ? 1'b1 : 1'b0;
endmodule

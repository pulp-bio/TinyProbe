/**
 * Mode-1 SPI transaction controller (CPOL=0, CPHA=1).
 * Incoming symbols and transaction state are sampled on falling SCLK edges;
 * the shift engine launches read symbols on rising SCLK edges.
 */
module spi_quad_controller #(
    parameter bit ENABLE_DUAL = 1'b0
) (
    input  logic        sclk,
    input  logic        sys_rst_n,
    input  logic        cs_n,
    output logic        shift_en,
    output logic        rx_mode,
    output logic        data_phase,
    output logic [5:0]  rx_frame_clks,
    input  logic [31:0] shift_data_next,
    input  logic        shift_done,
    input  logic        tx_done,
    output logic        load_en,
    output logic [31:0] load_data,
    output logic [31:0] sys_wr_data,
    output logic        sys_wr_valid,
    // One-SCLK predictive pulse at the address-to-write-data boundary.  It
    // is intentionally independent of the final payload capture and is used
    // only by the transport's SPI-domain write bring-up diagnostic.
    output logic        sys_wr_begin,
    output logic [23:0] sys_wr_begin_addr,
    // Level indication for the SPI-domain payload-progress diagnostic.
    output logic        sys_wr_data_active,
    input  logic        sys_wr_ready,
    output logic [23:0] latched_addr,
    output logic        sys_reg_rd_req,
    input  logic [31:0] sys_rd_data,
    input  logic        sys_rd_valid,
    output logic        sys_rd_ready,
    output logic [7:0]  latched_cmd,
    output logic [3:0]  spi_pad_oe
);

    typedef enum logic [3:0] { IDLE, CMD, ADDR_1, ADDR_2, ADDR_3,
                               DUMMY, DATA_RX, DATA_TX } state_t;
    state_t state, state_next;
    localparam logic [3:0] ACTIVE_PAD_OE = ENABLE_DUAL ? 4'b0011 : 4'b1111;
    localparam logic [5:0] SERIAL_FRAME_CLKS   = 6'd8;
    // One common read protocol budget.  It covers the register-read CDC
    // round trip and is also used by the normal FIFO/stream read command.
    // Firmware and the SSI hardware have been calibrated to this exact
    // response boundary.  Keep both sides at ten dummy clocks.
    localparam logic [5:0] READ_DUMMY_CLKS = 6'd10;

    logic is_write, is_read, is_reg_read;
    logic [31:0] wr_data_reg, tx_load_data;
    logic rd_ready_pending, tx_load_pending;

    spi_quad_cmd_decoder cmd_dec (
        .cmd_i(latched_cmd), .is_write_o(is_write), .is_read_o(is_read),
        .is_reg_read_o(is_reg_read), .is_invalid_o()
    );

    // This is predictive of the final mode-1 capture edge.  shift_data_next
    // already includes the IO1/IO0 pair about to be sampled, allowing the
    // write mailbox source to commit on that same falling SCLK edge.
    assign sys_wr_data  = ((state == DATA_RX) && shift_done) ? shift_data_next : wr_data_reg;
    // The mailbox applies its own ready qualification at the capture edge.
    // Keep this candidate independent of ready so diagnostics can distinguish
    // a missing write phase from a source mailbox that is not ready.
    assign sys_wr_valid = (state == DATA_RX) && shift_done;
    // At this falling edge latched_addr[23:8] is already complete; the final
    // address byte is shift_data_next.  This therefore captures the complete
    // command/address before the first dual-data symbol is consumed.
    assign sys_wr_begin      = (state == ADDR_3) && shift_done && is_write;
    assign sys_wr_begin_addr = {latched_addr[23:8], shift_data_next[7:0]};
    assign sys_wr_data_active = (state == DATA_RX);
    assign sys_rd_ready = rd_ready_pending;
    assign load_en      = tx_load_pending;
    assign load_data    = tx_load_data;

    always_comb begin
        state_next = state;
        shift_en   = 1'b0;
        rx_mode    = 1'b1;
        data_phase = 1'b0;
        rx_frame_clks = SERIAL_FRAME_CLKS;
        spi_pad_oe = 4'b0000;

        case (state)
            // Keep capture pre-armed while CS is high.  CS asynchronously
            // resets the shifter, so no symbol is accepted until CS is low;
            // this guarantees the first falling edge after CS assertion is
            // command bit 7 rather than an IDLE-entry bubble.
            IDLE: begin
                shift_en = 1'b1;
                if (!cs_n) begin
                    state_next = CMD;
                end
            end
            CMD: begin
                shift_en = 1'b1;
                if (shift_done) state_next = ADDR_1;
            end
            ADDR_1: begin
                shift_en = 1'b1;
                if (shift_done) state_next = ADDR_2;
            end
            ADDR_2: begin
                shift_en = 1'b1;
                if (shift_done) state_next = ADDR_3;
            end
            ADDR_3: begin
                shift_en = 1'b1;
                if (shift_done) begin
                    if (is_write)      state_next = DATA_RX;
                    else if (is_read)  state_next = DUMMY;
                    else               state_next = CMD;
                end
            end
            DUMMY: begin
                // All read commands hold the pads high-Z for the common,
                // fixed dummy budget before the first TX symbol is launched.
                shift_en = 1'b1;
                rx_frame_clks = READ_DUMMY_CLKS;
                if (shift_done) state_next = DATA_TX;
            end
            DATA_RX: begin
                shift_en   = 1'b1;
                data_phase = 1'b1;
            end
            DATA_TX: begin
                shift_en   = 1'b1;
                rx_mode    = 1'b0;
                data_phase = 1'b1;
                spi_pad_oe = ACTIVE_PAD_OE;
            end
            default: state_next = IDLE;
        endcase
    end

    always_ff @(negedge sclk or negedge sys_rst_n or posedge cs_n) begin
        if (!sys_rst_n || cs_n) begin
            state            <= IDLE;
            latched_cmd      <= 8'h00;
            latched_addr     <= 24'h0;
            wr_data_reg      <= 32'h0;
            sys_reg_rd_req   <= 1'b0;
            rd_ready_pending <= 1'b0;
            tx_load_pending  <= 1'b0;
            tx_load_data     <= 32'h0;
        end else begin
            state            <= state_next;
            sys_reg_rd_req   <= 1'b0;
            rd_ready_pending <= 1'b0;
            tx_load_pending  <= 1'b0;

            if ((state == CMD) && shift_done) begin
                latched_cmd <= shift_data_next[7:0];
            end

            // Command/address remain single-lane.  Save the complete 24-bit
            // address alongside the write word so system-side bridges do not
            // need to reconstruct SPI phase information.
            if ((state == ADDR_1) && shift_done) begin
                latched_addr[23:16] <= shift_data_next[7:0];
            end
            if ((state == ADDR_2) && shift_done) begin
                latched_addr[15:8] <= shift_data_next[7:0];
            end
            if ((state == ADDR_3) && shift_done) begin
                latched_addr[7:0] <= shift_data_next[7:0];
                // 0x4C is a distinct register-read request.  The address
                // latch updates on this edge; the request is consumed on the
                // following SCLK rising edge, when the full address is stable.
                if (is_reg_read) sys_reg_rd_req <= 1'b1;
            end

            if ((state == DUMMY) && shift_done && sys_rd_valid) begin
                tx_load_data     <= sys_rd_data;
                tx_load_pending  <= 1'b1;
                rd_ready_pending <= 1'b1;
            end

            if ((state == DATA_RX) && shift_done && sys_wr_ready) begin
                wr_data_reg      <= shift_data_next;
            end

            if ((state == DATA_TX) && tx_done && sys_rd_valid) begin
                tx_load_data     <= sys_rd_data;
                tx_load_pending  <= 1'b1;
                rd_ready_pending <= 1'b1;
            end
        end
    end

endmodule

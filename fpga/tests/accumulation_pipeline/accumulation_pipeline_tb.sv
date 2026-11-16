// Copyright 2026 ETH Zurich
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Authors:
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Connect the accumulation, averaging and readout pipeline for cocotb, with
//   selectable FIFO models.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps

// Registered-read functional FIFO model with independent clocks.
// Define USE_LIBERO_FIFO to exercise the generated CoreFIFO timing.
`ifndef USE_LIBERO_FIFO
module async_sym_fifo #(
    parameter integer FIFO_DATA_WIDTH = 26,
    parameter integer DEPTH = 8,
    localparam integer PTR_WIDTH = $clog2(DEPTH)
) (
    input logic wr_clk_i, wr_en_i,
    input logic [FIFO_DATA_WIDTH-1:0] data_i,
    output wire full_o,
    input logic rd_clk_i, rd_en_i,
    output logic [FIFO_DATA_WIDTH-1:0] data_o,
    output logic data_valid_o,
    output wire empty_o,
    input logic rst_i
);
    logic [FIFO_DATA_WIDTH-1:0] mem[DEPTH];
    logic [PTR_WIDTH:0] wr_ptr_q, rd_ptr_q;
    // Pointer crossings are ideal; use vendor mode to test synchronization.
    assign empty_o = wr_ptr_q == rd_ptr_q;
    assign full_o = (wr_ptr_q[PTR_WIDTH] != rd_ptr_q[PTR_WIDTH]) &&
                    (wr_ptr_q[PTR_WIDTH-1:0] == rd_ptr_q[PTR_WIDTH-1:0]);
    always @(posedge wr_clk_i or posedge rst_i) begin
        if (rst_i)
            wr_ptr_q <= 0;
        else if (wr_en_i && !full_o) begin
            mem[wr_ptr_q[PTR_WIDTH-1:0]] <= data_i;
            wr_ptr_q <= wr_ptr_q + 1'b1;
        end
    end
    always @(posedge rd_clk_i or posedge rst_i) begin
        if (rst_i) begin
            rd_ptr_q <= 0;
            data_o <= 0;
            data_valid_o <= 0;
        end else begin
            data_valid_o <= rd_en_i && !empty_o;
            if (rd_en_i && !empty_o) begin
                data_o <= mem[rd_ptr_q[PTR_WIDTH-1:0]];
                rd_ptr_q <= rd_ptr_q + 1'b1;
            end
        end
    end
endmodule
`endif

module accumulation_pipeline_tb;
    localparam int N_LANES = 2;
    localparam int SAMPLE_WIDTH = 10;
    localparam int SUM_WIDTH = 13;
    localparam int RAW_WIDTH = 2*SAMPLE_WIDTH;
    localparam int SUM_FRAME_WIDTH = 2*SUM_WIDTH;
    localparam int COUNT_WIDTH = 8;
    localparam int SAMPLE_COUNT = 3;

    logic afe_clk, core_clk, rst_n, sequence_reset;
    logic result_rst_n;
    logic fifo_reset, first_shot, start_capture, enable_average;
    logic [COUNT_WIDTH-1:0] shot_count;
    logic [N_LANES*RAW_WIDTH-1:0] raw_data;
    logic [N_LANES-1:0] capture_write;
    logic accumulation_done;
    logic accumulation_accept;
    logic [N_LANES-1:0] accumulation_full, accumulation_empty;
    logic [N_LANES-1:0] accumulation_read, accumulation_dvld;
    logic [N_LANES*SUM_FRAME_WIDTH-1:0] accumulation_data;
    logic [N_LANES-1:0] average_full, average_empty;
    logic [N_LANES-1:0] average_write, average_read;
    logic [N_LANES*RAW_WIDTH-1:0] average_write_data;
    logic [N_LANES*RAW_WIDTH-1:0] average_read_data;
    logic use_stream_reader, stream_start, stream_busy, frame_done;
    logic [N_LANES-1:0] stream_read;
    logic [7:0] stream_data;
    logic stream_valid, stream_ready;

    // The direct read port is retained for focused accumulator/divider tests.
    // In stream mode the production reader owns the result-FIFO read strobes.
    wire [N_LANES-1:0] average_read_mux =
        use_stream_reader ? stream_read : average_read;

    assign result_rst_n = rst_n && !sequence_reset;

    accumulation #(
        .N_FIFOS(N_LANES),
        .SAMPLE_WIDTH(SAMPLE_WIDTH),
        .SUM_WIDTH(SUM_WIDTH),
        .WRITE_CNT_WIDTH(COUNT_WIDTH),
        .RAW_QUEUE_DEPTH(4)
    ) accumulator (
        .rst_state_ni(rst_n),
        .rst_fifos_i({N_LANES{fifo_reset}}),
        .write_cnt_i(COUNT_WIDTH'(SAMPLE_COUNT)),
        .wr_fifo_done_o(accumulation_done),
        .wr_accept_o(accumulation_accept),
        .data_i(raw_data),
        .first_shot_i(first_shot),
        .start_capture_i(start_capture),
        .wr_clk_i(afe_clk),
        .wr_en_i(capture_write),
        .full_o(accumulation_full),
        .rd_clk_i(afe_clk),
        .rd_en_i(accumulation_read),
        .data_o(accumulation_data),
        .data_valid_o(accumulation_dvld),
        .empty_o(accumulation_empty)
    );

    result_average_engine #(
        .N_LANES(N_LANES),
        .SAMPLE_WIDTH(SAMPLE_WIDTH),
        .SUM_WIDTH(SUM_WIDTH),
        .COUNT_WIDTH(COUNT_WIDTH)
    ) average_engine (
        .clk_i(afe_clk),
        .rst_ni(result_rst_n),
        .enable_i(enable_average),
        .frame_done_o(frame_done),
        .accumulation_count_i(shot_count),
        .samples_per_lane_i(12'(SAMPLE_COUNT)),
        .lanes_enable_i({N_LANES{1'b1}}),
        .sum_empty_i(accumulation_empty),
        .sum_data_valid_i(accumulation_dvld),
        .sum_data_i(accumulation_data),
        .sum_read_o(accumulation_read),
        .average_full_i(average_full),
        .average_write_o(average_write),
        .average_data_o(average_write_data)
    );

    genvar lane;
    generate
        for (lane = 0; lane < N_LANES; lane++) begin : cdc_buffers
            async_sym_fifo #(.FIFO_DATA_WIDTH(RAW_WIDTH)) cdc (
                .rst_i(!result_rst_n),
                .wr_clk_i(afe_clk),
                .wr_en_i(average_write[lane]),
                .data_i(average_write_data[lane*RAW_WIDTH +: RAW_WIDTH]),
                .full_o(average_full[lane]),
                .rd_clk_i(core_clk),
                .rd_en_i(average_read_mux[lane]),
                .data_o(average_read_data[lane*RAW_WIDTH +: RAW_WIDTH]),
                .data_valid_o(),
                .empty_o(average_empty[lane])
            );
        end
    endgenerate

    multi_fifo_reader #(
        .N_FIFOS(N_LANES),
        .IN_DATA_WIDTH(RAW_WIDTH),
        .OUT_DATA_WIDTH(8),
        .READ_CNT_WIDTH(COUNT_WIDTH)
    ) stream_reader (
        .clk_i(core_clk),
        .rst_ni(result_rst_n),
        .start_i(stream_start),
        .read_cnt_i(COUNT_WIDTH'(SAMPLE_COUNT)),
        .busy_o(stream_busy),
        .fifos_en_i({N_LANES{1'b1}}),
        .fifos_empty_i(average_empty),
        .fifos_data_i(average_read_data),
        .fifos_read_req_o(stream_read),
        .data_o(stream_data),
        .valid_o(stream_valid),
        .ready_i(stream_ready),
        .debug_word_load_o(),
        .debug_word_data_o()
    );

    initial begin
        afe_clk         = 1'b0;
        core_clk        = 1'b0;
        rst_n           = 1'b0;
        sequence_reset  = 1'b0;
        fifo_reset      = 1'b1;
        first_shot      = 1'b0;
        start_capture   = 1'b0;
        enable_average  = 1'b0;
        shot_count      = '0;
        raw_data        = '0;
        capture_write   = '0;
        average_read    = '0;
        use_stream_reader = 1'b0;
        stream_start    = 1'b0;
        stream_ready    = 1'b0;
        $dumpfile("accumulation_pipeline.vcd");
        $dumpvars(0, accumulation_pipeline_tb);
    end
endmodule

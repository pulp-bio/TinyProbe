// Copyright 2026 LisaMaria Odermatt
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
// -----------------------------------------------------------------------------
// Description:
//   Connect the asynchronous two-entry buffer and byte reshaper for cocotb.
// -----------------------------------------------------------------------------

`timescale 1ns/1ps

module cdc_reshaper_pipeline_tb;
    localparam int DATA_WIDTH = 20;
    localparam int COUNT_WIDTH = 8;

    logic afe_clk, core_clk, rst_n;
    logic write_enable;
    logic [DATA_WIDTH-1:0] write_data;
    logic full, empty;
    logic [DATA_WIDTH-1:0] read_data;
    logic read_request;
    logic [COUNT_WIDTH-1:0] read_count;
    logic start, busy;
    logic [7:0] data;
    logic valid, ready;

    async_two_entry_buffer #(.DATA_WIDTH(DATA_WIDTH)) cdc (
        .rst_ni    (rst_n),
        .wr_clk_i (afe_clk),
        .wr_en_i  (write_enable),
        .wr_data_i(write_data),
        .full_o   (full),
        .rd_clk_i (core_clk),
        .rd_en_i  (read_request),
        .rd_data_o(read_data),
        .empty_o  (empty)
    );

    fifo_h2l_reshaper #(
        .INPUT_DATA_WIDTH (DATA_WIDTH),
        .OUTPUT_DATA_WIDTH(8),
        .READ_CNT_WIDTH   (COUNT_WIDTH)
    ) reshaper (
        .clk_i          (core_clk),
        .rst_ni         (rst_n),
        .read_cnt_i     (read_count),
        .fifo_empty_i   (empty),
        .fifo_data_i    (read_data),
        .fifo_read_req_o(read_request),
        .fifo_rst_o     (),
        .data_o         (data),
        .valid_o        (valid),
        .ready_i        (ready),
        .debug_word_load_o(),
        .debug_word_data_o(),
        .start_i        (start),
        .continue_i     (1'b0),
        .busy_o         (busy)
    );

    initial begin
        afe_clk = 1'b0;
        core_clk = 1'b0;
        rst_n = 1'b0;
        write_enable = 1'b0;
        write_data = '0;
        read_count = '0;
        start = 1'b0;
        ready = 1'b0;
        $dumpfile("cdc_reshaper_pipeline.vcd");
        $dumpvars(0, cdc_reshaper_pipeline_tb);
    end
endmodule

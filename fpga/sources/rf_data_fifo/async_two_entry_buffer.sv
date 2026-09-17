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
//   Buffer two data words across independent write and read clocks.
//
// Parameters:
//   DATA_WIDTH - Stored word width.
//
// Ports:
//   rst_ni - Active-low reset.
//   wr_clk_i - FIFO write clock.
//   wr_en_i - Write enable.
//   wr_data_i - FIFO write data.
//   full_o - FIFO full flag.
//   rd_clk_i - FIFO read clock.
//   rd_en_i - Read enable.
//   rd_data_o - FIFO read data.
//   empty_o - FIFO empty flag.
// -----------------------------------------------------------------------------

// Two-entry asynchronous FIFO implemented entirely with registers. The Gray
// pointers transfer ownership between clock domains; each data word remains
// stable until the synchronized read pointer releases its entry.
module async_two_entry_buffer #(
    parameter int unsigned DATA_WIDTH = 20
) (
    input  logic                  rst_ni,
    input  logic                  wr_clk_i,
    input  logic                  wr_en_i,
    input  logic [DATA_WIDTH-1:0] wr_data_i,
    output logic                  full_o,
    input  logic                  rd_clk_i,
    input  logic                  rd_en_i,
    output logic [DATA_WIDTH-1:0] rd_data_o,
    output logic                  empty_o
);
    logic [DATA_WIDTH-1:0] storage_q [0:1]
        /* synthesis syn_ramstyle="registers" */;

    // Two pointer bits: bit 0 selects an entry and bit 1 distinguishes wrap.
    logic [1:0] wr_bin_q, wr_gray_q;
    logic [1:0] rd_bin_q, rd_gray_q;
    logic [1:0] wr_bin_next, wr_gray_next;
    logic [1:0] rd_bin_next, rd_gray_next;
    (* async_reg = "true" *) logic [1:0] rd_gray_wr_q1, rd_gray_wr_q2;
    (* async_reg = "true" *) logic [1:0] wr_gray_rd_q1, wr_gray_rd_q2;

    logic write_fire, read_fire;

    assign write_fire = wr_en_i && !full_o;
    assign read_fire  = rd_en_i && !empty_o;

    assign wr_bin_next  = wr_bin_q + write_fire;
    assign wr_gray_next = (wr_bin_next >> 1) ^ wr_bin_next;
    assign rd_bin_next  = rd_bin_q + read_fire;
    assign rd_gray_next = (rd_bin_next >> 1) ^ rd_bin_next;

    // For a depth-two FIFO, the current write pointer is full when both Gray
    // pointer bits are inverted relative to the synchronized read pointer.
    assign full_o  = (wr_gray_q == ~rd_gray_wr_q2);
    assign empty_o = (rd_gray_q == wr_gray_rd_q2);

    always_ff @(posedge wr_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wr_bin_q      <= '0;
            wr_gray_q     <= '0;
            rd_gray_wr_q1 <= '0;
            rd_gray_wr_q2 <= '0;
            storage_q[0]  <= '0;
            storage_q[1]  <= '0;
        end else begin
            rd_gray_wr_q1 <= rd_gray_q;
            rd_gray_wr_q2 <= rd_gray_wr_q1;
            if (write_fire)
                storage_q[wr_bin_q[0]] <= wr_data_i;
            wr_bin_q  <= wr_bin_next;
            wr_gray_q <= wr_gray_next;
        end
    end

    always_ff @(posedge rd_clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            rd_bin_q      <= '0;
            rd_gray_q     <= '0;
            wr_gray_rd_q1 <= '0;
            wr_gray_rd_q2 <= '0;
            rd_data_o     <= '0;
        end else begin
            wr_gray_rd_q1 <= wr_gray_q;
            wr_gray_rd_q2 <= wr_gray_rd_q1;
            if (read_fire)
                rd_data_o <= storage_q[rd_bin_q[0]];
            rd_bin_q  <= rd_bin_next;
            rd_gray_q <= rd_gray_next;
        end
    end
endmodule

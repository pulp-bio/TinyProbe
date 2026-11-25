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
//   Implement a synchronous circular FIFO with full and empty flags.
//
// Parameters:
//   DATA_WIDTH - Stored word width.
//   DEPTH - FIFO capacity in words.
//
// Ports:
//   clk_i - Module clock.
//   rst_i - Active-high reset.
//   wr_en_i - Write enable.
//   data_i - Input data word.
//   full_o - FIFO full flag.
//   rd_en_i - Read enable.
//   data_o - Output data word.
//   empty_o - FIFO empty flag.
// -----------------------------------------------------------------------------

// Single-clock FIFO used by the circular accumulator. The implementation keeps
// one location unused (ACTIVE_DEPTH=DEPTH-1 in the controller), allowing one
// read and one write per clock without a full-state write ambiguity.
module sync_circular_fifo #(
    parameter int unsigned DATA_WIDTH = 28,
    parameter int unsigned DEPTH      = 2048,
    localparam int unsigned ADDR_WIDTH = $clog2(DEPTH)
) (
    input  logic                  clk_i,
    input  logic                  rst_i,
    input  logic                  wr_en_i,
    input  logic [DATA_WIDTH-1:0] data_i,
    output logic                  full_o,
    input  logic                  rd_en_i,
    output logic [DATA_WIDTH-1:0] data_o,
    output logic                  empty_o
);

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    logic [ADDR_WIDTH-1:0] wr_ptr_q;
    logic [ADDR_WIDTH-1:0] rd_ptr_q;
    logic [ADDR_WIDTH:0]   count_q;

    logic write_fire;
    logic read_fire;

    assign full_o     = (count_q == DEPTH);
    assign empty_o    = (count_q == 0);
    // Do not accept a write while full, even if a read is accepted in the same
    // cycle. In a count-based FIFO, the read and write pointers are equal when
    // full, so allowing both operations could access the same physical RAM
    // address and make the returned value device-mode dependent.
    assign write_fire = wr_en_i && !full_o;
    assign read_fire  = rd_en_i && !empty_o;

    // This assertion checks the addresses used on the current clock edge,
    // before either pointer is incremented. It is simulation-only and does not
    // consume FPGA resources.
    // synthesis translate_off
    always_ff @(posedge clk_i) begin
        if (!rst_i) begin
            assert (!(read_fire && write_fire &&
                      (rd_ptr_q == wr_ptr_q)))
                else $error(
                    "sync_circular_fifo simultaneous read/write address collision at %0d",
                    rd_ptr_q
                );
        end
    end
    // synthesis translate_on

    always_ff @(posedge clk_i or posedge rst_i) begin
        if (rst_i) begin
            wr_ptr_q <= '0;
            rd_ptr_q <= '0;
            count_q  <= '0;
            data_o   <= '0;
        end else begin
            if (write_fire) begin
                mem[wr_ptr_q] <= data_i;
                wr_ptr_q      <= wr_ptr_q + 1'b1;
            end

            if (read_fire) begin
                data_o  <= mem[rd_ptr_q];
                rd_ptr_q <= rd_ptr_q + 1'b1;
            end

            case ({write_fire, read_fire})
                2'b10: count_q <= count_q + 1'b1;
                2'b01: count_q <= count_q - 1'b1;
                default: count_q <= count_q;
            endcase
        end
    end

endmodule

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
//   Soumyo Bhattacharjee
//   LisaMaria Odermatt
// -----------------------------------------------------------------------------
// Description:
//   Wrap the generated 32-bit asynchronous stream FIFO and its read-valid
//   interface.
//
// Ports:
//   rst_ni - Active-low reset.
//   wr_clk_i - FIFO write clock.
//   wr_en_i - Write enable.
//   wr_data_i - FIFO write data.
//   wr_full_o - FIFO full flag.
//   rd_clk_i - FIFO read clock.
//   rd_en_i - Read enable.
//   rd_data_o - FIFO read data.
//   rd_valid_o - Read-data valid flag.
//   rd_empty_o - FIFO empty flag.
// -----------------------------------------------------------------------------

// 32-word asynchronous stream FIFO.  This must use the generated 32-bit
// QSPI_STREAM_FIFO wrapper: the existing RF_DATA_FIFO CoreFIFO is generated
// with a fixed 20-bit RAM wrapper and cannot safely be width-overridden.
module tp_stream_corefifo (
    input  logic        rst_ni,
    input  logic        wr_clk_i,
    input  logic        wr_en_i,
    input  logic [31:0] wr_data_i,
    output logic        wr_full_o,
    input  logic        rd_clk_i,
    input  logic        rd_en_i,
    output logic [31:0] rd_data_o,
    output logic        rd_valid_o,
    output logic        rd_empty_o
);
    QSPI_STREAM_FIFO i_stream_corefifo (
        .DATA   (wr_data_i),
        .WCLOCK (wr_clk_i),
        .WE     (wr_en_i),
        .RCLOCK (rd_clk_i),
        .RE     (rd_en_i),
        .RESET  (rst_ni),
        .Q      (rd_data_o),
        .FULL   (wr_full_o),
        .EMPTY  (rd_empty_o),
        .DVLD   (rd_valid_o)
    );
endmodule

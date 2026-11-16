// Copyright 2021-2026 ETH Zurich
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
//   Sergei Vostrikov
//   LisaMaria Odermatt
// -----------------------------------------------------------------------------
// Description:
//   Adapt the generated RF data FIFO to the acquisition write and read
//   interfaces.
//
// Parameters:
//   FIFO_DATA_WIDTH - FIFO word width.
//
// Ports:
//   wr_clk_i - FIFO write clock.
//   wr_en_i - Write enable.
//   data_i - Input data word.
//   full_o - FIFO full flag.
//   rd_clk_i - FIFO read clock.
//   rd_en_i - Read enable.
//   data_o - Output data word.
//   data_valid_o - Read-data valid flag.
//   empty_o - FIFO empty flag.
//   rst_i - Active-high reset.
// -----------------------------------------------------------------------------

// Symmetric async FIFO based on Microsemi CoreFIFO for SmartFusion2
module async_sym_fifo  #(
    parameter integer FIFO_DATA_WIDTH = 26
) (
    // Write interface
    input logic                           wr_clk_i,
    input logic                           wr_en_i,
    input logic [FIFO_DATA_WIDTH - 1:0]   data_i,
    output logic                          full_o,


    // Read interface
    input logic                           rd_clk_i,
    input logic                           rd_en_i,
    output logic [FIFO_DATA_WIDTH - 1:0]  data_o,
    output logic                          data_valid_o,
    output logic                          empty_o,

    // Reset signal
    input logic                           rst_i
);
    RF_DATA_FIFO fifo_microsemi (
        // Generated CoreFIFO RESET_POLARITY is 0 (active low); this wrapper
        // retains the project's active-high FIFO-reset convention.
        .RESET               (~rst_i),

        .DATA                (data_i),
        .WCLOCK              (wr_clk_i),
        // Generated CoreFIFO WE_POLARITY=0 means active high.
        .WE                  (wr_en_i),
        
        .Q                   (data_o),
        .RCLOCK              (rd_clk_i),
        // Generated CoreFIFO RE_POLARITY=0 means active high.
        .RE                  (rd_en_i),
        .DVLD                (data_valid_o),

        .FULL                (full_o),
        .EMPTY               (empty_o)
    );

endmodule

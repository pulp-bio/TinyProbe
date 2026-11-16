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
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Decode configuration-register reads and writes and expose the complete
//   register bank.
//
// Parameters:
//   ADDR_SIZE - Register address width.
//   REG_WIDTH - Configuration-register data width.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   addr_i - Configuration-register address.
//   data_o - Output data word.
//   data_i - Input data word.
//   wr_en_i - Write enable.
//   raw_regs_o - All configuration-register values.
// -----------------------------------------------------------------------------

module mem_mapped_regs # (
    parameter integer ADDR_SIZE      = 4,
    parameter integer REG_WIDTH      = 32
)(
    input  logic                                           clk_i,
    input  logic                                           rst_ni,

    input  logic  [ADDR_SIZE - 1:0]                        addr_i,

    output logic  [REG_WIDTH - 1:0]                        data_o,
    input  logic  [REG_WIDTH - 1:0]                        data_i, 
    input  logic                                           wr_en_i,

    output logic [ 2**ADDR_SIZE - 1:0] [REG_WIDTH - 1:0]   raw_regs_o
);
    localparam NUM_OF_REGS = 2**ADDR_SIZE;

    ///////////////////////////////// Address decoder /////////////////////////////////

    // Enable signals (internal)
    logic [NUM_OF_REGS - 1:0] reg_en;

    always_comb begin
        reg_en = '0;
        for(int j = 0; j < NUM_OF_REGS; j = j + 1) begin
            if (addr_i == j) begin
                reg_en = (1 << j);
            end
        end
    end

    ///////////////////////////////// Config registers default values /////////////////////////////////
    `include "reg_default_values.sv"
    parameter [REG_WIDTH - 1:0] PARAM_ARRAY [NUM_OF_REGS - 1:0] = `DEFAULT_VALS;

    ///////////////////////////////// Config registers /////////////////////////////////

    // output data array (internal)
    logic [NUM_OF_REGS - 1:0] [REG_WIDTH - 1:0] data_out;

    // Raw output data array
    logic [NUM_OF_REGS - 1:0] [REG_WIDTH - 1:0] raw_data_out;

    assign raw_regs_o = raw_data_out;

    // Declare a temporary loop variable
    genvar i;

    // Generate for loop to instantiate registers
    for (i = 0; i < NUM_OF_REGS; i = i + 1) begin

        config_reg #(
            .REG_WIDTH    (REG_WIDTH),
            .DEFAULT_VAL  (PARAM_ARRAY[i])
        ) config_reg_inst(
            .clk_i        (clk_i),
            .rst_ni       (rst_ni),

            .clk_en_i     (reg_en[i]),
            .data_i       (data_i),
            .wr_en_i      (wr_en_i),
            .data_o       (data_out[i]),

            .raw_reg_o    (raw_data_out[i])
        )/* synthesis syn_noprune=1 */;
    end

    ///////////////////////////////// Data out multiplexer /////////////////////////////////

    assign data_o = data_out[addr_i];

endmodule

// Copyright 2021-2024 ETH Zurich
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
// -----------------------------------------------------------------------------
// Description:
//   Store one configuration register with a reset default and registered
//   readback.
//
// Parameters:
//   REG_WIDTH - Configuration-register data width.
//   DEFAULT_VAL - Register reset value.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   clk_en_i - Clock/update enable.
//   data_i - Input data word.
//   data_o - Output data word.
//   wr_en_i - Write enable.
//   raw_reg_o - Registered configuration value.
// -----------------------------------------------------------------------------

module config_reg # (
    parameter REG_WIDTH    = 32,
    parameter DEFAULT_VAL  = 'hffffffff
)(
    input  logic                      clk_i,
    input  logic                      rst_ni,

    input  logic                      clk_en_i,
    input  logic  [REG_WIDTH - 1:0]   data_i,
    output logic  [REG_WIDTH - 1:0]   data_o,
    input  logic                      wr_en_i,

    output logic  [REG_WIDTH - 1:0]   raw_reg_o
);

    logic [REG_WIDTH - 1:0] register_d, register_q;
    logic [REG_WIDTH - 1:0] data_d, data_q;

    assign register_d = data_i;
    assign data_d     = register_q;

    // Output assignments
    assign raw_reg_o = data_q;
    assign data_o    = data_q;

    always @(posedge clk_i, negedge rst_ni) begin

        if (!rst_ni) begin
            register_q       <= DEFAULT_VAL;
            data_q           <= DEFAULT_VAL;
        end else if (clk_en_i) begin
            if(wr_en_i) begin
                register_q <= register_d;
            end
            data_q <= data_d;
        end
    end

endmodule
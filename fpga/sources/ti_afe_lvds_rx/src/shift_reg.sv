// Copyright 2021 ETH Zurich
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
//   Shift serial input bits into a parallel word while enabled.
//
// Parameters:
//   N_BITS - Number of bits in the parallel word.
//
// Ports:
//   d_i - Serial data input.
//   clk_i - Module clock.
//   en_i - Block enable.
//   rst_ni - Active-low reset.
//   d_o - Buffered or shifted data output.
// -----------------------------------------------------------------------------

// LSB first output order
module shift_reg #(
    parameter N_BITS = 10
)(
    input logic d_i,
    input logic clk_i,

    input logic en_i,
    input logic rst_ni,

    output logic [N_BITS-1:0] d_o
);

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (~rst_ni) begin
            d_o <= '0;
        end else begin
            if (en_i) begin
                d_o <= {d_i, d_o[N_BITS-1:1]};
            end
        end
    end

endmodule
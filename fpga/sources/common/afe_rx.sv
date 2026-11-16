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
//   Receive and deserialize the enabled AFE LVDS lanes into parallel frames.
//
// Parameters:
//   N_LANES - Number of data lanes.
//   BITS_PER_FRAME - Serial bits in each parallel frame.
//
// Ports:
//   ser_data_i - Serial AFE data input.
//   bit_clk_i - AFE DDR bit clock.
//   frame_clk_i - AFE frame clock.
//   en_i - Block enable.
//   rst_ni - Active-low reset.
//   data_o - Output data word.
// -----------------------------------------------------------------------------

// AFE IC receiver
module afe_rx #(
    parameter int N_LANES = 16,
    parameter int BITS_PER_FRAME = 20
)(
    input logic [N_LANES - 1:0] ser_data_i,
    input logic bit_clk_i,
    input logic frame_clk_i,

    input logic [N_LANES - 1:0] en_i,
    input logic rst_ni,

    output logic [BITS_PER_FRAME * N_LANES - 1:0] data_o
);

    // Declare a temporary loop variable
    genvar i;

    // Generate for loop to instantiate lvds receiver for each lane
    for (i = 0; i < N_LANES; i = i + 1) begin
        ti_afe_lvds_rx #(
            .BITS_PER_FRAME   (BITS_PER_FRAME)
        ) lvds_rx (
            .ser_data_i       (ser_data_i[i]),
            .bit_clk_i        (bit_clk_i),
            .frame_clk_i      (frame_clk_i),

            .en_i             (en_i[i]),
            .rst_ni           (rst_ni),

            .data_o           (data_o[BITS_PER_FRAME * (i + 1) - 1: BITS_PER_FRAME * i])
        )/* synthesis syn_noprune=1 */;
    end

endmodule
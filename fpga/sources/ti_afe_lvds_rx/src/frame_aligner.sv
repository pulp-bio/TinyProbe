// Copyright 2021-2023 ETH Zurich
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
//   Align a parallel data frame to the frame clock with a configurable bit
//   offset.
//
// Parameters:
//   N_BITS - Number of bits in the parallel word.
//   SKEW - Bit offset applied to frame alignment.
//
// Ports:
//   data_i - Input data word.
//   frame_clk_i - AFE frame clock.
//   en_i - Block enable.
//   rst_ni - Active-low reset.
//   data_o - Output data word.
// -----------------------------------------------------------------------------

// Given the skew, aligns the data, introduces latency of 2 frame_clk_i clock cycles.
module frame_aligner #(
    parameter int N_BITS = 20,  // Bits per frame
    parameter int SKEW = 0
)(
    input logic [N_BITS-1:0]  data_i,
    input logic               frame_clk_i,

    input logic               en_i,
    input logic               rst_ni,

    output logic [N_BITS-1:0] data_o  // aligned data
);

    logic [N_BITS - 1:0] data_q, data_q2, data_q3;
    logic [N_BITS*3 - 1:0] data_total;

    assign data_total = {data_q, data_q2, data_q3};

    always_ff @(posedge frame_clk_i, negedge rst_ni) begin
        if (~rst_ni) begin
            data_q  <= '0;
            data_q2 <= '0;
            data_q3 <= '0;
        end else begin
            if (en_i) begin
                data_q   <= data_i;
                data_q2  <= data_q;
                data_q3  <= data_q2;
            end
        end
    end

    // Assign output
    assign data_o = data_total[N_BITS*2 - 1 - SKEW : N_BITS - SKEW];

endmodule
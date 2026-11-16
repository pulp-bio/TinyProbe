// The following notice covers TinyProbe contributions.
// The original design reference is retained below.
//
// Copyright 2020 ETH Zurich
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
//   Generate a programmable periodic strobe from an input clock.
//
// Parameters:
//   CNT_WIDTH - Timing-counter and divider width.
//
// Ports:
//   clk_i - Module clock.
//   cnt_en_i - Enable the divider counter.
//   div_i - Programmable division count.
//   stb_o - Divider strobe output.
// -----------------------------------------------------------------------------

// Creates strobe signal from the root clock and divider
// Based on https://forum.digilentinc.com/topic/18256-frequency-divider-in-systemverilog/
module integer_divider #(
    parameter integer CNT_WIDTH = 16  // Counter width
)(
	input	logic	                 clk_i,
    input	logic	                 cnt_en_i,
	input	logic [CNT_WIDTH-1:0]	 div_i,
	output	logic	                 stb_o
);

	logic	[CNT_WIDTH-1:0]  cnt_d, cnt_q;

    always_comb begin
        cnt_d = cnt_q - 1;
        if(cnt_q == 0) begin
            cnt_d = div_i - 1;
        end
    end

	always_ff @(posedge clk_i) begin
        if (~cnt_en_i) begin
            cnt_q <= 0;
        end
        else begin
            cnt_q <= cnt_d;
        end
    end

	// Assign output
   	assign	stb_o = (cnt_d == 0);
        
endmodule
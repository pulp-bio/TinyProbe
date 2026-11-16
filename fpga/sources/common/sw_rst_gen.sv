// Copyright 2020-2021 ETH Zurich
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
//   Generate complementary software-reset pulses from a trigger.
//
// Parameters:
//   RESET_LENGTH_CYCLES - Software-reset pulse length in clock cycles.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   trig_in - Trigger input.
//   sw_rst_no - Active-low software-reset output.
//   sw_rst_o - Active-high software-reset output.
//   busy_o - Operation in progress.
// -----------------------------------------------------------------------------

module sw_rst_gen  #(
    parameter integer RESET_LENGTH_CYCLES = 20
) (
    input logic         clk_i,
    input logic         rst_ni,

    // Trigger signal
    input logic         trig_in,
    output logic        sw_rst_no,
    output logic        sw_rst_o,
    output logic        busy_o
);
    // Rising edge detector for input trigger
    logic trig_in_q;
    logic trig_in_ris_edge;

    assign trig_in_ris_edge = !trig_in_q & trig_in;

    always_ff @(posedge clk_i) begin
        trig_in_q  <= trig_in;
    end

    // Counter to control duration of reset
    logic [7:0] cnt_d, cnt_q;
    logic cnt_en_d, cnt_en_q;
    
    logic sw_rst_d, sw_rst_q;

    // Output assignment
    assign busy_o    = cnt_en_q;
    assign sw_rst_o  = sw_rst_q;
    assign sw_rst_no = !sw_rst_q;

    always_comb begin
        sw_rst_d     = sw_rst_q;
        cnt_d        = cnt_q;
        cnt_en_d     = cnt_en_q;

        // Check if trigger was asserted
        if (trig_in_ris_edge && (!cnt_en_q)) begin
            cnt_en_d    = 1'b1;
        end
        
        if (cnt_en_q) begin
            // If enabled count or stop if reached target duration
            if (cnt_q == RESET_LENGTH_CYCLES - 1) begin
                cnt_d       = '0;
                sw_rst_d    = 1'b0;
                cnt_en_d    = 1'b0;
            end else begin
                cnt_d       = cnt_q + 1'b1;
                sw_rst_d    = 1'b1;
                cnt_en_d    = 1'b1;
            end
        end
    end

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            cnt_q      <= '0;
            cnt_en_q   <= 1'b0;
            sw_rst_q   <= 1'b0;
        end else begin
            cnt_q      <= cnt_d;
            cnt_en_q   <= cnt_en_d;
            sw_rst_q   <= sw_rst_d;
        end
    end

endmodule

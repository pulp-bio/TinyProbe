// Copyright 2026 ETH Zurich
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
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Divide unsigned sample magnitudes by shot counts from 1 to 12 using
//   reciprocal multiplication and exact quotient correction.
//
// Parameters:
//   NUMERATOR_WIDTH - Unsigned accumulated-sample magnitude width.
//   DIVISOR_WIDTH - Unsigned shot-count width.
//   QUOTIENT_WIDTH - Unsigned average-result magnitude width.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   start_i - Start request.
//   numerator_i - Unsigned accumulated-sample magnitude.
//   divisor_i - Unsigned shot count.
//   busy_o - Operation in progress.
//   done_o - Operation complete.
//   quotient_o - Unsigned average-result magnitude.
// -----------------------------------------------------------------------------

// Shared sequential unsigned divider for accumulated samples.
//
// Division is implemented as reciprocal multiplication followed by an exact
// correction step. Both multiplications use the same inferred multiplier,
// explicitly requested as a SmartFusion2 DSP/MACC implementation.
module sample_average_divider #(
    parameter int unsigned NUMERATOR_WIDTH = 14,
    parameter int unsigned DIVISOR_WIDTH   = 8,
    parameter int unsigned QUOTIENT_WIDTH  = 10
) (
    input  logic                       clk_i,
    input  logic                       rst_ni,
    input  logic                       start_i,
    input  logic [NUMERATOR_WIDTH-1:0] numerator_i,
    input  logic [DIVISOR_WIDTH-1:0]   divisor_i,
    output logic                       busy_o,
    output logic                       done_o,
    output logic [QUOTIENT_WIDTH-1:0]  quotient_o
);

    // Q16 reciprocals keep the largest positive coefficient (65536) inside
    // one signed 18-bit MACC input. The exact correction phase below removes
    // the possible one-count reciprocal approximation error.
    localparam int unsigned RECIPROCAL_SHIFT = 16;
    localparam int unsigned DSP_WIDTH        = 18;

    typedef enum logic [1:0] {
        DIV_IDLE,
        DIV_ESTIMATE,
        DIV_CORRECT
    } divider_state_t;

    divider_state_t state_q;

    logic [NUMERATOR_WIDTH-1:0] numerator_q;
    logic [DIVISOR_WIDTH-1:0] divisor_q;
    logic [QUOTIENT_WIDTH-1:0] estimate_q;
    logic signed [DSP_WIDTH-1:0] multiplier_a_q;
    logic signed [DSP_WIDTH-1:0] multiplier_b_q;
    logic signed [(2*DSP_WIDTH)-1:0] multiplier_product;

    // Synplify supports syn_multstyle="DSP" for SmartFusion2. Keeping one
    // multiplication expression allows both divider phases to share one MACC.
    assign multiplier_product =
        multiplier_a_q * multiplier_b_q
        /* synthesis syn_multstyle="DSP" */;

    function automatic logic [DSP_WIDTH-1:0] reciprocal(
        input logic [DIVISOR_WIDTH-1:0] divisor
    );
        case (divisor)
            8'd1:  reciprocal = 18'd65536;
            8'd2:  reciprocal = 18'd32768;
            8'd3:  reciprocal = 18'd21846;
            8'd4:  reciprocal = 18'd16384;
            8'd5:  reciprocal = 18'd13108;
            8'd6:  reciprocal = 18'd10923;
            8'd7:  reciprocal = 18'd9363;
            8'd8:  reciprocal = 18'd8192;
            8'd9:  reciprocal = 18'd7282;
            8'd10: reciprocal = 18'd6554;
            8'd11: reciprocal = 18'd5958;
            8'd12: reciprocal = 18'd5462;
            default: reciprocal = '0;
        endcase
    endfunction

    assign busy_o = (state_q != DIV_IDLE);

    always_ff @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            state_q          <= DIV_IDLE;
            numerator_q      <= '0;
            divisor_q        <= '0;
            estimate_q       <= '0;
            multiplier_a_q   <= '0;
            multiplier_b_q   <= '0;
            quotient_o       <= '0;
            done_o           <= 1'b0;
        end else begin
            done_o <= 1'b0;

            case (state_q)
                DIV_IDLE: begin
                    if (start_i) begin
                        numerator_q    <= numerator_i;
                        divisor_q      <= divisor_i;
                        multiplier_a_q <= {{(DSP_WIDTH-NUMERATOR_WIDTH){1'b0}},
                                           numerator_i};
                        multiplier_b_q <= reciprocal(divisor_i);
                        state_q        <= DIV_ESTIMATE;
                    end
                end

                DIV_ESTIMATE: begin
                    estimate_q <=
                        multiplier_product >> RECIPROCAL_SHIFT;
                    multiplier_a_q <=
                        (multiplier_product >> RECIPROCAL_SHIFT);
                    multiplier_b_q <=
                        {{(DSP_WIDTH-DIVISOR_WIDTH){1'b0}}, divisor_q};
                    state_q <= DIV_CORRECT;
                end

                DIV_CORRECT: begin
                    if ($unsigned(multiplier_product) > numerator_q)
                        quotient_o <= estimate_q[QUOTIENT_WIDTH-1:0] - 1'b1;
                    else
                        quotient_o <= estimate_q[QUOTIENT_WIDTH-1:0];
                    done_o <= 1'b1;
                    state_q <= DIV_IDLE;
                end

                default: state_q <= DIV_IDLE;
            endcase
        end
    end

endmodule

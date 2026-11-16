// Copyright 2020-2026 ETH Zurich
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
//   Stretch a capture command for transfer from the transport clock to the
//   slower waveform clock, then rearm for the next command.
//
// Ports:
//   clk_i - Module clock.
//   rst_ni - Active-low reset.
//   trig_in - Trigger input.
//   start_o - Stretched start command.
//   busy_o - Operation in progress.
// -----------------------------------------------------------------------------

module start_gen (
    input logic         clk_i,
    input logic         rst_ni,

    // Trigger in signal
    input logic         trig_in,
    output logic        start_o,
    output logic        busy_o
);

    // Stretch a command across the 60 MHz transport -> 10/20 MHz waveform
    // clock crossing, then return low so the next command has a rising edge.
    // Previously start_q latched high until global reset, preventing rearming.
    logic [5:0] cycles_left_q;
    logic trig_q;
    assign start_o = (cycles_left_q != 0);
    assign busy_o = start_o;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            cycles_left_q <= '0;
            trig_q <= 1'b0;
        end else begin
            trig_q <= trig_in;
            if (cycles_left_q != 0)
                cycles_left_q <= cycles_left_q - 1'b1;
            else if (trig_in && !trig_q)
                cycles_left_q <= 6'd32;
        end
    end

endmodule

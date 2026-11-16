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
//   Convert a differential input pair into a single logic signal.
//
// Ports:
//   pad_i - Positive differential input.
//   pad_ni - Negative differential input.
//   d_o - Buffered or shifted data output.
// -----------------------------------------------------------------------------

// Differential input buffer

`define IGNORE_VERILOG_BLACKBOX_GUTS

module ibuf_diff (
    input logic pad_i,
    input logic pad_ni,

    output logic d_o
);

// For Microsemi SmartFusion2

    INBUF_DIFF input_diff_buf (
        .PADP     (pad_i),
        .PADN     (pad_ni), 
        .Y        (d_o)
    );

endmodule

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
//   Capture a serial input on both clock edges using the IGLOO2 DDR input
//   primitive.
//
// Ports:
//   d_i - Serial data input.
//   clk_i - Module clock.
//   clk_en_i - Clock/update enable.
//   qr_o - Rising-edge sample.
//   qf_o - Falling-edge sample.
// -----------------------------------------------------------------------------

// DDR reg of Microsemi Smart Fusion 2 FPGA

module ddr_reg_wrapper(
    input logic d_i,
    input logic clk_i,
    input logic clk_en_i,

    output logic qr_o,
    output logic qf_o
);

    DDR_IN ddr_reg (
        .D       (d_i),
        .CLK     (clk_i),
        .EN      (clk_en_i),
        .ALn     (1'b1),
        .ADn     (1'b1),
        .SLn     (1'b1),
        .SD      (1'b0),
        .QR      (qr_o),
        .QF      (qf_o)
    );

endmodule
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
//   Deserialize one AFE LVDS lane on both bit-clock edges and align it to the
//   frame clock.
//
// Parameters:
//   BITS_PER_FRAME - Serial bits in each parallel frame.
//   FRAME_SKEW - Bit offset passed to the frame aligner.
//
// Ports:
//   ser_data_i - Serial AFE data input.
//   bit_clk_i - AFE DDR bit clock.
//   frame_clk_i - AFE frame clock.
//   en_i - Block enable.
//   rst_ni - Active-low reset.
//   data_o - Output data word.
// -----------------------------------------------------------------------------

module ti_afe_lvds_rx #(
    parameter int BITS_PER_FRAME = 20,
    parameter int FRAME_SKEW = 0
)(
    input logic ser_data_i,
    input logic bit_clk_i,
    input logic frame_clk_i,

    input logic en_i,
    input logic rst_ni,

    output logic [BITS_PER_FRAME-1:0] data_o
);

    logic qr, qf;
    logic [BITS_PER_FRAME/2 - 1:0] reg_r_data, reg_f_data;
    logic [BITS_PER_FRAME - 1:0] shift_regs_data;


    ddr_reg_wrapper ddr_reg (
        .d_i       (ser_data_i),
        .clk_i     (bit_clk_i),
        .clk_en_i  (en_i),
        .qr_o      (qr),
        .qf_o      (qf)
    );

    shift_reg # (
        .N_BITS   ((BITS_PER_FRAME/2))
    ) reg_rising (
        .d_i      (qr),
        .clk_i    (bit_clk_i),
        .en_i     (en_i),
        .rst_ni   (rst_ni),
        .d_o      (reg_r_data)
    );

    shift_reg # (
        .N_BITS   ((BITS_PER_FRAME/2))
    ) reg_falling (
        .d_i      (qf),
        .clk_i    (bit_clk_i),
        .en_i     (en_i),
        .rst_ni   (rst_ni),
        .d_o      (reg_f_data)
    );

    // Assign shift reg output vector (assuming LSB first)
    genvar i;
    generate
        for (i = 0; i < BITS_PER_FRAME/2; i = i + 1) begin
            // Even bits
            assign shift_regs_data[2*i + 1] = reg_r_data[i];
            // Odd bits
            assign shift_regs_data[2*i] = reg_f_data[i];
        end
    endgenerate

    frame_aligner # (
        .N_BITS        (BITS_PER_FRAME),
        .SKEW          (FRAME_SKEW)
    ) frame_aligner_inst (
        .data_i        (shift_regs_data),
        .frame_clk_i   (frame_clk_i),
        .en_i          (en_i),
        .rst_ni        (rst_ni),
        .data_o        (data_o)
    );

endmodule
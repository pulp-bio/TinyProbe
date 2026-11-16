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
//   Soumyo Bhattacharjee
//   Sergei Vostrikov
//   LisaMaria Odermatt
// -----------------------------------------------------------------------------
// Description:
//   Route MCU SPI traffic to the FPGA slave or to the AFE and transmitter
//   configuration interfaces.
//
// Ports:
//   spi_clk_i - SPI serial clock.
//   spi_io0_i - SPI pad input.
//   spi_io1_i - SPI pad input.
//   spi_cs_i - Active-low SPI chip select.
//   spi_ext_int_sel_i - Select internal FPGA or external peripheral SPI
//     routing.
//   spi_ext_cs_sel_i - Select the external AFE or transmitter chip select.
//   spi_clk_int_o - Clock to the internal SPI slave.
//   spi_io0_int_o - Pad data to the internal SPI slave.
//   spi_io1_int_o - Pad data to the internal SPI slave.
//   spi_io0_int_i - Response data from the internal SPI slave.
//   spi_io1_int_i - Response data from the internal SPI slave.
//   spi_pad_oe_int_i - Internal slave pad output enables.
//   spi_cs_int_no - Active-low internal slave chip select.
//   spi_io0_o - SPI pad output data.
//   spi_io1_o - SPI pad output data.
//   spi_pad_oe_o - SPI pad output enables.
//   spi_clk_ext_o - Clock to the external configuration interfaces.
//   spi_mosi_ext_o - Serial configuration data to external peripherals.
//   spi_miso_ext_i - Serial response from external peripherals.
//   spi_cs_tx_no - Active-low transmitter configuration chip select.
//   spi_cs_afe_no - Active-low AFE configuration chip select.
// -----------------------------------------------------------------------------

// Routes the MCU SPI pads either to the internal dual-SPI transport or to the
// existing external AFE/TX SPI bus.  IO0 is master-to-slave when external
// devices are selected; IO1 returns their MISO data to the MCU.
module spi_demux (
    input  logic spi_clk_i,
    input  logic spi_io0_i,
    input  logic spi_io1_i,
    input  logic spi_cs_i,
    input  logic spi_ext_int_sel_i,
    input  logic spi_ext_cs_sel_i,
    output logic spi_clk_int_o,
    output logic spi_io0_int_o,
    output logic spi_io1_int_o,
    input  logic spi_io0_int_i,
    input  logic spi_io1_int_i,
    input  logic [1:0] spi_pad_oe_int_i,
    output logic spi_cs_int_no,
    output logic spi_io0_o,
    output logic spi_io1_o,
    output logic [1:0] spi_pad_oe_o,
    output logic spi_clk_ext_o,
    output logic spi_mosi_ext_o,
    input  logic spi_miso_ext_i,
    output logic spi_cs_tx_no,
    output logic spi_cs_afe_no
);
    logic spi_cs_ext;
    always_comb begin
        spi_clk_int_o = 1'b0;
        spi_io0_int_o = 1'b0;
        spi_io1_int_o = 1'b0;
        spi_cs_int_no = 1'b1;
        spi_clk_ext_o = 1'b0;
        spi_mosi_ext_o = 1'b0;
        spi_cs_ext = 1'b1;
        spi_io0_o = 1'b0;
        spi_io1_o = 1'b0;
        spi_pad_oe_o = 2'b00;
        if (spi_ext_int_sel_i) begin
            spi_clk_ext_o = spi_clk_i;
            spi_mosi_ext_o = spi_io0_i;
            spi_cs_ext = spi_cs_i;
            spi_io1_o = spi_miso_ext_i;
            spi_pad_oe_o[1] = 1'b1;
        end else begin
            spi_clk_int_o = spi_clk_i;
            spi_io0_int_o = spi_io0_i;
            spi_io1_int_o = spi_io1_i;
            spi_cs_int_no = spi_cs_i;
            spi_io0_o = spi_io0_int_i;
            spi_io1_o = spi_io1_int_i;
            spi_pad_oe_o = spi_pad_oe_int_i;
        end
    end
    always_comb begin
        spi_cs_tx_no = 1'b1;
        spi_cs_afe_no = 1'b1;
        if (spi_ext_cs_sel_i) spi_cs_tx_no = spi_cs_ext;
        else spi_cs_afe_no = spi_cs_ext;
    end
endmodule

// Copyright 2025-2026 ETH Zurich
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
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Combine SPI command decoding, transfer control and serial-word shifting.
//
// Parameters:
//   ENABLE_DUAL - Enable dual-lane payload transfers.
//
// Ports:
//   spi_sclk - SPI serial clock.
//   spi_cs_n - Active-low SPI chip select.
//   spi_sdi0 - SPI lane input data.
//   spi_sdi1 - SPI lane input data.
//   spi_sdi2 - SPI lane input data.
//   spi_sdi3 - SPI lane input data.
//   spi_sdo0 - SPI lane output data.
//   spi_sdo1 - SPI lane output data.
//   spi_sdo2 - SPI lane output data.
//   spi_sdo3 - SPI lane output data.
//   spi_pad_oe - SPI pad output enables.
//   sys_clk - Module clock.
//   sys_rst_n - Active-low reset.
//   wr_data - Received register-write data.
//   wr_valid - Register-write payload valid.
//   wr_begin - Predictive start of the register-write payload phase.
//   wr_begin_addr - Address associated with the write-start diagnostic.
//   wr_data_active - Register-write payload phase diagnostic.
//   wr_ready - Register-write receiver ready.
//   wr_addr - Captured register address.
//   reg_rd_req - Register-read request.
//   rd_data - Register or stream read data.
//   rd_valid - Read-data valid.
//   rd_ready - Read-data consumer ready.
//   stream_word_complete_toggle - Toggle on completion of a transmitted
//     stream word.
//   latched_cmd - Captured SPI command byte.
// -----------------------------------------------------------------------------

/**
QUAD SPI Slave - Top Level

//TODO : Uses sys_rst_n directly for async reset need to move to synchronized reset
**/

module spi_quad_slave #(
    parameter bit ENABLE_DUAL = 1'b0
) (
    input  logic        spi_sclk,
    input  logic        spi_cs_n,
    input  logic        spi_sdi0, spi_sdi1, spi_sdi2, spi_sdi3,
    output logic        spi_sdo0, spi_sdo1, spi_sdo2, spi_sdo3,
    output logic [3:0]  spi_pad_oe,
    
    input  logic        sys_clk,
    input  logic        sys_rst_n,
    
    output logic [31:0] wr_data,
    output logic        wr_valid,
    output logic        wr_begin,
    output logic [23:0] wr_begin_addr,
    output logic        wr_data_active,
    input  logic        wr_ready,
    output logic [23:0] wr_addr,
    output logic        reg_rd_req,
    
    input  logic [31:0] rd_data,
    input  logic        rd_valid,
    output logic        rd_ready,
    output logic        stream_word_complete_toggle,

    output logic [7:0]  latched_cmd
);

    logic shift_en, rx_mode, data_phase;
    logic [5:0] rx_frame_clks;
    logic [31:0] shift_data_next, load_data;
    logic shift_done, tx_done, load_en;
    
    spi_quad_shift_reg #(
        .ENABLE_DUAL(ENABLE_DUAL)
    ) i_shift_reg (
        .sclk(spi_sclk), .sys_rst_n(sys_rst_n), .cs_n(spi_cs_n),   
        .rx_mode(rx_mode), .data_phase(data_phase), .shift_en(shift_en),
        .rx_frame_clks(rx_frame_clks),
        .sdi0(spi_sdi0), .sdi1(spi_sdi1), .sdi2(spi_sdi2), .sdi3(spi_sdi3),
        .sdo0(spi_sdo0), .sdo1(spi_sdo1), .sdo2(spi_sdo2), .sdo3(spi_sdo3),
        .shift_data_next(shift_data_next), .shift_done(shift_done),
        .load_data(load_data), .load_en(load_en), .tx_done(tx_done)
    );
    
    spi_quad_controller #(
        .ENABLE_DUAL(ENABLE_DUAL)
    ) i_controller (
        .sclk(spi_sclk), .sys_rst_n(sys_rst_n), .cs_n(spi_cs_n),
        .shift_en(shift_en), .rx_mode(rx_mode), .data_phase(data_phase),
        .rx_frame_clks(rx_frame_clks),
        .shift_data_next(shift_data_next), .shift_done(shift_done), .tx_done(tx_done),
        .load_en(load_en), .load_data(load_data),
        .sys_wr_data(wr_data), .sys_wr_valid(wr_valid),
        .sys_wr_begin(wr_begin), .sys_wr_begin_addr(wr_begin_addr),
        .sys_wr_data_active(wr_data_active),
        .sys_wr_ready(wr_ready),
        .latched_addr(wr_addr),
        .sys_reg_rd_req(reg_rd_req),
        .sys_rd_data(rd_data), .sys_rd_valid(rd_valid), .sys_rd_ready(rd_ready),
        .stream_word_complete_toggle(stream_word_complete_toggle),
        .spi_pad_oe(spi_pad_oe), .latched_cmd(latched_cmd)
    );

endmodule

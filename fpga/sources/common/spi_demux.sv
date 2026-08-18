// Author: Soumyo Bhattacharjee
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

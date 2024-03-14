module spi_demux (
    // SPI Master input signals
    input  logic  spi_clk_i,
    input  logic  spi_mosi_i,
    output logic  spi_miso_o,
    input  logic  spi_cs_i,

    // Control inputs for mux/demux
    input logic  spi_ext_int_sel_i,
    input logic  spi_ext_cs_sel_i,

    // SPI internal signals
    // (For internal FPGA SPI module)
    output logic  spi_clk_int_o,
    output logic  spi_mosi_int_o,
    input  logic  spi_miso_int_i,
    output logic  spi_cs_int_no,

    // SPI external signals
    output logic  spi_clk_ext_o,
    output logic  spi_mosi_ext_o,
    input  logic  spi_miso_ext_i,
    output logic  spi_cs_tx_no,
    output logic  spi_cs_afe_no
);

    logic spi_cs_ext;
    
    // Demux for SPI signals (External (AFE or TX) and internal (SPI sensorbridge))
    always_comb begin
        // If external SPI slave is selected
        if (spi_ext_int_sel_i) begin
            // Set the outputs for internal SPI to default
            spi_clk_int_o   = 1'b0;
            spi_mosi_int_o  = 1'b0;
            spi_cs_int_no   = 1'b1;

            // Connect shared signals of external SPI 
            // To SPI master input
            spi_clk_ext_o  = spi_clk_i;
            spi_mosi_ext_o = spi_mosi_i;
            spi_cs_ext     = spi_cs_i;
            spi_miso_o     = spi_miso_ext_i;

        // If internal SPI slave is selected
        end else begin

            // Set the outputs for external SPI to default
            spi_clk_ext_o   = 1'b0;
            spi_mosi_ext_o  = 1'b0;
            spi_cs_ext      = 1'b1;

            // Connect signals of the internal SPI 
            // To SPI master input
            spi_clk_int_o  = spi_clk_i;
            spi_mosi_int_o = spi_mosi_i;
            spi_cs_int_no  = spi_cs_i;   
            spi_miso_o     = spi_miso_int_i;
        end
    end

    always_comb begin
        spi_cs_tx_no  = 1'b1;
        spi_cs_afe_no = 1'b1;

        // Check whicn external slave is selected
        if (spi_ext_cs_sel_i) begin
            spi_cs_tx_no  = spi_cs_ext;
        end else begin
            spi_cs_afe_no = spi_cs_ext;
        end
    end

endmodule
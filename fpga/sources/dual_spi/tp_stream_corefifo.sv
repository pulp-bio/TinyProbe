// Author: Soumyo Bhattacharjee
// 32-word asynchronous stream FIFO.  This must use the generated 32-bit
// QSPI_STREAM_FIFO wrapper: the existing RF_DATA_FIFO CoreFIFO is generated
// with a fixed 20-bit RAM wrapper and cannot safely be width-overridden.
module tp_stream_corefifo (
    input  logic        rst_ni,
    input  logic        wr_clk_i,
    input  logic        wr_en_i,
    input  logic [31:0] wr_data_i,
    output logic        wr_full_o,
    input  logic        rd_clk_i,
    input  logic        rd_en_i,
    output logic [31:0] rd_data_o,
    output logic        rd_valid_o,
    output logic        rd_empty_o
);
    QSPI_STREAM_FIFO i_stream_corefifo (
        .DATA   (wr_data_i),
        .WCLOCK (wr_clk_i),
        .WE     (wr_en_i),
        .RCLOCK (rd_clk_i),
        .RE     (rd_en_i),
        .RESET  (rst_ni),
        .Q      (rd_data_o),
        .FULL   (wr_full_o),
        .EMPTY  (rd_empty_o),
        .DVLD   (rd_valid_o)
    );
endmodule

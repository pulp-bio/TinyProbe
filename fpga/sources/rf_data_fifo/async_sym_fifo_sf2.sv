// Symmetric async FIFO based on Microsemi CoreFIFO for SmartFusion2
module async_sym_fifo  #(
    parameter integer FIFO_DATA_WIDTH = 40
) (
    // Write interface
    input logic                           wr_clk_i,
    input logic                           wr_en_i,
    input logic [FIFO_DATA_WIDTH - 1:0]   data_i,
    output logic                          full_o,


    // Read interface
    input logic                           rd_clk_i,
    input logic                           rd_en_i,
    output logic [FIFO_DATA_WIDTH - 1:0]  data_o,
    output logic                          empty_o,

    // Reset signal
    input logic                           rst_i
);
    RF_DATA_FIFO fifo_microsemi (
        .RESET               (rst_i),

        .DATA                (data_i),
        .WCLOCK              (wr_clk_i),
        .WE                  (wr_en_i),
        
        .Q                   (data_o),
        .RCLOCK              (rd_clk_i),
        .RE                  (rd_en_i),

        .FULL                (full_o),
        .EMPTY               (empty_o)
    );

endmodule
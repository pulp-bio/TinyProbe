`timescale 1ns/1ps

`ifndef USE_LIBERO_FIFO
module async_sym_fifo #(
    parameter integer FIFO_DATA_WIDTH = 28
) (
    input logic wr_clk_i, wr_en_i,
    input logic [FIFO_DATA_WIDTH-1:0] data_i,
    output logic full_o,
    input logic rd_clk_i, rd_en_i,
    output logic [FIFO_DATA_WIDTH-1:0] data_o,
    output logic data_valid_o, empty_o,
    input logic rst_i
);
    sync_circular_fifo #(.DATA_WIDTH(FIFO_DATA_WIDTH), .DEPTH(4)) mem (
        .clk_i(wr_clk_i), .rst_i(rst_i), .wr_en_i(wr_en_i),
        .data_i(data_i), .full_o(full_o), .rd_en_i(rd_en_i),
        .data_o(data_o), .empty_o(empty_o)
    );
    always_ff @(posedge rd_clk_i) begin
        if (rst_i)
            data_valid_o <= 1'b0;
        else
            data_valid_o <= rd_en_i && !empty_o;
    end
endmodule
`endif

module accumulation_tb;
    localparam int RAW_WIDTH = 20;
    localparam int FIFO_WIDTH = 28;
    logic clk, rst_n, fifo_reset, first_shot, start_capture, wr_en;
    logic [RAW_WIDTH-1:0] data_in;
    logic done, full, rd_en, dvld, empty;
    logic [FIFO_WIDTH-1:0] data_out;

    accumulation #(
        .N_FIFOS(1), .SAMPLE_WIDTH(10), .SUM_WIDTH(14),
        .WRITE_CNT_WIDTH(3), .RAW_QUEUE_DEPTH(4)
    ) dut (
        .rst_state_ni(rst_n), .rst_fifos_i(fifo_reset),
        .write_cnt_i(3), .wr_fifo_done_o(done),
        .data_i(data_in), .first_shot_i(first_shot),
        .start_capture_i(start_capture), .wr_clk_i(clk),
        .wr_en_i(wr_en), .full_o(full), .rd_clk_i(clk),
        .rd_en_i(rd_en), .data_o(data_out),
        .data_valid_o(dvld), .empty_o(empty)
    );

    initial begin
        $dumpfile("accumulation.vcd");
        $dumpvars(0, accumulation_tb);
    end
endmodule

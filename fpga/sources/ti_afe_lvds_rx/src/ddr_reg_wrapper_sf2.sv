// DDR reg of Microsemi Smart Fusion 2 FPGA

module ddr_reg_wrapper(
    input logic d_i,
    input logic clk_i,
    input logic clk_en_i,
    input logic clr_i,

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
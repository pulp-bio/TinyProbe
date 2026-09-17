// Differential input buffer

`define IGNORE_VERILOG_BLACKBOX_GUTS

module ibuf_diff (
    input logic pad_i,
    input logic pad_ni,
    // input logic en_i,

    output logic d_o
);

// For Microsemi SmartFusion2

    INBUF_DIFF input_diff_buf (
        .PADP     (pad_i),
        .PADN     (pad_ni), 
        .Y        (d_o)
    );

    // logic pad_n_int;
    // logic iout_int;
    // logic buf_i;

    // IOPADN_IN padn_in (
    //     .PAD_P      (pad_ni),
    //     .N2POUT_P   (pad_n_int)
    // );

    // IOPADP_IN padp_in (
    //     .PAD_P      (pad_i),
    //     .N2PIN_P    (pad_n_int),
    //     .IOUT_P     (iout_int)
    // );

    // IOINFF_BYPASS ioinff_bypass (
    //     .A    (iout_int),
    //     .Y    (buf_i)
    // );

    // IOIN_IB input_buf (
    //     .YIN    (buf_i),
    //     .E      (en_i),
    //     .Y      (d_o)
    // );

endmodule

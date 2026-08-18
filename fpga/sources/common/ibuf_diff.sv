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

endmodule

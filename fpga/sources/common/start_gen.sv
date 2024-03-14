module start_gen (
    input logic         clk_i,
    input logic         rst_ni,

    // Trigger in signal
    input logic         trig_in,
    output logic        start_o,
    output logic        busy_o
);

    logic start_q, start_d;

    assign start_o = start_q;

    always_comb begin
        busy_o = 1'b0;
        start_d = start_q;
        if (!start_q & trig_in) begin
            start_d = 1'b1;
            busy_o  = 1'b1;
        end
    end

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            start_q      <= 1'b0;
        end else begin
            start_q      <= start_d;
        end
    end

endmodule

module start_gen (
    input logic         clk_i,
    input logic         rst_ni,

    // Trigger in signal
    input logic         trig_in,
    output logic        start_o,
    output logic        busy_o
);

    // Stretch a command across the 60 MHz transport -> 10/20 MHz waveform
    // clock crossing, then return low so the next command has a rising edge.
    // Previously start_q latched high until global reset, preventing rearming.
    logic [5:0] cycles_left_q;
    logic trig_q;
    assign start_o = (cycles_left_q != 0);
    assign busy_o = start_o;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            cycles_left_q <= '0;
            trig_q <= 1'b0;
        end else begin
            trig_q <= trig_in;
            if (cycles_left_q != 0)
                cycles_left_q <= cycles_left_q - 1'b1;
            else if (trig_in && !trig_q)
                cycles_left_q <= 6'd32;
        end
    end

endmodule

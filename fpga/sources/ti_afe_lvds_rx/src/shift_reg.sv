// LSB first output order
module shift_reg #(
    parameter N_BITS = 10
)(
    input logic d_i,
    input logic clk_i,

    input logic en_i,
    input logic rst_ni,

    output logic [N_BITS-1:0] d_o
);

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (~rst_ni) begin
            d_o <= '0;
        end else begin
            if (en_i) begin
                d_o <= {d_i, d_o[N_BITS-1:1]};
            end
        end
    end

endmodule
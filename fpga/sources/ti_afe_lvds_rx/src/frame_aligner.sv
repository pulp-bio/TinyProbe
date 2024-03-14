// Given the skew, aligns the data, introduces latency of 2 frame_clk_i clock cycles.
module frame_aligner #(
    parameter int N_BITS = 20,  // Bits per frame
    parameter int SKEW = 0
)(
    input logic [N_BITS-1:0]  data_i,
    input logic               frame_clk_i,

    input logic               en_i,
    input logic               rst_ni,

    output logic [N_BITS-1:0] data_o  // aligned data
);

    logic [N_BITS - 1:0] data_q, data_q2, data_q3;
    logic [N_BITS*3 - 1:0] data_total;

    assign data_total = {data_q, data_q2, data_q3};

    always_ff @(posedge frame_clk_i, negedge rst_ni) begin
        if (~rst_ni) begin
            data_q  <= '0;
            data_q2 <= '0;
            data_q3 <= '0;
        end else begin
            if (en_i) begin
                data_q   <= data_i;
                data_q2  <= data_q;
                data_q3  <= data_q2;
            end
        end
    end

    // Assign output
    assign data_o = data_total[N_BITS*2 - 1 - SKEW : N_BITS - SKEW];

endmodule
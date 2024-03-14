// AFE5832LP receiver
module afe_rx #(
    parameter int N_LANES = 16,
    parameter int BITS_PER_FRAME = 20,
    parameter int FRAME_SKEW [N_LANES - 1] = {0}
)(
    input logic [N_LANES - 1:0] ser_data_i,
    input logic bit_clk_i,
    input logic frame_clk_i,

    input logic [N_LANES - 1:0] en_i,
    input logic rst_ni,

    output logic [BITS_PER_FRAME * N_LANES - 1:0] data_o
);

    // Declare a temporary loop variable
    genvar i;

    // Generate for loop to instantiate lvds receiver for each lane
    for (i = 0; i < N_LANES; i = i + 1) begin
        ti_afe_lvds_rx #(
            .BITS_PER_FRAME   (BITS_PER_FRAME)
        ) lvds_rx (
            .ser_data_i       (ser_data_i[i]),
            .bit_clk_i        (bit_clk_i),
            .frame_clk_i      (frame_clk_i),

            .en_i             (en_i[i]),
            .rst_ni           (rst_ni),

            .data_o           (data_o[BITS_PER_FRAME * (i + 1) - 1: BITS_PER_FRAME * i])
        )/* synthesis syn_noprune=1 */;
    end

endmodule
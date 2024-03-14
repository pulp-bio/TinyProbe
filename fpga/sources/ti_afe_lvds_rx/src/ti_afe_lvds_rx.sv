module ti_afe_lvds_rx #(
    parameter int BITS_PER_FRAME = 20,
    parameter int FRAME_SKEW = 0
)(
    input logic ser_data_i,
    input logic bit_clk_i,
    input logic frame_clk_i,

    input logic en_i,
    input logic rst_ni,

    output logic [BITS_PER_FRAME-1:0] data_o
);

    logic reg_clr;
    logic qr, qf;
    logic [BITS_PER_FRAME/2 - 1:0] reg_r_data, reg_f_data;
    logic [BITS_PER_FRAME - 1:0] shift_regs_data;

    assign reg_clr = ~rst_ni;

    ddr_reg_wrapper ddr_reg (
        .d_i       (ser_data_i),
        .clk_i     (bit_clk_i),
        .clk_en_i  (en_i),
        .clr_i     (reg_clr),
        .qr_o      (qr),
        .qf_o      (qf)
    );

    shift_reg # (
        .N_BITS   ((BITS_PER_FRAME/2))
    ) reg_rising (
        .d_i      (qr),
        .clk_i    (bit_clk_i),
        .en_i     (en_i),
        .rst_ni   (rst_ni),
        .d_o      (reg_r_data)
    );

    shift_reg # (
        .N_BITS   ((BITS_PER_FRAME/2))
    ) reg_falling (
        .d_i      (qf),
        .clk_i    (bit_clk_i),
        .en_i     (en_i),
        .rst_ni   (rst_ni),
        .d_o      (reg_f_data)
    );

    // Assign shift reg output vector (assuming LSB first)
    genvar i;
    generate
        for (i = 0; i < BITS_PER_FRAME/2; i = i + 1) begin
            // Even bits
            assign shift_regs_data[2*i + 1] = reg_r_data[i];
            // Odd bits
            assign shift_regs_data[2*i] = reg_f_data[i];
        end
    endgenerate

    frame_aligner # (
        .N_BITS        (BITS_PER_FRAME),
        .SKEW          (FRAME_SKEW)
    ) frame_aligner_inst (
        .data_i        (shift_regs_data),
        .frame_clk_i   (frame_clk_i),
        .en_i          (en_i),
        .rst_ni        (rst_ni),
        .data_o        (data_o)
    );

    // // Latch the data by frame clock
    // always_ff @(posedge frame_clk_i, negedge rst_ni) begin
    //     if (~rst_ni) begin
    //         data_o <= '0;
    //     end else begin
    //         if (en_i) begin
    //             data_o <= shift_regs_data;
    //         end
    //     end
    // end

endmodule
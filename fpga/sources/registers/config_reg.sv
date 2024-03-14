module config_reg # (
    parameter REG_WIDTH    = 32,
    parameter DEFAULT_VAL  = 'hffffffff
)(
    input  logic                      clk_i,
    input  logic                      rst_ni,

    input  logic                      clk_en_i,
    input  logic  [REG_WIDTH - 1:0]   data_i,
    output logic  [REG_WIDTH - 1:0]   data_o,
    input  logic                      wr_en_i,

    output logic  [REG_WIDTH - 1:0]   raw_reg_o
);

    logic [REG_WIDTH - 1:0] register_d, register_q;
    logic [REG_WIDTH - 1:0] data_d, data_q;

    assign register_d = data_i;
    assign data_d     = register_q;

    // Output assignments
    assign raw_reg_o = data_q;
    assign data_o    = data_q;

    always @(posedge clk_i, negedge rst_ni) begin

        if (!rst_ni) begin
            register_q       <= DEFAULT_VAL;
            data_q           <= DEFAULT_VAL;
        end else if (clk_en_i) begin
            if(wr_en_i) begin
                register_q <= register_d;
            end
            data_q <= data_d;
        end
    end

endmodule
module mem_mapped_regs # (
    parameter integer ADDR_SIZE      = 4,
    parameter integer REG_WIDTH      = 32
)(
    input  logic                                           clk_i,
    input  logic                                           rst_ni,

    input  logic  [ADDR_SIZE - 1:0]                        addr_i,

    output logic  [REG_WIDTH - 1:0]                        data_o,
    input  logic  [REG_WIDTH - 1:0]                        data_i, 
    input  logic                                           wr_en_i,

    output logic [ 2**ADDR_SIZE - 1:0] [REG_WIDTH - 1:0]   raw_regs_o
);
    localparam NUM_OF_REGS = 2**ADDR_SIZE;

    ///////////////////////////////// Address decoder /////////////////////////////////

    // Enable signals (internal)
    logic [NUM_OF_REGS - 1:0] reg_en;

    always_comb begin
        reg_en = '0;
        for(int j = 0; j < NUM_OF_REGS; j = j + 1) begin
            if (addr_i == j) begin
                reg_en = (1 << j);
            end
        end
    end

    ///////////////////////////////// Config registers default values /////////////////////////////////
    `include "reg_default_values.svh"
    parameter [REG_WIDTH - 1:0] PARAM_ARRAY [NUM_OF_REGS - 1:0] = `DEFAULT_VALS;

    ///////////////////////////////// Config registers /////////////////////////////////

    // output data array (internal)
    logic [NUM_OF_REGS - 1:0] [REG_WIDTH - 1:0] data_out;

    // Raw output data array
    logic [NUM_OF_REGS - 1:0] [REG_WIDTH - 1:0] raw_data_out;

    assign raw_regs_o = raw_data_out;

    // Declare a temporary loop variable
    genvar i;

    // Generate for loop to instantiate registers
    for (i = 0; i < NUM_OF_REGS; i = i + 1) begin

        config_reg #(
            .REG_WIDTH    (REG_WIDTH),
            .DEFAULT_VAL  (PARAM_ARRAY[i])
        ) config_reg_inst(
            .clk_i        (clk_i),
            .rst_ni       (rst_ni),

            .clk_en_i     (reg_en[i]),
            .data_i       (data_i),
            .wr_en_i      (wr_en_i),
            .data_o       (data_out[i]),

            .raw_reg_o    (raw_data_out[i])
        )/* synthesis syn_noprune=1 */;
    end

    ///////////////////////////////// Data out multiplexer /////////////////////////////////

    assign data_o = data_out[addr_i];

endmodule



// module config_regs # (
//     parameter integer RAM_ADDR_SIZE   = 4,
//     parameter integer RAM_WORD_WIDTH  = 32
// )(
//     input  logic                           clk_i,
//     input  logic                           rst_ni,

//     output logic  [RAM_WORD_WIDTH - 1:0]   data_o,
//     input  logic  [RAM_ADDR_SIZE - 1:0]    addr_i,
//     input  logic  [RAM_WORD_WIDTH - 1:0]   data_i, 
//     input  logic                           wr_en_i
// );
//     localparam NUM_OF_REGS = 2**RAM_ADDR_SIZE;

//     logic [NUM_OF_REGS - 1:0] [RAM_WORD_WIDTH - 1:0] memory;

//     always @(posedge clk_i, negedge rst_ni) begin

//         if (!rst_ni) begin
//             for (int i=0; i < NUM_OF_REGS; i++) memory[i] <= '0;
//         end else if (wr_en_i) begin
//             memory[addr_i] <= data_i;
//         end
//         data_o <= memory[addr_i];
//     end

// endmodule
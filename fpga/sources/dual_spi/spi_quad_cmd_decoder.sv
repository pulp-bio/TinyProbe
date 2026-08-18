/**
SPI Command Decoder
- Command opcodes are shared across both dual and quad builds:
  - 0x32 write
  - 0x6B FIFO/stream read
  - 0x4C register readback
**/

module spi_quad_cmd_decoder (
    input  logic [7:0] cmd_i,
    
    output logic       is_write_o,
    output logic       is_read_o,
    output logic       is_reg_read_o,
    output logic       is_invalid_o
);

    logic is_write;
    logic is_read;
    logic is_invalid, is_reg_read;
    logic [7:0] write_cmd;
    logic [7:0] read_cmd;
    
    always_comb begin
        write_cmd = 8'h32;
        read_cmd  = 8'h6B;

        is_write = (cmd_i == write_cmd);
        is_reg_read = (cmd_i == 8'h4C);
        is_read  = (cmd_i == read_cmd) || is_reg_read;
        
        is_invalid = !(is_write || is_read);
    end

    assign is_write_o   = is_write;
    assign is_read_o    = is_read;
    assign is_reg_read_o = is_reg_read;
    assign is_invalid_o = is_invalid;

endmodule


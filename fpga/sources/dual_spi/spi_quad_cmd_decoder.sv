// Copyright 2025-2026 ETH Zurich
// Copyright and related rights are licensed under the Solderpad Hardware
// License, Version 0.51 (the "License"); you may not use this file except in
// compliance with the License. You may obtain a copy of the License at
// http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
// or agreed to in writing, software, hardware and materials distributed under
// this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.
//
// Authors:
//   Soumyo Bhattacharjee
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Classify SPI commands as writes, stream reads or register reads.
//
// Ports:
//   cmd_i - SPI command byte.
//   is_write_o - Command is a write.
//   is_read_o - Command is a stream read.
//   is_reg_read_o - Command is a register read.
// -----------------------------------------------------------------------------

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
    output logic       is_reg_read_o
);

    logic is_write;
    logic is_read;
    logic is_reg_read;
    logic [7:0] write_cmd;
    logic [7:0] read_cmd;
    
    always_comb begin
        write_cmd = 8'h32;
        read_cmd  = 8'h6B;

        is_write = (cmd_i == write_cmd);
        is_reg_read = (cmd_i == 8'h4C);
        is_read  = (cmd_i == read_cmd) || is_reg_read;
        
    end

    assign is_write_o   = is_write;
    assign is_read_o    = is_read;
    assign is_reg_read_o = is_reg_read;

endmodule


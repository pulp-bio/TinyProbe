// Copyright 2021-2026 ETH Zurich
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
//   Sergei Vostrikov
//   LisaMaria Odermatt
//   Federico Villani
// -----------------------------------------------------------------------------
// Description:
//   Define reset values for the sixteen FPGA configuration registers.
// -----------------------------------------------------------------------------

`ifndef CONFIG_REGS_DEF_VALUES_SVH_
`define CONFIG_REGS_DEF_VALUES_SVH_


`define DEFAULT_VALS {/* REG 0  */ 32'h00000000,\
                      /* REG 1  */ 32'h00000000,\
                      /* REG 2  */ 32'h0000ffff,\
                      /* REG 3  */ 32'hC3506420,\
                      /* REG 4  */ 32'h001E01F4,\
                      /* REG 5  */ 32'h00001792,\
                      /* REG 6  */ 32'h00000002,\
                      /* REG 7  */ 32'h0000017C,\
                      /* REG 8  */ 32'h00000008,\
                      /* REG 9  */ 32'h0000001E,\
                      /* REG 10 */ 32'h00000000,\
                      /* REG 11 */ 32'h00000001,\
                      /* REG 12 */ 32'h00000000,\
                      /* REG 13 */ 32'h00000000,\
                      /* REG 14 */ 32'h00000000,\
                      /* REG 15 */ 32'h00000000}

`endif

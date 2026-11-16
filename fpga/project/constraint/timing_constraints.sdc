# Copyright 2021-2026 ETH Zurich
# Copyright and related rights are licensed under the Solderpad Hardware
# License, Version 0.51 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
# or agreed to in writing, software, hardware and materials distributed under
# this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Authors:
#   Soumyo Bhattacharjee
#   Sergei Vostrikov
#   LisaMaria Odermatt
#   Federico Villani
# -----------------------------------------------------------------------------
# Description:
#   Clock and interface timing constraints, including 300 MHz DDR AFE capture
#   at 600 Mbps per lane.
# -----------------------------------------------------------------------------

# AFE: 600 Mbps per lane, DCLK 300 MHz DDR, FCLK 30 MHz (20 bits/frame).
# ADC clock 60 MHz, 10X serialization, 1X lane mode. All times below are ns.
# DCLK period = 1000/300; UI = 1000/600. FCLK period = 20*UI,
# rising edge = 0.75*DCLK period = 2.5, falling edge = 2.5 + period/2.
create_clock -name {afe_bit_clk} -period 3.333333333 -waveform {0 1.666666667} [get_ports {afe_bit_clk_i}]
create_clock -name {afe_frame_clk} -period 33.333333333 -waveform {2.5 19.166666667} [get_ports {afe_frame_clk_i}]
# SPI: maximum 10 MHz; period = 1000/10 = 100 ns, 50% duty cycle.
create_clock -name {spi_clk_i} -period 100 -waveform {50 0 } [ get_ports { spi_clk_i } ]
# PLL clocks
create_clock -ignore_errors -name {crystal_clk_i} -period 62.5 [ get_pins { ext_osc/EXT_OSC_0/I_XTLOSC/CLKOUT } ]
create_generated_clock -name {tx_bf_clk} -multiply_by 75 -divide_by 12 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL0 } ]
create_generated_clock -name {afe_clk} -multiply_by 75 -divide_by 20 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL1 } ]
create_generated_clock -name {core_clk} -multiply_by 75 -divide_by 120 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL2 } ]
# Set output delay constraints
create_generated_clock -name {tx_bf_clk_out} -divide_by 1 -source [ get_pins { tx_chip_clk_obuf/PAD } ] [ get_ports { tx_bf_clk_o } ]
create_generated_clock -name {afe_clk_out} -divide_by 1 -source [ get_pins { afe_clk_obuf/PAD } ] [ get_ports { afe_clk_o } ]
# AFE data at the FPGA pins, matched clock/data routes (TI SBAS922 8.9).
# UI = 1000/600 = 1.666666667; tOSU = tOH = UI/2 - 0.4 = 0.433333333.
# Input min = tOH; input max = UI - tOSU = 1.233333333, on both DDR edges.
# These bounds include the 90-degree centring; do not shift DCLK again.
# Physical per-lane taps are in constraint/io/phys_constr_gen_v2_igloo.pdc.
set_input_delay 0.433333333 -min -clock {afe_bit_clk} [get_ports {afe_data_i[*]}]
set_input_delay 1.233333333 -max -clock {afe_bit_clk} [get_ports {afe_data_i[*]}]
set_input_delay 0.433333333 -min -clock_fall -add_delay -clock {afe_bit_clk} [get_ports {afe_data_i[*]}]
set_input_delay 1.233333333 -max -clock_fall -add_delay -clock {afe_bit_clk} [get_ports {afe_data_i[*]}]
# Setup (max = + tSU)
set_output_delay 4 -max  -clock { spi_clk_i } [ get_ports { spi_io0_io spi_io1_io } ]
# Hold  (min = - tH)
set_output_delay -7.5 -min  -clock { spi_clk_i } [ get_ports { spi_io0_io spi_io1_io } ]
# AFE TGC signals output delays. Setup time = 3 ns, hold time = 2ns. Calculations assume afe_clk = 60 MHz
set_output_delay -2 -min  -clock { afe_clk_out } [ get_ports { tgc_slope_o tgc_up_dn_o } ]
set_output_delay 3 -max  -clock { afe_clk_out } [ get_ports { tgc_slope_o tgc_up_dn_o } ]
# TX Chip TR_BF_SYNC to TR_BF_CLK setup time = 1.27, hold time = 1.57 . Delays below assume 100 Mhz TX_BF_CLK
set_output_delay -1.57 -min  -clock { tx_bf_clk_out } [ get_ports { tx_bf_sync_o } ]
set_output_delay 1.27 -max  -clock { tx_bf_clk_out } [ get_ports { tx_bf_sync_o } ]
# Configure external mode only outside acquisition.
set_false_path -from [get_cells {qspi_transport/i_mem_mapped_regs/genblk1[12].config_reg_inst/data_q[25]}] \
    -to [get_ports {tx_bf_sync_o}]
# Logically exclusive clock groups
set_clock_groups  -asynchronous -group [ get_clocks { crystal_clk_i tx_bf_clk afe_clk core_clk } ] -group [ get_clocks { afe_bit_clk afe_frame_clk } ] -group [ get_clocks { spi_clk_i } ]
set_multicycle_path 2 -setup_only -through [get_nets {spi_pad_oe_qspi*}]  -to [get_ports {spi_io0_io spi_io1_io}]

# FCLK is an AFE output with the same nominal timing as the data.
set_clock_uncertainty -from [get_clocks {afe_bit_clk}] -to [get_clocks {afe_frame_clk}] 0.4

# Author: Soumyo Bhattacharjee
# AFE LVDS clocks (for 30 MHz AFE sampling rate)
create_clock -name {afe_bit_clk} -period 3.33 -waveform {0 1.665 } [ get_ports { afe_bit_clk_i } ]
create_clock -name {afe_frame_clk} -period 33.3 -waveform {2.4975 19.1475 } [ get_ports { afe_frame_clk_i } ]
# SPI clock constraints (for 50 MHz AFE sampling rate)
create_clock -name {spi_clk_i} -period 20 -waveform {10 0 } [ get_ports { spi_clk_i } ]
# PLL clocks
create_clock -ignore_errors -name {crystal_clk_i} -period 62.5 [ get_pins { ext_osc/EXT_OSC_0/I_XTLOSC/CLKOUT } ]
create_generated_clock -name {tx_bf_clk} -multiply_by 75 -divide_by 12 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL0 } ]
create_generated_clock -name {afe_clk} -multiply_by 75 -divide_by 20 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL1 } ]
create_generated_clock -name {core_clk} -multiply_by 75 -divide_by 60 -source [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/XTLOSC } ] -phase 0 [ get_pins { pll_clk_gen/Clock_gen_0/CCC_INST/GL2 } ]
# Set output delay constraints
create_generated_clock -name {tx_bf_clk_out} -divide_by 1 -source [ get_pins { tx_chip_clk_obuf/PAD } ] [ get_ports { tx_bf_clk_o } ]
create_generated_clock -name {afe_clk_out} -divide_by 1 -source [ get_pins { afe_clk_obuf/PAD } ] [ get_ports { afe_clk_o } ]
# Min = external hold (0.43 ns), max  = period - external setup (0.43 ns) (too hard to meet)
set_input_delay 0.65 -min  -clock { afe_bit_clk } [ get_ports { afe_data_i[*] } ]
set_input_delay 0.65 -max  -clock { afe_bit_clk } [ get_ports { afe_data_i[*] } ]
set_input_delay 0.65 -min -clock_fall -add_delay  -clock { afe_bit_clk } [ get_ports { afe_data_i[*] } ]
set_input_delay 0.65 -max -clock_fall -add_delay  -clock { afe_bit_clk } [ get_ports { afe_data_i[*] } ]
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
# Logically exclusive clock groups
set_clock_groups  -asynchronous -group [ get_clocks { crystal_clk_i tx_bf_clk afe_clk core_clk } ] -group [ get_clocks { afe_bit_clk afe_frame_clk } ] -group [ get_clocks { spi_clk_i } ]
set_multicycle_path 2 -setup_only -through [get_nets {spi_pad_oe_qspi*}]  -to [get_ports {spi_io0_io spi_io1_io}]
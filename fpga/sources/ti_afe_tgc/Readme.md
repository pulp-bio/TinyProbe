# Time Gain Compensation (TGC) RTL module for TI AFEs
This project implement hardware RTL module that produces control signals for Texas Instruments AFE5832LP required for Time Gain Compensation.
### Structure of the project
- src - source RTL files
- tests - verification tests
- vivado_test_files - additianal source files and constraints for vivado project

### Short description of the current design
User provides the following inputs:
- clk_i,
- rst_ni
- start_i
- delay_start_i
- capt_time_i
- delay_finish_i

1. Initially, outputs **tgc_slope_o** and **tgc_up_dn_o** are equal to logic 0.

2. User logic asserts signal **start_i**. In one cycle of **clk_i** after this signal was captured by the rising edge, numerical values
- delay_start_i
- capt_time_i
- delay_finish_i
<br />are loaded inside the module.

3. Then, the system waits for **(3 + delay_start_i)** cycles.
4. Afterward, the output **tgc_slope_o** gets connected to the clock signal **clk_i**.  **tgc_up_dn_o** stays low.
5. The system waits for **capt_time_i** cycles
6. **tgc_up_dn_o** gets changed to high.
7. The system waits for **delay_finish_i** cycles
8. Finally, system returns to the state 1.

![Simulation waveform](images/test_waveform.png "Simulation waveform")
 
### Requirements to run tests:
1. Python module cocotb 1.4.0
2. cocotb-spi extension
https://github.com/Martoni/cocotbext-spi

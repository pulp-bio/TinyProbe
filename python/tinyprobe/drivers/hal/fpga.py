from tinyprobe.drivers.hal import TP_HAL
from tinyprobe.drivers.ll.fpga_ll import TP_LL_FPGA
from tinyprobe.protocol.commands import (
    TinyProbeCmdSeq,
    SwitchSpiMux,
    WriteFPGAReg,
)
import numpy as np

# Defaults

FPGA_MAX_LVDS_LANES = 16
SYNC_PER_DEFAULT_US = 5000
FPGA_MAX_FIFO_DEPTH = 2048

REFRESH_CNT_PER_DEF_US = 5000
REFRESH_CNT_TR_ON_DEF_US = 10

TR_SW_WKUP_TIME_DEF_US = 10
TR_SW_SLEEP_TIME_DEF_US = 3.2

AFE_RES_BIT_PER_SAMPLE = 10
AFE_WKUP_TIME_DEF_US = 3
AFE_CLK_ON_TIME_DEF_US = 50

AFE_DATA_ACQ_DEF_US = 100
TGC_DELAY_FINISH_DEF_CYCLES = 2


# FIFO reset precedes the TX trigger
# but the following number of fpga_core_clock cycles
FIFO_RST_ADVANCE_CYCLES = 4 + 1

# FIFO start capture signal
# is delayed (with resp to AFE trig.) by the following
# number of fpga_clock cycles
FIFO_START_CAPT_DELAY_CYCLES = 5 + 2

# Safety margin to make sure all the data is acquired
# by FPGA from the AFE
AFE_ACQ_TIME_MARGIN_CYCLES = 20


# Default clocks
TX_BF_CLK_LOW = 20 * 10**6
TX_BF_CLK_HIGH = 100 * 10**6

AFE_CLK_LOW = 20 * 10**6 / 2
AFE_CLK_HIGH = 60 * 10**6 / 2

FPGA_CORE_CLK_LOW = 10 * 10**6
FPGA_CORE_CLK_HIGH = 20 * 10**6

# Source of control
signal_ctrl_src = {"register": 0, "wave_gen": 1}


class TP_HAL_FPGA(TP_HAL):
    def __init__(self):
        super().__init__("FPGA")

        self._ll = TP_LL_FPGA()

        # Output PLL clocks
        self._tx_bf_clk = TX_BF_CLK_LOW
        self._afe_clk = AFE_CLK_LOW
        self._fpga_core_clk = FPGA_CORE_CLK_LOW

        # Acquistion parameters
        self._meas_period_us = SYNC_PER_DEFAULT_US
        self._n_shots = 1
        self._afe_start_capt_delay_us = 0
        self._data_acq_time_us = AFE_DATA_ACQ_DEF_US

        # Calculated throughput requirements
        # given the meas. settings
        self._throughput_req = 0

    @property
    def tx_bf_clk(self):
        return self._tx_bf_clk

    @property
    def afe_clk(self):
        return self._afe_clk

    @property
    def fpga_core_clk(self):
        return self._fpga_core_clk

    @property
    def meas_period_us(self):
        return self._meas_period_us

    @property
    def n_shots(self):
        return self._n_shots

    def get_cmd_sequence(self, write_all_regs=False, from_history=False):
        if write_all_regs:
            # Get all the registers and their states
            addr_list, val_list = self._ll.get_all_regs_and_vals()
        else:
            # First get the list of regs and vals to write
            addr_list, val_list = self._ll.get_modified_regs_and_vals(
                from_history=from_history
            )

        cmd_seq = TinyProbeCmdSeq([])

        # Add commands to write the registers to a list
        cmd_list = []

        for i in range(len(addr_list)):
            cmd_list.append(WriteFPGAReg(addr_list[i], val_list[i]))

        # Extend the command sequence with the list of new commands
        cmd_seq.extend(cmd_list)

        return cmd_seq

    def _us_to_clk_cycles(self, time_us, clk_freq_Hz):
        return np.ceil(time_us * 10 ** (-6) * clk_freq_Hz)

    ### Functions to configure the FPGA ###

    ## PLL Settings ##

    # Set tx_bf_clock
    def set_tx_bf_clk_mux(self, high_freq=False):
        self._ll.set_pll_ngmux_gl0(state=high_freq)

        if high_freq:
            self._tx_bf_clk = TX_BF_CLK_HIGH
        else:
            self._tx_bf_clk = TX_BF_CLK_LOW
        return

    # Set afe_clock
    def set_afe_clk_mux(self, high_freq=False):
        self._ll.set_pll_ngmux_gl1(state=high_freq)

        if high_freq:
            self._afe_clk = AFE_CLK_HIGH
        else:
            self._afe_clk = AFE_CLK_LOW
        return

    # Set fpga_core_clock
    def set_fpga_core_clk_mux(self, high_freq=False):
        self._ll.set_pll_ngmux_gl2(state=high_freq)

        if high_freq:
            self._fpga_core_clk = FPGA_CORE_CLK_HIGH
        else:
            self._fpga_core_clk = FPGA_CORE_CLK_LOW

        return

    # Set countol source for the tx_bf_clk
    def set_tx_bf_clk_en_ctrl_src(self, ctrl_source="register"):
        if isinstance(ctrl_source, str):
            self._ll.set_pll_gl0_en_mux(wave_gen_ctrl=signal_ctrl_src[ctrl_source])
        else:
            print("Error! ctrl_source is wrong")

    # Set countol source for the afe_clk
    def set_afe_clk_en_ctrl_src(self, ctrl_source="register"):
        if isinstance(ctrl_source, str):
            self._ll.set_pll_gl1_en_mux(wave_gen_ctrl=signal_ctrl_src[ctrl_source])
        else:
            print("Error! ctrl_source is wrong")

    # Power Down Clock
    def pwr_down_clk(self, clock="TX"):
        if clock == "TX":
            self._ll.set_pll_gl0_en_mux(wave_gen_ctrl=False)
            self._ll.pll_gl0_en_reg(en=False)
        elif clock == "AFE":
            self._ll.set_pll_gl1_en_mux(wave_gen_ctrl=False)
            self._ll.pll_gl1_en_reg(en=False)
        else:
            print("Error! The clock name is wrong")

        return

    # Power Up the Clock
    def pwr_up_clk(self, clock="TX"):
        if clock == "TX":
            self._ll.pll_gl0_en_reg(en=True)
            self._ll.set_pll_gl0_en_mux(wave_gen_ctrl=False)
        elif clock == "AFE":
            self._ll.pll_gl1_en_reg(en=True)
            self._ll.set_pll_gl1_en_mux(wave_gen_ctrl=False)
        else:
            print("Error! The clock name is wrong")
        return

    ## Acquisition settings ##

    def set_active_lvds_lanes(self, lvds_lanes_ids=[]):
        # First, disable all the LVDS lanes
        self._ll.disable_lvds_lanes([x for x in range(FPGA_MAX_LVDS_LANES)])

        # Then, enable only specified ones
        self._ll.enable_lvds_lanes(lvds_lanes_ids)

        return

    # Set Measurement period
    def set_meas_period_us(self, period_us=SYNC_PER_DEFAULT_US):
        clk_cycles = self._us_to_clk_cycles(period_us, self.fpga_core_clk)
        self._ll.set_wavegen_sync_per(clk_cycles)
        self._meas_period_us = period_us
        return

    # The capture will start in delay_us after the start command arrives
    def set_glob_start_capt_delay(self, delay_us=50):
        delay_clk_cycles = self._us_to_clk_cycles(delay_us, self.fpga_core_clk)

        half_sync_per_clk_cycles = (
            int(self._us_to_clk_cycles(self._meas_period_us, self.fpga_core_clk)) >> 1
        )

        if delay_clk_cycles > (half_sync_per_clk_cycles - FIFO_RST_ADVANCE_CYCLES):
            print(
                "Warning! Specified delay_us exceeds the maximum value (half of the meas_period)"
            )
            print(
                "Warning! Forced delay_us to max value of half_sync_per_clk_cycles - FIFO_RST_ADVANCE_CYCLES"
            )
            start_capt_time_cycles = 0

        elif delay_clk_cycles < (FIFO_RST_ADVANCE_CYCLES):
            print("Warning! Specified delay_us is too small")
            print("Warning! Forced delay_us to FIFO_RST_ADVANCE_CYCLES")
            start_capt_time_cycles = half_sync_per_clk_cycles - FIFO_RST_ADVANCE_CYCLES
        else:
            start_capt_time_cycles = half_sync_per_clk_cycles - delay_clk_cycles

        self._ll.set_wavegen_start_capt_time(start_capt_time_cycles)
        return

    def set_n_shots(self, n_shots):
        self._ll.set_wavegen_n_shots(n_shots)
        return

    def set_sensing_depth(self, n_samples):
        self._ll.set_samples_counter(n_samples)

        # Calculate and set the data acquisition time
        data_acq_time_us = n_samples / self.afe_clk * 10**6
        data_acq_time_cycles = self._us_to_clk_cycles(
            data_acq_time_us, self.fpga_core_clk
        )

        # Save the value internally
        self._data_acq_time_us = data_acq_time_cycles / self.fpga_core_clk * 10**6

        # Accunt for the FIFO start delay
        data_acq_time_cycles = data_acq_time_cycles + FIFO_START_CAPT_DELAY_CYCLES

        # Account for the safety margin
        data_acq_time_cycles = data_acq_time_cycles + AFE_ACQ_TIME_MARGIN_CYCLES

        self._ll.set_wavegen_afe_acq_time(data_acq_time_cycles)
        return

    # Set AFE capture delay with respect to the TX chip
    def set_afe_start_capt_delay_us(self, start_capt_delay_us=0):
        start_capt_delay_cycles = self._us_to_clk_cycles(
            start_capt_delay_us, self.fpga_core_clk
        )
        # Save the value internally
        self._afe_start_capt_delay_us = (
            start_capt_delay_cycles / self.fpga_core_clk * 10**6
        )

        self._ll.set_wavegen_afe_start_capt_delay(start_capt_delay_cycles)

        return

    ## Advanced Settings of the Wake Up timings (AFE, TX chips) ##

    # Set timings of the Transmit/Receive switch
    def set_tr_switch_wkup_timings_us(
        self, wkup_time_us=TR_SW_WKUP_TIME_DEF_US, sleep_time_us=TR_SW_SLEEP_TIME_DEF_US
    ):
        wkup_time_cycles = self._us_to_clk_cycles(wkup_time_us, self.fpga_core_clk)
        sleep_time_cyces = self._us_to_clk_cycles(sleep_time_us, self.fpga_core_clk)

        self._ll.set_wavegen_trs_wkup_time(wkup_time_cycles)
        self._ll.set_wavegen_trs_sleep_time(sleep_time_cyces)

        return

    # Set AFE wake up timings for AFE and AFE clock
    def set_afe_wkup_timings_us(
        self,
        afe_wkup_time_us=AFE_WKUP_TIME_DEF_US,
        afe_clk_on_time_us=AFE_CLK_ON_TIME_DEF_US,
    ):
        afe_wkup_time_cycles = self._us_to_clk_cycles(
            afe_wkup_time_us, self.fpga_core_clk
        )
        afe_clk_on_time_cycles = self._us_to_clk_cycles(
            afe_clk_on_time_us, self.fpga_core_clk
        )

        self._ll.set_wavegen_afe_wkup_time(afe_wkup_time_cycles)
        self._ll.set_wavegen_afe_clk_on_time(afe_clk_on_time_cycles)

        return

    ## AFE/TX chip reset and power-down mode control fir ICs and buffers ##

    def reset_afe_ic(self, en=True):
        self._ll.reset_afe(en=en)
        return

    def reset_tx_ic(self, en=True):
        self._ll.reset_tx(en=en)
        return

    def set_afe_fast_pwd_ctrl_src(self, ctrl_source="wave_gen"):
        if isinstance(ctrl_source, str):
            self._ll.set_afe_fast_pwd_mux(reg_ctrl=not signal_ctrl_src[ctrl_source])
        else:
            print("Error! ctrl_source is wrong")
        return

    def set_afe_glb_pwd_ctrl_src(self, ctrl_source="wave_gen"):
        if isinstance(ctrl_source, str):
            self._ll.set_afe_glb_pwd_mux(reg_ctrl=not signal_ctrl_src[ctrl_source])
        else:
            print("Error! ctrl_source is wrong")
        return

    def set_tx_tr_en_ctrl_src(self, ctrl_source="wave_gen"):
        if isinstance(ctrl_source, str):
            self._ll.set_tx_tr_en_mux(reg_ctrl=not signal_ctrl_src[ctrl_source])
        else:
            print("Error! ctrl_source is wrong")
        return

    # Force enable the AFE clock output buffer
    # If en=False then the clk buf is controlled by the waveform_gen
    def force_en_afe_clk_buf(self, en=True):
        self._ll.en_afe_clk_buf(en=en)
        return

    # Force enable the TX BF clock output buffer
    # If en=False then the clk buf is controlled by the waveform_gen
    def force_en_tx_clk_buf(self, en=True):
        self._ll.en_tx_clk_buf(en=en)
        return

    # Powerdown AFE IC
    def pwr_down_afe(self, mode="global", en=True):
        if mode == "global":
            self._ll.set_afe_glb_pwd_mux(reg_ctrl=True)
            self._ll.en_afe_glb_pwd_reg(en=en)
        elif mode == "fast":
            self._ll.set_afe_fast_pwd_mux(reg_ctrl=True)
            self._ll.en_afe_fast_pwd_reg(en=en)
        else:
            print("Error! mode is wrong")

    def set_tx_tr_en(self, en=True):
        self._ll.en_tx_tr_en_reg(en=en)

    ## TR_EN Refreshing Counter Settings ##

    def set_tr_en_refresh_cnt_params(
        self, en_refresh=True, refresh_per_us=5000, tr_en_on_time_us=10
    ):
        self._ll.en_wavegen_tr_en_refresh_timer(en=en_refresh)

        refresh_per_cycles = self._us_to_clk_cycles(refresh_per_us, self.fpga_core_clk)
        tr_en_on_time_cycles = self._us_to_clk_cycles(
            tr_en_on_time_us, self.fpga_core_clk
        )

        self._ll.set_wavegen_tr_en_refresh_per(refresh_per_cycles)
        self._ll.set_wavegen_tr_en_refresh_on_time(tr_en_on_time_cycles)

        return

    ## Trigger Settings ##

    def en_ext_trigger(self, en=False):
        self._ll.en_ext_trigger(en=en)
        return

    def set_out_trigger_src(self, source="tx_bf_sync"):
        if isinstance(source, str):
            self._ll.set_out_trig_src_mux(state=source)
        else:
            print("Error! output trigger source is wrong")

        return

    def set_mcu_interrupt_src(self, source="fifo_wr_done"):
        if isinstance(source, str):
            self._ll.set_mcu_int_src_mux(state=source)
        else:
            print("Error! mcu interrupt source is wrong")

        return

    ## TGC Settings ##
    # TO DO

    ## High Level Configuration functions ##

    def default_config(
        self,
        active_lvds_lanes=[x for x in range(FPGA_MAX_LVDS_LANES)],
        sensing_depth_samples=FPGA_MAX_FIFO_DEPTH,
        meas_period_ms=SYNC_PER_DEFAULT_US / 1000,
        n_acquisitions=1,
        afe_clk_high_speed=True,
        tx_bf_clk_high_speed=True,
        fpga_core_clk_high_speed=False,
        afe_start_capt_delay_us=0,
    ):
        # Switch MUX to communicate with TX chip
        cmd_spi = SwitchSpiMux()
        cmd_spi.select_fpga()

        # Make a command sequence
        cmd_seq = TinyProbeCmdSeq([cmd_spi])

        ## Set up PLL settings
        self.set_afe_clk_mux(high_freq=afe_clk_high_speed)
        self.set_tx_bf_clk_mux(high_freq=tx_bf_clk_high_speed)
        self.set_fpga_core_clk_mux(high_freq=fpga_core_clk_high_speed)

        # AFE clk is controlled by the waveform generator
        self.set_afe_clk_en_ctrl_src(ctrl_source="wave_gen")
        # TX clock is powered up by default
        self.pwr_up_clk(clock="TX")

        # Force enable TX clock output buffers
        # (not controlled by waveform generator)
        self.force_en_tx_clk_buf(en=True)

        # AFE clock buffer is controlled by waveform generator
        self.force_en_afe_clk_buf(en=False)

        ## Activate LVDS Lanes
        self.set_active_lvds_lanes(active_lvds_lanes)

        ## Program FIFO write/read depth
        # Data acq time is calculated automatically
        self.set_sensing_depth(n_samples=sensing_depth_samples)

        ## Configure WaveForm Generator
        # Refresh counter
        self.set_tr_en_refresh_cnt_params(
            en_refresh=True,
            refresh_per_us=REFRESH_CNT_PER_DEF_US,
            tr_en_on_time_us=REFRESH_CNT_TR_ON_DEF_US,
        )

        # Number of acquisitions
        self.set_n_shots(n_acquisitions)

        # Measurement period, TR switch sleep and wake-up times
        self.set_meas_period_us(period_us=meas_period_ms * 1000)
        self.set_tr_switch_wkup_timings_us(
            wkup_time_us=TR_SW_WKUP_TIME_DEF_US, sleep_time_us=TR_SW_SLEEP_TIME_DEF_US
        )

        # AFE wake up timings for the IC and for the clock
        self.set_afe_wkup_timings_us(
            afe_wkup_time_us=AFE_WKUP_TIME_DEF_US,
            afe_clk_on_time_us=AFE_CLK_ON_TIME_DEF_US,
        )

        # AFE Fast and Global Power Down mode
        self.set_afe_fast_pwd_ctrl_src(ctrl_source="wave_gen")
        self.pwr_down_afe(mode="global", en=True)

        # AFE start capture delay
        self.set_afe_start_capt_delay_us(start_capt_delay_us=afe_start_capt_delay_us)

        ## Trigger options
        self.en_ext_trigger(en=False)
        self.set_out_trigger_src(source="tx_bf_sync")
        self.set_mcu_interrupt_src(source="fifo_wr_done")

        # Estimation of the throughput
        self._throughput_req = (
            1000
            / meas_period_ms
            * len(np.unique(active_lvds_lanes))
            * 2
            * sensing_depth_samples
            * AFE_RES_BIT_PER_SAMPLE
            / 1e6
        )

        print("Throughput required [Mbps]: ", self._throughput_req)

        cmd_seq.extend(self.get_cmd_sequence(write_all_regs=True))

        return cmd_seq

    def set_tgc_settings(
        self,
        gain_step_period_us=1,
        start_delay_us=0,
        capture_time_us=0,
        finish_delay_us=0,
        match_with_wavegen=False,
    ):
        # If option is selected, match the parameters written earlier to waveform generator
        if match_with_wavegen:
            start_delay_cycles = self._us_to_clk_cycles(
                self._afe_start_capt_delay_us, self.fpga_core_clk
            )
            capture_time_cycles = self._us_to_clk_cycles(
                self._data_acq_time_us, self.fpga_core_clk
            )
            finish_delay_cycles = TGC_DELAY_FINISH_DEF_CYCLES
        else:
            start_delay_cycles = self._us_to_clk_cycles(
                start_delay_us, self.fpga_core_clk
            )
            capture_time_cycles = self._us_to_clk_cycles(
                capture_time_us, self.fpga_core_clk
            )
            finish_delay_cycles = self._us_to_clk_cycles(
                finish_delay_us, self.fpga_core_clk
            )

        print(start_delay_cycles)
        print(capture_time_cycles)
        print(finish_delay_cycles)

        # Clock divider defines the inclination of the TGC amplification curve
        clk_divider = round(gain_step_period_us * 10 ** (-6) * self.fpga_core_clk)

        print(clk_divider)

        # Switch MUX to communicate with TX chip
        cmd_spi = SwitchSpiMux()
        cmd_spi.select_fpga()

        # Make a command sequence
        cmd_seq = TinyProbeCmdSeq([cmd_spi])

        self._ll.set_tgc_clk_divider(clk_divider)
        self._ll.set_tgc_delay_start(start_delay_cycles)
        self._ll.set_tgc_capture_time(start_delay_cycles + capture_time_cycles)
        self._ll.set_tgc_delay_finish(
            start_delay_cycles + capture_time_cycles + finish_delay_cycles
        )

        # Make a command sequence
        cmd_seq.extend(self.get_cmd_sequence(from_history=True))
        return cmd_seq

from tinyprobe.drivers.hal import TP_HAL
from tinyprobe.drivers.ll.tx7332_ll import TP_LL_TX7332
from tinyprobe.protocol.commands import (
    TinyProbeCmdSeq,
    SwitchSpiMux,
    WriteTxReg,
)
import numpy as np

TX7332_NUM_CHANNELS = 32

# For TR SW delays
TX7332_DIV_TO_K = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

# For pulser pattern generator
TX7332_PULSER_LEVELS = {"+HV": 2, "-HV": 1, "GND": 3, "TERM": 7}


class TP_HAL_TX7332(TP_HAL):
    def __init__(self, bf_clk=100 * 10**6):
        super().__init__("TX7332")

        self._ll = TP_LL_TX7332()

        # For on-chip Beamforming
        self._tx_bf_clk = bf_clk
        # Clock divider for beamforming
        self._tx_bf_div_factor = 0
        self._tx_bf_div = 2 ** (self._tx_bf_div_factor)
        self._bf_dt = self._tx_bf_div / self._tx_bf_clk

    @property
    def tx_bf_clk(self):
        return self._tx_bf_clk

    @tx_bf_clk.setter
    def tx_bf_clk(self, new_clk):
        self._tx_bf_clk = new_clk
        self._bf_dt = self._tx_bf_div / self._tx_bf_clk

    def get_cmd_sequence(self, from_history=False):
        # First get the list of regs and vals to write
        addr_list, val_list = self._ll.get_modified_regs_and_vals(
            from_history=from_history
        )

        cmd_seq = TinyProbeCmdSeq([])

        # Add commands to write TX registers to a list
        cmd_list = []

        for i in range(len(addr_list)):
            cmd_list.append(WriteTxReg(addr_list[i], val_list[i]))

        # Extend the command sequence with the list of new commands
        cmd_seq.extend(cmd_list)

        return cmd_seq

    ### Functions to configure TX chip ###
    ### Delay tables ###

    def set_bf_clk_divider(self, factor=0):
        if factor < 0 or factor > 5:
            print("Error! factor is out of range")

        self._tx_bf_div_factor = factor
        self._tx_bf_div = 2**factor

        # Update BF period
        self._bf_dt = self._tx_bf_div / self._tx_bf_clk

    # Set channels' delays in seconds
    def set_delays_s(self, delays, dp_id=0):
        if len(delays) != TX7332_NUM_CHANNELS:
            print("Error! Not enough values to set the delay profile")
            return

        # Convert delays into number of clock periods
        delays = np.rint(np.array(delays) / self._bf_dt)

        if delays.max() > 2**13:
            print("Error! Delay exceeds the range")
            print("Try to increase the BF clk divider.")

        if delays.min() < 0:
            print("Error! Negative delays are not allowed.")

        # Write to the registers
        for i in range(len(delays)):
            self._ll.write_dp_delay(dp_id, i, delays[i])

        return

    def set_delay_prof_id(self, dp_id=0):
        # Write the same delay profile to both groups of channels
        self._ll.bf_prof_sel(dp_id, group=0)
        return

    ### Excitation settings ###
    def set_pulse_pattern(self, n_pulses, pulse_freq, pp_id=0):
        half_pulse_period = 1 / (2 * pulse_freq)

        # Calculate per val (half of the pulse period)
        # expressed in the number of BF clocks
        per_val = np.rint(half_pulse_period / self._bf_dt - 2)

        if per_val > 30:
            print("Error! Frequency is too low for given BF clk.")
            print("Try to increase the clk divider.")
        elif per_val < 0:
            print("Error! Frequency is too high for given BF clk.")
            print("Try to decrease the clk divider.")

        # Set the first level to +HV
        self._ll.write_pp_period(pp_id, 0, per_val)
        self._ll.write_pp_level(pp_id, 0, TX7332_PULSER_LEVELS["+HV"])

        # Set the second level to -HV
        self._ll.write_pp_period(pp_id, 1, per_val)
        self._ll.write_pp_level(pp_id, 1, TX7332_PULSER_LEVELS["-HV"])

        # Set the third state to termination
        self._ll.write_pp_period(pp_id, 2, per_val)
        self._ll.write_pp_level(pp_id, 2, TX7332_PULSER_LEVELS["TERM"])

        # Set repeat count to the number of pulses
        self._ll.repeat_count(count=n_pulses)

        # Configure the tail state
        self._ll.tail_count(count=1)

        return

    def set_patt_prof_id(self, pp_id=0):
        # Write the same pattern profile to both groups of channels
        self._ll.patt_prof_sel(pp_id, group=0)
        return

    def pdn_pulsers(self, pulser_ids, en=True):
        for pulser_id in pulser_ids:
            if pulser_id >= 0 and pulser_id <= 31:
                self._ll.pdn_pulser(pulser_id, en=en)

        return

    ### Common ###
    def load_profile(self):
        # Set Load profile bit
        self._ll.load_profile()
        return

    def pdn_global(self, en=True):
        self._ll.pdn_global(en)
        return

    ### Pre-programmed  configurations ###
    def default_config(
        self, n_pulses=2, pulse_freq_hz=5 * 10**6, tx_start_delay_us=2, tr_sw_delay_us=1
    ):
        # Switch MUX to communicate with TX chip
        cmd_test = SwitchSpiMux()
        cmd_test.select_tx()

        # Make a command sequence
        cmd_seq = TinyProbeCmdSeq([cmd_test])

        # TX SW reset
        self._ll.sw_reset()

        # This function call forces the commands mentioned above
        # to appear earlier in the cmd_seq than the next ones
        # I.e. it forces the order of the previous commands with respect to the next ones
        cmd_seq.extend(self.get_cmd_sequence())

        # Enable LDO in dynamic mode
        self._ll.dyn_pwr_ldo()
        self._ll.dyn_cntrl_1(en=True)
        self._ll.dyn_cntrl_2(en=True)

        # Enable 0.5 A driving strength
        self._ll.drv_mux_sel(sw_control=True)
        self._ll.drv_current_sel(val=2)

        # Set pulse pattern
        self.set_pulse_pattern(n_pulses, pulse_freq_hz, pp_id=0)
        # Select pulse pattern profile
        self.set_patt_prof_id(pp_id=0)

        cmd_seq.extend(self.get_cmd_sequence())

        # Set Load profile bit
        self._ll.load_profile()

        # Set TX start delay (a minimum is 2 us)
        # Page 41 of the datasheet

        if tx_start_delay_us < 2:
            print("Warning: tx_start_delay_us is below 2 us. Forced to 2 us.")
            tx_start_delay_us = 2

        tx_delay_val = np.ceil(
            ((tx_start_delay_us * 10 ** (-6) / self._bf_dt - 121) / 8)
        )

        if tx_delay_val < 0:
            print("Warning: tx_delay_val < 0. Forced to 0")
            tx_delay_val = 0
        elif tx_delay_val >= 2**9:
            print("Error: tx_delay_val is too high. Forced to max value.")
            tx_delay_val = 2**9 - 1
        self._ll.tx_start_delay(tx_delay_val)

        # Delay mode
        self._ll.tr_sw_delay_mode(1)
        # Set Turn On delay (when the T/R switch is on after finishing pulsing (TR_SW_DEL_MODE=1))
        # P 51. Delay is (4 * tr_sw_del + 5 + 2^K) clock cycles where K depends on clk div

        tr_sw_del_val = np.ceil(
            (
                (tr_sw_delay_us * 10 ** (-6) / self._bf_dt)
                - 5
                - 2 ** (TX7332_DIV_TO_K[self._tx_bf_div_factor])
            )
            / 4
        )

        if tr_sw_del_val < 25:
            print("Warning: tr_sw_del_val < 25. Forced to 26")
            tr_sw_del_val = 26
        elif tr_sw_del_val >= 2**12:
            print("Error: tr_sw_del_val is too high. Forced to max value.")
            tx_delay_val = 2**12 - 1

        # Apply to all groups of channels
        self._ll.tr_sw_on_delay(tr_sw_del_val, group=0)

        # Set On-chip beamforming mode
        self._ll.tx_bf_mode(on_chip=True)

        cmd_seq.extend(self.get_cmd_sequence())

        return cmd_seq

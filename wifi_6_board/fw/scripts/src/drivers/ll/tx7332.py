from .ll import TP_LL

# Number of registers
TX7332_DEFAULT_REGS = [0] * 416  # TODO: set the default register values
TX7332_NUM_REGS = len(TX7332_DEFAULT_REGS)  # Number of registers

### Constants for Delay Profile ###

# Number of delay profiles
TX7332_NUM_DELAY_PROFILES = 16
# 20h
TX7332_DELAY_PROFILES_BASE_ADDR = 32
# 10h. i.e. 16 registers per one delay profile
TX7332_DELAY_PROFILES_ADDR_SHIFT = 16
# Bitwidth of a single delay field
TX7332_DELAY_PROFILES_DELAY_WIDTH = 13

# Mapping of the channels IDs to the registers (first arg) and bit shifts (2nd arg)
# withing the delay profile (with respect to the start address for the profile)
TX7332_CHANNEL_TO_SHIFT = {
    0: (15, 0),
    1: (11, 0),
    2: (15, 16),
    3: (11, 16),
    4: (14, 0),
    5: (10, 0),
    6: (14, 16),
    7: (10, 16),
    8: (13, 0),
    9: (9, 0),
    10: (13, 16),
    11: (9, 16),
    12: (12, 0),
    13: (8, 0),
    14: (12, 16),
    15: (8, 16),
    16: (7, 0),
    17: (3, 0),
    18: (7, 16),
    19: (3, 16),
    20: (6, 0),
    21: (2, 0),
    22: (6, 16),
    23: (2, 16),
    24: (5, 0),
    25: (1, 0),
    26: (5, 16),
    27: (1, 16),
    28: (4, 0),
    29: (0, 0),
    30: (4, 16),
    31: (0, 16),
}

### Constants for Pattern Profile ###
# Number of pattern profiles
TX7332_NUM_PATTERN_PROFILES = 32
# 120h
TX7332_PATTERN_PROFILES_BASE_ADDR = 288
# 4h. i.e. 4 registers per one pattern profile
TX7332_PATTERN_PROFILES_ADDR_SHIFT = 4
# Bitwidth of a single field
TX7332_PATTERN_PROFILES_PERIOD_WIDTH = 5
TX7332_PATTERN_PROFILES_LEVEL_WIDTH = 3
# Mapping from period id to register (with respect to the start address for the profile)
# and bit shift
TX7332_PERIOD_TO_SHIFT = {
    0: (0, 3),
    1: (0, 11),
    2: (0, 19),
    3: (0, 27),
    4: (1, 3),
    5: (1, 11),
    6: (1, 19),
    7: (1, 27),
    8: (2, 3),
    9: (2, 11),
    10: (2, 19),
    11: (2, 27),
    12: (3, 3),
    13: (3, 11),
    14: (3, 19),
    15: (3, 27),
}

# Mapping from level id to register (with respect to the start address for the profile)
# and bit shift
TX7332_LEVEL_TO_SHIFT = {
    0: (0, 0),
    1: (0, 8),
    2: (0, 16),
    3: (0, 24),
    4: (1, 0),
    5: (1, 8),
    6: (1, 16),
    7: (1, 24),
    8: (2, 0),
    9: (2, 8),
    10: (2, 16),
    11: (2, 24),
    12: (3, 0),
    13: (3, 8),
    14: (3, 16),
    15: (3, 24),
}


# A class to represent TX7332 chip
class TP_LL_TX7332(TP_LL):
    def __init__(self):
        super().__init__("TX7332", TX7332_DEFAULT_REGS)

        # Pulsers mapping for power down
        self._pul_map = []
        # Channels 0 - 15
        self._pul_map.extend(
            [16, 24, 17, 25, 18, 26, 19, 27, 20, 28, 21, 29, 22, 30, 23, 31]
        )
        # Channels 16 - 31
        self._pul_map.extend([0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15])

    def burst_write(self, en=True):
        self._reg_bit(0, 8, en)
        return

    def load_profile(self):
        self._reg_bit(0, 3, set=True)
        return

    def sw_reset(self):
        self._reg_bit(0, 0, set=True)
        return

    def stndby_g1(self, en=True):
        self._reg_bit(1, 16, en)
        return

    def stndby_g2(self, en=True):
        self._reg_bit(1, 0, en)
        return

    def dyn_cntrl_2(self, en=True):
        self._reg_bit(6, 4, not en)
        return

    def ldo_mode_g1(self, high_power=True):
        self._reg_bit(11, 22, high_power)
        self._reg_bit(11, 23, high_power)
        self._reg_bit(11, 24, high_power)
        self._reg_bit(11, 25, high_power)
        return

    def tr_sw_off_delay(self, delay, group=0):
        if group == 1:
            self._reg_val(12, 6, 16, delay)
        elif group == 2:
            self._reg_val(12, 6, 24, delay)
        elif group == 3:
            self._reg_val(12, 6, 0, delay)
        elif group == 4:
            self._reg_val(12, 6, 8, delay)
        elif group == 0:
            self._reg_val(12, 6, 16, delay)
            self._reg_val(12, 6, 24, delay)
            self._reg_val(12, 6, 0, delay)
            self._reg_val(12, 6, 8, delay)
        else:
            print("Error! No group %d found" % group)

        return

    def dyn_cntrl_1(self, en=True):
        self._reg_bit(15, 4, not en)
        return

    def ldo_mode_g2(self, high_power=True):
        self._reg_bit(20, 22, high_power)
        self._reg_bit(20, 23, high_power)
        self._reg_bit(20, 24, high_power)
        self._reg_bit(20, 25, high_power)
        return

    def tr_sw_on_delay(self, delay, group=0):
        if group == 1:
            self._reg_val(22, 12, 16, delay)
        elif group == 2:
            self._reg_val(21, 12, 16, delay)
        elif group == 3:
            self._reg_val(22, 12, 0, delay)
        elif group == 4:
            self._reg_val(21, 12, 0, delay)
        elif group == 0:
            self._reg_val(22, 12, 16, delay)
            self._reg_val(21, 12, 16, delay)
            self._reg_val(22, 12, 0, delay)
            self._reg_val(21, 12, 0, delay)
        else:
            print("Error! No group %d found" % group)

        return

    def bf_prof_sel(self, dp_id=0, group=0):
        if group == 1:
            self._reg_val(22, 4, 28, dp_id)
        elif group == 2:
            self._reg_val(22, 4, 12, dp_id)
        elif group == 0:
            # Write to both
            self._reg_val(22, 4, 28, dp_id)
            self._reg_val(22, 4, 12, dp_id)
        else:
            print("Error! No group %d found" % group)

        return

    def pdn_clk_sync_1(self, en=True):
        self._reg_bit(23, 10, en)
        return

    def pdn_clk_sync_2(self, en=True):
        self._reg_bit(23, 9, en)
        return

    def drv_mux_sel(self, sw_control=True):
        self._reg_bit(23, 4, sw_control)
        return

    # Controls output  transistor current
    # 00 - 1A, 01 - 0.75 A, 10 - 0.5 A, 11 - 0.25 A
    def drv_current_sel(self, val=2):
        self._reg_val(23, 2, 2, val)
        return

    def en_resync_mux_sel(self, sw_control=True):
        self._reg_bit(23, 1, sw_control)
        return

    def en_resync(self, en=True):
        self._reg_bit(23, 0, en)
        return

    def tx_start_delay(self, val):
        self._reg_val(24, 9, 18, val)
        return

    def cw_wave_mode(self, val):
        if val == 3:
            print("Error! Don't use 11 value for register 23 (cw_wave_mode)")
        self._reg_val(24, 2, 16, val)
        return

    def cw_en_mux_sel(self, sw_control=True):
        self._reg_bit(24, 15, sw_control)
        return

    def cw_en_1(self, en=False):
        self._reg_bit(24, 14, en)
        return

    def cw_en_2(self, en=False):
        self._reg_bit(24, 13, en)
        return

    def cw_damp_count(self, count):
        self._reg_val(24, 3, 9, count)
        return

    def patt_inversion(self, en=False):
        self._reg_bit(24, 6, en)
        return

    def clk_div_factor(self, divider):
        self._reg_val(24, 3, 3, divider)
        return

    def tr_sw_delay_mode(self, mode=0):
        self._reg_bit(24, 1, mode)
        return

    def tx_bf_mode(self, on_chip=True):
        self._reg_bit(24, 0, on_chip)
        return

    def pdn_global(self, en=True):
        self._reg_bit(25, 31, en)
        return

    def dyn_pwr_ldo(self, en=True):
        self._reg_bit(25, 30, en)
        return

    def elastic_mode(self, en=True):
        self._reg_bit(25, 11, en)
        return

    def elastic_repeats(self, repeats=0):
        self._reg_val(25, 6, 12, repeats)
        return

    def tail_count(self, count=0):
        self._reg_val(25, 5, 6, count)
        return

    def repeat_count(self, count=0):
        self._reg_val(25, 5, 1, count)
        return

    ###   Pattern Select   ###

    def patt_prof_sel(self, pp_id=0, group=0):
        if group == 1:
            self._reg_val(31, 6, 0, pp_id)
        elif group == 2:
            self._reg_val(30, 6, 0, pp_id)
        elif group == 0:
            # Write to both
            self._reg_val(31, 6, 0, pp_id)
            self._reg_val(30, 6, 0, pp_id)
        else:
            print("Error! No group %d found" % group)

        return

    ###   Channel Power Down   ###

    def en_tr_switch(self, channel, en=True):
        if channel < 16 and channel >= 0:
            self._reg_bit(26, 16 + channel, en)
        elif channel < 32 and channel >= 16:
            self._reg_bit(26, channel - 16, en)
        else:
            print("Error! Channel id %d is out of range" % channel)

        return

    def pdn_pulser(self, channel, en=True):
        self._reg_bit(27, self._pul_map[channel], en)
        return

    ###   Delay Profile   ###
    def write_dp_delay(self, dp_id, ch_id, delay):
        if dp_id < TX7332_NUM_DELAY_PROFILES and dp_id >= 0:
            # Get the start of the delay profile
            reg_id = (
                TX7332_DELAY_PROFILES_BASE_ADDR
                + TX7332_DELAY_PROFILES_ADDR_SHIFT * dp_id
            )
            # Move to the correspondent register
            reg_id += TX7332_CHANNEL_TO_SHIFT[ch_id][0]

            # Retrieve position within 32-bit word
            bit_shift = TX7332_CHANNEL_TO_SHIFT[ch_id][1]

            # Write to the reg map
            self._reg_val(reg_id, TX7332_DELAY_PROFILES_DELAY_WIDTH, bit_shift, delay)

        else:
            print("Error! dp_id is out of range")

        return

    ###   Pattern Profile   ###
    def write_pp_period(self, pp_id, per_id, period):
        if pp_id < TX7332_NUM_PATTERN_PROFILES and pp_id >= 0:
            # Get the start of the patterm profile
            reg_id = (
                TX7332_PATTERN_PROFILES_BASE_ADDR
                + TX7332_PATTERN_PROFILES_ADDR_SHIFT * pp_id
            )
            # Move to the correspondent register
            reg_id += TX7332_PERIOD_TO_SHIFT[per_id][0]

            # Retrieve position within 32-bit word
            bit_shift = TX7332_PERIOD_TO_SHIFT[per_id][1]

            # Write to the reg map
            self._reg_val(
                reg_id, TX7332_PATTERN_PROFILES_PERIOD_WIDTH, bit_shift, period
            )

        else:
            print("Error! pp_id is out of range")

        return

    def write_pp_level(self, pp_id, lvl_id, level):
        if pp_id < TX7332_NUM_PATTERN_PROFILES and pp_id >= 0:
            # Get the start of the patterm profile
            reg_id = (
                TX7332_PATTERN_PROFILES_BASE_ADDR
                + TX7332_PATTERN_PROFILES_ADDR_SHIFT * pp_id
            )
            # Move to the correspondent register
            reg_id += TX7332_LEVEL_TO_SHIFT[lvl_id][0]

            # Retrieve position within 32-bit word
            bit_shift = TX7332_LEVEL_TO_SHIFT[lvl_id][1]

            # Write to the reg map
            self._reg_val(reg_id, TX7332_PATTERN_PROFILES_LEVEL_WIDTH, bit_shift, level)

        else:
            print("Error! pp_id is out of range")

        return

    def _proc_self_clr_bits(self):
        # Check self-clearing bits
        # Check if SW reset bit was activated
        if self._regs[0] & 1:
            # Set all the values to the default ones (after reset)
            self._regs_reset()
        # Check LOAD_PROF bit
        if self._regs[0] & (1 << 3):
            # Clear self-clearing bit in the register map.
            self._reg_bit(0, 3, set=False)

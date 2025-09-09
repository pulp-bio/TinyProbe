"""
    Copyright (C) 2025 ETH Zurich. All rights reserved.

    Author: Sergei Vostrikov, ETH Zurich

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    SPDX-License-Identifier: Apache-2.0
"""

from tinyprobe.drivers.hal import TP_HAL
from tinyprobe.drivers.ll.afe5832lp_ll import TP_LL_AFE5832LP_GLB, TP_LL_AFE5832LP_DTGC
from tinyprobe.protocol.commands import TinyProbeCmdSeq, SwitchSpiMux, WriteAfeReg

# Named test pattern modes
AFE5832LP_TEST_PATTERNS = {
    "normal": 0,
    "half_zeros_half_ones": 1,
    "altern_zero_one": 2,
    "custom": 3,  # Not supported
    "all_ones": 4,
    "toggle": 5,
    "all_zeros": 6,
    "ramp": 7,
}


class TP_HAL_AFE5832LP(TP_HAL):
    def __init__(self):
        super().__init__("AFE5832LP")

        # Create separate low-level drivers for each die map
        self._ll_glb = TP_LL_AFE5832LP_GLB()
        self._ll_dtgc = TP_LL_AFE5832LP_DTGC()

        self._low_power_mode = False  # Track current low power mode state

    def get_cmd_sequence(self, from_history=False):
        # Gather register changes from both dies
        addr_glb, val_glb = self._ll_glb.get_modified_regs_and_vals(
            from_history=from_history
        )
        addr_dtgc, val_dtgc = self._ll_dtgc.get_modified_regs_and_vals(
            from_history=from_history
        )

        # Build command sequence with proper dtgc flag per die
        cmd_list = [SwitchSpiMux(code=2)]
        for addr, val in zip(addr_glb, val_glb):
            cmd_list.append(WriteAfeReg(addr=addr, val=val, dtgc_die=False))
        for addr, val in zip(addr_dtgc, val_dtgc):
            cmd_list.append(WriteAfeReg(addr=addr, val=val, dtgc_die=True))

        return TinyProbeCmdSeq(cmd_list)

    def set_fixed_gain(self, gain):
        # See AFE5832LP datasheet, section 9.3.4.3.1 about this
        # Final gain would be 36 dB / (gain / 8) dB
        # TODO: Do mapping from gain to attenuation, gain is wrong term here
        if gain > 288 or gain < 0:
            raise ValueError(f"Attenuation must be between 0 and 288, got {gain}")

        # Set fixed gain and mode on DTGC die
        self._ll_dtgc.set_gain(gain)
        self._ll_dtgc.set_fixed_gain_mode()

    def set_test_pattern(self, pattern):
        # Select and apply digital test pattern to global die
        if isinstance(pattern, str):
            pattern_code = AFE5832LP_TEST_PATTERNS.get(pattern.lower(), 0)
        else:
            pattern_code = pattern
        self._ll_glb.set_test_pattern(pattern_code)

    def configure_tgc(self, start_db, stop_db, slope_db_per_us):
        # Convert dB settings to register values
        ATTEN_MAX_GAIN_DB = 36
        POS_TGC_GAIN_DB_PER_STEP = 0.125

        start_db = min(start_db, ATTEN_MAX_GAIN_DB)
        stop_db = min(stop_db, ATTEN_MAX_GAIN_DB)

        start_gain = round(start_db / 0.25)
        stop_gain = round(stop_db / 0.25)

        gain_step_period_us = POS_TGC_GAIN_DB_PER_STEP / slope_db_per_us

        # Program TGC profile to DTGC and enable via global die
        self._ll_dtgc.set_tgc_profile(start_gain, stop_gain)
        self._ll_glb.enable_tgc_profile(enable=False)
        self._ll_dtgc.set_tgc_mode()

        return gain_step_period_us

    def set_lna_gain(self, gain_db):
        # 15 dB = 3, 18 dB = 0, 21 dB = 1
        lna_gain_map = {15: 3, 18: 0, 21: 1}
        if gain_db not in lna_gain_map:
            raise ValueError(f"Unsupported LNA gain setting: {gain_db} dB")
        self._ll_glb.set_lna_gain(lna_gain_map[gain_db])

    def set_pga_gain(self, gain_db):
        # 21 dB = 2, 24 dB = 0, 27 dB = 1
        pga_gain_map = {21: 2, 24: 0, 27: 1}
        if gain_db not in pga_gain_map:
            raise ValueError(f"Unsupported PGA gain setting: {gain_db} dB")
        self._ll_glb.set_pga_gain(pga_gain_map[gain_db])

    def set_lpf_freq(self, freq_mhz):
        # LPF frequency is encoded using LPF_PROG1 and LPF_PROG2 differently depending on power mode
        lpf_map = {
            10: (0b10, 0b10),
            15: (0b11, 0b11),
            20: (0b00, 0b00),
            25: (0b01, 0b01),  # Not supported in low power mode
        }

        if freq_mhz not in lpf_map:
            raise ValueError(f"Unsupported LPF frequency: {freq_mhz} MHz")

        lpf_prog1, lpf_prog2 = lpf_map[freq_mhz]

        if self._low_power_mode:
            if freq_mhz == 25:
                raise ValueError("25 MHz LPF is not supported in low power mode")
            # In LP mode, LPF_PROG2 is fixed to 00 regardless of PROG1
            lpf_prog2 = 0b00

        self._ll_glb.set_lpf_prog(lpf_prog1, lpf_prog2)

    def set_lna_hpf_freq(self, freq_khz):
        # Program the LNA HPF frequency using supported values from Table 100
        freq_to_code = {
            20: 0b00001,
            30: 0b00010,
            40: 0b00011,
            50: 0b00100,
            60: 0b00101,
            70: 0b00110,
            80: 0b00111,
            90: 0b01000,
            100: 0b00000,
            110: 0b00001,
            120: 0b00010,
            130: 0b00011,
            140: 0b00100,
            150: 0b00101,
            160: 0b00110,
            165: 0b00111,
            170: 0b00111,
            180: 0b11000,
            190: 0b11001,
            200: 0b11010,
            210: 0b11011,
            220: 0b11100,
            230: 0b11101,
            240: 0b11110,
            250: 0b11111,
            260: 0b10000,
            270: 0b10001,
            290: 0b10010,
            300: 0b10011,
            310: 0b10100,
        }
        if freq_khz not in freq_to_code:
            raise ValueError(f"Unsupported LNA HPF frequency: {freq_khz} kHz")

        self._ll_glb.set_lna_lpf_freq(freq_to_code[freq_khz])

    def _apply_power_mode(self, low_power: bool):
        # Internal helper to apply power mode state
        self._low_power_mode = low_power
        self._ll_glb.set_low_power(low_power)

    def set_low_power_mode(self):
        # Enable low power mode via internal helper
        self._apply_power_mode(low_power=True)

    def set_low_noise_mode(self):
        # Enable low noise mode via internal helper
        self._apply_power_mode(low_power=False)

    def enable_channel_groups(self, enabled_channels):
        # Disables all LVDS/VCA/ADC channels except those listed in `enabled_channels using the internal low-level driver.
        if not all(0 <= ch <= 15 for ch in enabled_channels):
            raise ValueError("Channel numbers must be in range 0–15.")

        afe_pdn_lvds_ch = [x for x in range(16)]
        for ch in enabled_channels:
            afe_pdn_lvds_ch.remove(ch)

        reg_low = 0
        reg_high = 0
        for ch in afe_pdn_lvds_ch:
            if 0 <= ch < 8:
                reg_low |= 3 << (2 * ch)
            elif 8 <= ch < 16:
                reg_high |= 3 << (2 * (ch - 8))

        self._ll_glb.disable_channel_groups(reg_low, reg_high)

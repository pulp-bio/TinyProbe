from tinyprobe.drivers.ll import TP_LL

AFE5832LP_NUM_REGS = 256
AFE5832LP_DEFAULT_REGS = [0] * AFE5832LP_NUM_REGS


class TP_LL_AFE5832LP_GLB(TP_LL):
    def __init__(self):
        super().__init__("AFE5832LP_GLOBAL", AFE5832LP_DEFAULT_REGS.copy())

    def set_test_pattern(self, pattern_code):
        self._reg_val(
            2, 16, 0, pattern_code << 7
        )  # 0x02: Test pattern at bits 7–9, full overwrite

    def enable_tgc_profile(self, enable):
        self._reg_val(249, 16, 0, int(enable))  # 0xF9: Entire register, only bit 0 used

    def set_lna_gain(self, lna_code):
        self._reg_val(199, 2, 0, lna_code)  # 0xC7: bits 0–1  # 0xC7: bits 0–1

    def set_pga_gain(self, pga_code):
        self._reg_val(199, 2, 2, pga_code)  # 0xC7: bits 2–3  # 0xC7: bits 2–3

    def set_lpf_prog(self, prog1, prog2):
        self._reg_val(199, 2, 5, prog1)  # 0xC7: LPF_PROG1 @5–6
        self._reg_val(
            199, 2, 14, prog2
        )  # 0xC7: LPF_PROG2 @14–15  # 0xC7: LPF PROG1 @5–6, PROG2 @14–15

    def set_lna_lpf_freq(self, code):
        self._reg_val(199, 5, 9, code)  # 0xC7: HPF freq @9–13  # 0xC7: HPF freq @9–13

    def set_low_power(self, enable):
        self._reg_val(200, 16, 0, int(enable))  # 0xC8: Global reg, only bit 0 used

    def disable_channel_groups(self, reg_low, reg_high):
        self._reg_val(197, 16, 0, reg_low)  # 0xC5: disable channels 0–7
        self._reg_val(206, 16, 0, reg_high)  # 0xCE: disable channels 8–15


class TP_LL_AFE5832LP_DTGC(TP_LL):
    def __init__(self):
        super().__init__("AFE5832LP_DTGC", AFE5832LP_DEFAULT_REGS.copy())

    def set_gain(self, gain):
        self._reg_val(181, 16, 0, gain)  # 0xB5: Full register write for gain

    def set_fixed_gain_mode(self):
        self._reg_val(
            182, 16, 0, 2 << 14
        )  # 0xB6: Full write to bits 14–15 for gain mode

    def set_tgc_profile(self, start_gain, stop_gain):
        val = (start_gain << 8) | stop_gain
        self._reg_val(161, 16, 0, val)  # 0xA1: Combined 16-bit write

    def set_tgc_mode(self):
        self._reg_val(
            182, 16, 0, 1 << 11
        )  # 0xB6: bit 11 high for ext. non-uniform mode

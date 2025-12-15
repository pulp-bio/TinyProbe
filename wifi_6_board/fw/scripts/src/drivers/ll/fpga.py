from .ll import TP_LL

# Number of registers
FPGA_DEFAULT_REGS = [
    0x00_00_00_00,  # 0x00: CMD_REG
    0x00_00_00_00,  # 0x01: PLL_CONFIG_REG
    0x00_00_00_00,  # 0x02: LVDS_CH_EN
    0x00_00_00_00,  # 0x03: WAVEFORM_GEN_REG_1
    0x00_00_00_00,  # 0x04: WAVEFORM_GEN_REG_2
    0x00_00_00_00,  # 0x05: WAVEFORM_GEN_REG_3
    0x00_00_00_00,  # 0x06: TGC_REG_1
    0x00_00_00_00,  # 0x07: TGC_REG_2
    0x00_00_00_00,  # 0x08: TGC_REG_3
    0x00_00_00_00,  # 0x09: TGC_REG_4
    0x00_00_00_00,  # 0x0A: AFE_TX_RST_REG
    0x00_00_00_00,  # 0x0B: WAVEFORM_GEN_REG_4
    0x00_00_00_00,  # 0x0C: WAVEFORM_GEN_REG_5
    0x00_00_00_00,  # 0x0D: EXT_INT_TRIG_REG
]

FPGA_NUM_REGS = len(FPGA_DEFAULT_REGS)  # Number of registers

# Commands to the FPGA system controller
FPGA_COMMANDS = {"dummy": 0, "start": 1, "reset": 2, "read_en": 3, "echo": 4}

# Output options for MCU interrupt
FPGA_MCU_INT = {"fifo_wr_done": 0, "afe_tx_trig": 1, "tx_bf_sync": 2, "ext_trig": 3}

# Output options for out trigger
FPGA_OUT_TRIG = {
    "tx_bf_sync": 0,
    "afe_tx_trig": 1,
    "pll_lock": 2,
    "fifo_wr_done": 3,
}


# A class to represent the FPGA
class TP_LL_FPGA(TP_LL):
    def __init__(self):
        super().__init__("FPGA", FPGA_DEFAULT_REGS)

    def get_all_regs_and_vals(self):
        # Update the "old state" of the registers
        self._regs_old = self._regs.copy()

        # Clear the history of the written register
        self._addr_list_hist = []

        return [x for x in range(self._n_regs)], self._regs

    def write_cmd(self, cmd):
        if isinstance(cmd, str):
            self._reg_val(0, 32, 0, FPGA_COMMANDS[cmd])
        elif isinstance(cmd, int):
            self._reg_val(0, 32, 0, cmd)
        else:
            print("Error! cmd is wrong")

    # Cotrols of the PLL's non glitch multiplexers (NGMUXs)
    def set_pll_ngmux_gl0(self, state=0):
        if state:
            self._reg_bit(1, 0, set=True)
        else:
            self._reg_bit(1, 0, set=False)

        return

    def set_pll_ngmux_gl1(self, state=0):
        if state:
            self._reg_bit(1, 1, set=True)
        else:
            self._reg_bit(1, 1, set=False)

        return

    def set_pll_ngmux_gl2(self, state=0):
        if state:
            self._reg_bit(1, 2, set=True)
        else:
            self._reg_bit(1, 2, set=False)

        return

    # Multiplexers for GLx's enable signals
    def set_pll_gl0_en_mux(self, wave_gen_ctrl=True):
        if wave_gen_ctrl:
            self._reg_bit(1, 3, set=True)
        else:
            self._reg_bit(1, 3, set=False)

        return

    def set_pll_gl1_en_mux(self, wave_gen_ctrl=True):
        if wave_gen_ctrl:
            self._reg_bit(1, 5, set=True)
        else:
            self._reg_bit(1, 5, set=False)

        return

    # Enable GL0 clock from the register
    def pll_gl0_en_reg(self, en=True):
        if en:
            self._reg_bit(1, 4, set=True)
        else:
            self._reg_bit(1, 4, set=False)
        return

    # Enable GL1 clock from the register
    def pll_gl1_en_reg(self, en=True):
        if en:
            self._reg_bit(1, 6, set=True)
        else:
            self._reg_bit(1, 6, set=False)

        return

    # Multiplexer controlling if an external signal (SPI SS)
    # drives ARST_N or POWERDOWN_N input of the PLL
    # Note: Active only under specific settings of the SPI_MUX
    def set_pll_pwd_arst_driver_mux(self, arst=True):
        if arst:
            self._reg_bit(1, 7, set=True)
        else:
            self._reg_bit(1, 7, set=False)

        return

    # Enable specified LVDS lanes
    def enable_lvds_lanes(self, lvds_lanes_ids=[]):
        if max(lvds_lanes_ids) > 15 or min(lvds_lanes_ids) < 0:
            print("Error! IDs of the LVDS lanes are outside the range")
            return

        for id in lvds_lanes_ids:
            self._reg_bit(2, id, set=True)

        return

    # Enable specified LVDS lanes
    def disable_lvds_lanes(self, lvds_lanes_ids=[]):
        if max(lvds_lanes_ids) > 15 or min(lvds_lanes_ids) < 0:
            print("Error! IDs of the LVDS lanes are outside the range")
            return

        for id in lvds_lanes_ids:
            self._reg_bit(2, id, set=False)

        return

    # Set the value of Write/Read samples counter
    # When the FPGA received the n_samples, it stops receiving
    # and generates an interrupt
    def set_samples_counter(self, n_samples=2048):
        if n_samples < 0 or n_samples > 2048:
            print("Error: n_samples is out of range")
            return

        self._reg_val(2, 12, 16, n_samples)
        return

    def en_afe_clk_buf(self, en=True):
        self._reg_bit(2, 31, set=en)
        return

    def en_tx_clk_buf(self, en=True):
        self._reg_bit(2, 30, set=en)
        return

    # Settings for the WAVEFORM GENERATOR
    def set_wavegen_sync_per(self, value):
        self._reg_val(3, 16, 16, value)
        return

    def set_wavegen_trs_wkup_time(self, value):
        self._reg_val(3, 8, 8, value)
        return

    def set_wavegen_trs_sleep_time(self, value):
        self._reg_val(3, 8, 0, value)
        return

    def set_wavegen_afe_clk_on_time(self, value):
        self._reg_val(4, 16, 0, value)
        return

    def set_wavegen_afe_wkup_time(self, value):
        self._reg_val(4, 8, 16, value)
        return

    def set_wavegen_afe_acq_time(self, value):
        self._reg_val(5, 16, 0, value)
        return

    def set_wavegen_afe_start_capt_delay(self, value):
        self._reg_val(5, 16, 16, value)
        return

    def set_wavegen_start_capt_time(self, value):
        self._reg_val(11, 16, 16, value)
        return

    def set_wavegen_n_shots(self, value):
        self._reg_val(11, 16, 0, value)
        return

    # Settings for the counter refreshing TR_EN signal
    def set_wavegen_tr_en_refresh_per(self, value):
        self._reg_val(12, 16, 0, value)
        return

    def set_wavegen_tr_en_refresh_on_time(self, value):
        self._reg_val(12, 8, 16, value)
        return

    def en_wavegen_tr_en_refresh_timer(self, en=True):
        self._reg_bit(12, 31, set=en)
        return

    ## Settings for TGC
    def set_tgc_clk_divider(self, value):
        self._reg_val(6, 32, 0, value)
        return

    def set_tgc_capture_time(self, value):
        self._reg_val(7, 32, 0, value)
        # print("Capture time: ", value)
        return

    def set_tgc_delay_finish(self, value):
        self._reg_val(8, 32, 0, value)
        # print("Delay finish time: ", value)
        return

    def set_tgc_delay_start(self, value):
        self._reg_val(9, 32, 0, value)
        # print("Delay start time: ", value)
        return

    ## Reset for AFE and TX chips
    def reset_afe(self, en=True):
        self._reg_bit(10, 0, set=en)
        return

    def reset_tx(self, en=True):
        self._reg_bit(10, 1, set=en)
        return

    # AFE fast and global powerdown + TR_EN signal of the TX IC

    # Mux settings
    # If reg_ctrl is not true that waveform gen controls these signals
    # Otherwise through register
    def set_afe_fast_pwd_mux(self, reg_ctrl=True):
        self._reg_bit(10, 2, set=reg_ctrl)
        return

    def set_afe_glb_pwd_mux(self, reg_ctrl=True):
        self._reg_bit(10, 4, set=reg_ctrl)
        return

    def set_tx_tr_en_mux(self, reg_ctrl=True):
        self._reg_bit(10, 6, set=reg_ctrl)
        return

    # Register control of the signals
    def en_afe_fast_pwd_reg(self, en=False):
        self._reg_bit(10, 3, set=en)
        return

    def en_afe_glb_pwd_reg(self, en=False):
        self._reg_bit(10, 5, set=en)
        return

    def en_tx_tr_en_reg(self, en=False):
        self._reg_bit(10, 7, set=en)
        return

    # External triggering options, MCU interrupt options

    # Enable external trigger (otherwise in SW)
    def en_ext_trigger(self, en=False):
        self._reg_bit(13, 0, set=en)
        return

    def set_mcu_int_src_mux(self, state=0):
        if isinstance(state, str):
            self._reg_val(13, 2, 1, FPGA_MCU_INT[state])
        elif isinstance(state, int):
            self._reg_val(13, 2, 1, state)
        else:
            print("Error! state for the _mcu_int_src_mux is wrong")

    def set_out_trig_src_mux(self, state=0):
        if isinstance(state, str):
            self._reg_val(13, 2, 3, FPGA_OUT_TRIG[state])
        elif isinstance(state, int):
            self._reg_val(13, 2, 3, state)
        else:
            print("Error! state for the out_trig_src_mux is wrong")

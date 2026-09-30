"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Sergei Vostrikov, ETH Zurich
    - Cedric Hirschi, ETH Zurich

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import warnings
from enum import Enum, auto

from ..regmap import Regmap_FPGA


class HAL_FPGA_ClockingTiming:
    """High-Level Abstraction for FPGA clocking/timing control

    This class is responsible for managing FPGA clocking and timing configurations, including:

    - PLL settings
    - waveform generator parameters,
    - timing relationships between different events in the acquisition process
    """

    regmap: Regmap_FPGA
    """Reference to the register map for the FPGA"""

    # -------------------------------------------------------------------------------------------
    # MARK: Constants
    # -------------------------------------------------------------------------------------------

    FREQ_TX_BF_LOW = 20e6
    """Slow TX Beamforming frequency"""
    FREQ_TX_BF_HIGH = 100e6
    """Fast TX Beamforming frequency"""
    FREQ_AFE_LOW = 10e6
    """Slow AFE frequency"""
    FREQ_AFE_HIGH = 30e6
    """Fast AFE frequency"""
    FREQ_FPGA_CORE_LOW = 10e6
    """Slow FPGA Core frequency"""
    FREQ_FPGA_CORE_HIGH = 20e6
    """Fast FPGA Core frequency"""

    _FIFO_START_CAPTURE_DELAY_CYCLES = 5 + 2
    """FIFO start capture signal is delayed (with resp to AFE trig.) by this number of FPGA core clock cycles"""
    _FIFO_RST_ADVANCE_CYCLES = 4 + 1
    """FIFO reset precedes the TX trigger this number of FPGA core clock cycles"""
    _AFE_CAPTURE_TIME_MARGIN_CYCLES = 20
    """Safety margin to make sure all the data is captured by FPGA from the AFE"""
    _AFE_DEFAULT_TGC_DELAY_FINISH_CYCLES = 2
    """TODO"""
    _AFE_POS_TGC_GAIN_DB_PER_STEP = 0.125
    """TODO"""

    # -------------------------------------------------------------------------------------------
    # MARK: Enumerations
    # -------------------------------------------------------------------------------------------

    class _ClockDomain(Enum):
        """Clock domains for PLL configuration"""

        TX_BF = auto()
        """TX Beamforming clock domain"""
        AFE = auto()
        """AFE clock domain"""
        FPGA_CORE = auto()
        """FPGA Core clock domain"""

    class _WaveGenSetting(Enum):
        """Waveform generator settings"""

        SYNC_PERIOD = auto()
        """Defines the total period (in clock cycles) for synchronization events. Determines the entire acquisition period length"""

        TX_WAKEUP = auto()
        """Number of clock cycles before the sync event to enable and power up the TX clock and logic"""
        TX_SLEEP = auto()
        """Number of clock cycles after the sync event to keep the TX clock active before powering it down"""

        AFE_ACTIVE_START = auto()
        """Number of clock cycles before the sync event to power up the AFE"""
        AFE_ACTIVE_DURATION = auto()
        """Duration (in clock cycles) for which the AFE clock remains on before and around the sync event, ensuring stable AFE operation"""

        AFE_CAPTURE_START = auto()
        """Delay (in clock cycles) from the sync trigger event until AFE data acquisition starts"""
        AFE_CAPTURE_DURATION = auto()
        """Duration (in clock cycles) during which the AFE is actively acquiring data after the sync event"""

        CAPTURE_START = auto()
        """Preloads the main counter of the waveform generator, allowing a deterministic delay between the trigger event and the first shot"""
        NUM_SHOTS = auto()
        """Number of acquisitions to be performed before stopping"""

        TR_EN_REFRESH_PERIOD = auto()
        """Defines the interval at which the refresh signal is generated"""
        TR_EN_ACTIVE_DURATION = auto()
        """Specifies how long the refresh signal remains active during each refresh cycle"""
        TR_EN_ENABLED = auto()
        """Enables or disables the periodic refresh mechanism"""

    class _TGCSetting(Enum):
        """TGC settings"""

        CLK_DIVIDER = auto()
        """TGC clock divider"""
        CAPTURE_TIME = auto()
        """TGC capture time"""
        DELAY_START = auto()
        """TGC delay start time"""
        DELAY_FINISH = auto()
        """TGC delay finish time"""

    PeriodicRefresh = Regmap_FPGA.EnumFen

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: Clocking
    # -------------------------------------------------------------------------------------------

    def _pll_set(
        self,
        domain: _ClockDomain,
        *,
        fast: bool | None = None,
        enable: bool | None = None,
        enable_buffer: bool | None = None,
        wavegen_ctrl: bool | None = None,
    ) -> None:
        """Set PLL configuration for the specified clock domain

        Args:
            domain (ClockDomain): The clock domain to configure
            fast (Optional[bool]): If True, select fast clock source
            enable (Optional[bool]): If True, enable the PLL manually (Ignored if `wavegen_ctrl` is True)
            enable_buffer (Optional[bool]): If True, enable the clock buffer
            wavegen_ctrl (Optional[bool]): If True, control PLL enable from waveform generator (Otherwise, control from `enable` parameter)

        Note:
            For the `FPGA_CORE` domain, only the `fast` argument is applicable. Other parameters will be ignored.

        Raises:
            ValueError: If no parameters are provided or if an invalid domain is specified
        """

        if not any(v is not None for v in (fast, enable, enable_buffer, wavegen_ctrl)):
            raise ValueError("At least one parameter must be provided to pll_set")

        match domain:
            case self._ClockDomain.TX_BF:
                if fast is not None:
                    self.regmap.pll_config_reg.tx_mux.value = int(fast)
                if wavegen_ctrl is not None:
                    self.regmap.pll_config_reg.tx_ctrl.value = int(wavegen_ctrl)
                    if wavegen_ctrl:
                        self.regmap.pll_config_reg.tx_en.value = (
                            0  # Ignored when wavegen_ctrl is True
                        )
                if enable is not None:
                    if (
                        self.regmap.pll_config_reg.tx_ctrl.value == 0
                    ):  # wavegen_ctrl is False
                        self.regmap.pll_config_reg.tx_en.value = int(enable)
                    else:
                        raise ValueError(
                            "TX_BF PLL enable ignored since wavegen_ctrl is True"
                        )
                if enable_buffer is not None:
                    self.regmap.lvds_ch_en.clk_ctl_tx.value = int(enable_buffer)

            case self._ClockDomain.AFE:
                if fast is not None:
                    self.regmap.pll_config_reg.afe_mux.value = int(fast)
                if wavegen_ctrl is not None:
                    self.regmap.pll_config_reg.afe_ctrl.value = int(wavegen_ctrl)
                    if wavegen_ctrl:
                        self.regmap.pll_config_reg.afe_en.value = (
                            0  # Ignored when wavegen_ctrl is True
                        )
                if enable is not None:
                    if (
                        self.regmap.pll_config_reg.afe_ctrl.value == 0
                    ):  # wavegen_ctrl is False
                        self.regmap.pll_config_reg.afe_en.value = int(enable)
                    else:
                        raise ValueError(
                            "AFE PLL enable ignored since wavegen_ctrl is True"
                        )
                if enable_buffer is not None:
                    self.regmap.lvds_ch_en.clk_ctl_afe.value = int(enable_buffer)

            case self._ClockDomain.FPGA_CORE:
                if fast is not None:
                    self.regmap.pll_config_reg.fpga_mux.value = int(fast)
                if enable is not None:
                    raise ValueError(
                        "FPGA_CORE PLL does not support manual enable/disable"
                    )
                if enable_buffer is not None:
                    raise ValueError(
                        "FPGA_CORE PLL does not support clock buffer enable/disable"
                    )
                if wavegen_ctrl is not None:
                    raise ValueError(
                        "FPGA_CORE PLL does not support waveform generator control"
                    )

            case _:
                raise ValueError(f"Invalid Clock Domain: {domain}")

    def _pll_get(
        self, domain: _ClockDomain
    ) -> tuple[bool, bool | None, bool | None, bool | None]:
        """Get PLL configuration for the specified clock domain

        Args:
            domain (ClockDomain): The clock domain to query

        Returns:
            status (tuple[bool, Optional[bool], Optional[bool], Optional[bool]]): A tuple containing:
                - fast (bool): Whether the fast clock source is selected
                - enable (Optional[bool]): Whether the PLL is enabled
                - enable_buffer (Optional[bool]): Whether the clock buffer is enabled
                - wavegen_ctrl (Optional[bool]): Whether waveform generator controls the PLL

        Note:
            For the `FPGA_CORE` domain, only the `fast` value is applicable. Other values will be `None`.
        """

        match domain:
            case self._ClockDomain.TX_BF:
                fast = bool(self.regmap.pll_config_reg.tx_mux.value)
                enable = bool(self.regmap.pll_config_reg.tx_en.value)
                enable_buffer = bool(self.regmap.lvds_ch_en.clk_ctl_tx.value)
                wavegen_ctrl = bool(self.regmap.pll_config_reg.tx_ctrl.value)
                return fast, enable, enable_buffer, wavegen_ctrl

            case self._ClockDomain.AFE:
                fast = bool(self.regmap.pll_config_reg.afe_mux.value)
                enable = bool(self.regmap.pll_config_reg.afe_en.value)
                enable_buffer = bool(self.regmap.lvds_ch_en.clk_ctl_afe.value)
                wavegen_ctrl = bool(self.regmap.pll_config_reg.afe_ctrl.value)
                return fast, enable, enable_buffer, wavegen_ctrl

            case self._ClockDomain.FPGA_CORE:
                fast = bool(self.regmap.pll_config_reg.fpga_mux.value)
                return fast, None, None, None

            case _:
                raise ValueError(f"Invalid Clock Domain: {domain}")

    @property
    def freq_tx_bf_hz(self) -> float:
        """TX Beamforming clock frequency in Hz

        Valid values:

        - `FREQ_TX_BF_LOW`
        - `FREQ_TX_BF_HIGH`
        """

        return (
            self.FREQ_TX_BF_HIGH
            if self._pll_get(self._ClockDomain.TX_BF)[0]
            else self.FREQ_TX_BF_LOW
        )

    @freq_tx_bf_hz.setter
    def freq_tx_bf_hz(self, freq: float) -> None:
        if freq == self.FREQ_TX_BF_HIGH:
            self._pll_set(self._ClockDomain.TX_BF, fast=True)
        elif freq == self.FREQ_TX_BF_LOW:
            self._pll_set(self._ClockDomain.TX_BF, fast=False)
        else:
            raise ValueError(
                f"Invalid TX BF frequency: {freq}. Must be either {self.FREQ_TX_BF_LOW} or {self.FREQ_TX_BF_HIGH}."
            )

    @property
    def freq_afe_hz(self) -> float:
        """AFE clock frequency in Hz

        Valid values:

        - `FREQ_AFE_LOW`
        - `FREQ_AFE_HIGH`
        """

        return (
            self.FREQ_AFE_HIGH
            if self._pll_get(self._ClockDomain.AFE)[0]
            else self.FREQ_AFE_LOW
        )

    @freq_afe_hz.setter
    def freq_afe_hz(self, freq: float) -> None:
        if freq == self.FREQ_AFE_HIGH:
            self._pll_set(self._ClockDomain.AFE, fast=True)
        elif freq == self.FREQ_AFE_LOW:
            self._pll_set(self._ClockDomain.AFE, fast=False)
        else:
            raise ValueError(
                f"Invalid AFE frequency: {freq}. Must be either {self.FREQ_AFE_LOW} or {self.FREQ_AFE_HIGH}."
            )

    @property
    def freq_fpga_core_hz(self) -> float:
        """FPGA core clock frequency in Hz

        Valid values:

        - `FREQ_FPGA_CORE_LOW`
        - `FREQ_FPGA_CORE_HIGH`
        """

        return (
            self.FREQ_FPGA_CORE_HIGH
            if self._pll_get(self._ClockDomain.FPGA_CORE)[0]
            else self.FREQ_FPGA_CORE_LOW
        )

    @freq_fpga_core_hz.setter
    def freq_fpga_core_hz(self, freq: float) -> None:
        if freq == self.FREQ_FPGA_CORE_HIGH:
            self._pll_set(self._ClockDomain.FPGA_CORE, fast=True)
        elif freq == self.FREQ_FPGA_CORE_LOW:
            self._pll_set(self._ClockDomain.FPGA_CORE, fast=False)
        else:
            raise ValueError(
                f"Invalid FPGA core frequency: {freq}. Must be either "
                f"{self.FREQ_FPGA_CORE_LOW} or {self.FREQ_FPGA_CORE_HIGH}."
            )

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: Wavegen
    # -------------------------------------------------------------------------------------------

    def _cycles_to_us(self, cycles: int, domain: _ClockDomain) -> float:
        """Convert clock cycles to microseconds based on the clock domain frequency."""
        freq = {
            self._ClockDomain.FPGA_CORE: self.freq_fpga_core_hz,
            self._ClockDomain.TX_BF: self.freq_tx_bf_hz,
            self._ClockDomain.AFE: self.freq_afe_hz,
        }[domain]
        return (cycles / freq) * 1e6

    def _us_to_cycles(self, us: float, domain: _ClockDomain) -> int:
        """Convert microseconds to clock cycles based on the clock domain frequency."""
        freq = {
            self._ClockDomain.FPGA_CORE: self.freq_fpga_core_hz,
            self._ClockDomain.TX_BF: self.freq_tx_bf_hz,
            self._ClockDomain.AFE: self.freq_afe_hz,
        }[domain]
        return round((us / 1e6) * freq)

    def _wavegen_set(self, setting: _WaveGenSetting, value: int | bool) -> None:
        """Set waveform generator parameter

        Args:
            setting (WaveGenSetting): The waveform generator setting to configure
            value (int | bool): The value to set for the specified setting

        Raises:
            ValueError: If an invalid setting is provided
        """

        match setting:
            case self._WaveGenSetting.SYNC_PERIOD:
                self.regmap.waveform_gen_reg_1.sync_period.value = value

            case self._WaveGenSetting.TX_WAKEUP:
                self.regmap.waveform_gen_reg_1.tr_sw_wkp_time.value = value

            case self._WaveGenSetting.TX_SLEEP:
                self.regmap.waveform_gen_reg_1.tr_sw_sleep_time.value = value

            case self._WaveGenSetting.AFE_ACTIVE_START:
                self.regmap.waveform_gen_reg_2.afe_wkp_time.value = value

            case self._WaveGenSetting.AFE_ACTIVE_DURATION:
                self.regmap.waveform_gen_reg_2.afe_clk_on_time.value = value

            case self._WaveGenSetting.AFE_CAPTURE_START:
                self.regmap.waveform_gen_reg_3.capture_delay.value = value

            case self._WaveGenSetting.AFE_CAPTURE_DURATION:
                self.regmap.waveform_gen_reg_3.afe_data_acq_time.value = value

            case self._WaveGenSetting.CAPTURE_START:
                self.regmap.waveform_gen_reg_4.start_capture_time.value = value

            case self._WaveGenSetting.NUM_SHOTS:
                self.regmap.waveform_gen_reg_4.n_shots_to_make.value = value

            case self._WaveGenSetting.TR_EN_REFRESH_PERIOD:
                self.regmap.waveform_gen_reg_5.refresh_cnt_period.value = value

            case self._WaveGenSetting.TR_EN_ACTIVE_DURATION:
                self.regmap.waveform_gen_reg_5.tr_en_on_time.value = value

            case self._WaveGenSetting.TR_EN_ENABLED:
                self.regmap.waveform_gen_reg_5.fen.value = self.PeriodicRefresh(value)

            case _:
                raise ValueError(f"Invalid WaveGenSetting: {setting}")

    def _wavegen_get(self, setting: _WaveGenSetting) -> int | bool:
        """Get waveform generator parameter

        Args:
            setting (WaveGenSetting): The waveform generator setting to query

        Returns:
            value (int | bool): The current value of the specified setting

        Raises:
            ValueError: If an invalid setting is provided
        """

        match setting:
            case self._WaveGenSetting.SYNC_PERIOD:
                assert isinstance(
                    self.regmap.waveform_gen_reg_1.sync_period.value, int
                ), "Expected integer value for SYNC_PERIOD"  # To satisfy type checker

                return self.regmap.waveform_gen_reg_1.sync_period.value

            case self._WaveGenSetting.TX_WAKEUP:
                assert isinstance(
                    self.regmap.waveform_gen_reg_1.tr_sw_wkp_time.value, int
                ), "Expected integer value for TR_SW_WAKEUP"  # To satisfy type checker

                return self.regmap.waveform_gen_reg_1.tr_sw_wkp_time.value

            case self._WaveGenSetting.TX_SLEEP:
                assert isinstance(
                    self.regmap.waveform_gen_reg_1.tr_sw_sleep_time.value, int
                ), "Expected integer value for TR_SW_SLEEP"  # To satisfy type checker

                return self.regmap.waveform_gen_reg_1.tr_sw_sleep_time.value

            case self._WaveGenSetting.AFE_ACTIVE_START:
                assert isinstance(
                    self.regmap.waveform_gen_reg_2.afe_wkp_time.value, int
                ), (
                    "Expected integer value for AFE_ACTIVE_START"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_2.afe_wkp_time.value

            case self._WaveGenSetting.AFE_ACTIVE_DURATION:
                assert isinstance(
                    self.regmap.waveform_gen_reg_2.afe_clk_on_time.value, int
                ), (
                    "Expected integer value for AFE_ACTIVE_DURATION"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_2.afe_clk_on_time.value

            case self._WaveGenSetting.AFE_CAPTURE_START:
                assert isinstance(
                    self.regmap.waveform_gen_reg_3.capture_delay.value, int
                ), (
                    "Expected integer value for AFE_CAPTURE_START"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_3.capture_delay.value

            case self._WaveGenSetting.AFE_CAPTURE_DURATION:
                assert isinstance(
                    self.regmap.waveform_gen_reg_3.afe_data_acq_time.value, int
                ), (
                    "Expected integer value for AFE_CAPTURE_DURATION"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_3.afe_data_acq_time.value

            case self._WaveGenSetting.CAPTURE_START:
                assert isinstance(
                    self.regmap.waveform_gen_reg_4.start_capture_time.value, int
                ), "Expected integer value for CAPTURE_START"  # To satisfy type checker

                return self.regmap.waveform_gen_reg_4.start_capture_time.value

            case self._WaveGenSetting.NUM_SHOTS:
                assert isinstance(
                    self.regmap.waveform_gen_reg_4.n_shots_to_make.value, int
                ), "Expected integer value for NUM_SHOTS"  # To satisfy type checker

                return self.regmap.waveform_gen_reg_4.n_shots_to_make.value

            case self._WaveGenSetting.TR_EN_REFRESH_PERIOD:
                assert isinstance(
                    self.regmap.waveform_gen_reg_5.refresh_cnt_period.value, int
                ), (
                    "Expected integer value for TR_EN_REFRESH_PERIOD"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_5.refresh_cnt_period.value

            case self._WaveGenSetting.TR_EN_ACTIVE_DURATION:
                assert isinstance(
                    self.regmap.waveform_gen_reg_5.tr_en_on_time.value, int
                ), (
                    "Expected integer value for TR_EN_ACTIVE_DURATION"
                )  # To satisfy type checker

                return self.regmap.waveform_gen_reg_5.tr_en_on_time.value

            case self._WaveGenSetting.TR_EN_ENABLED:
                return bool(self.regmap.waveform_gen_reg_5.fen.value)

            case _:
                raise ValueError(f"Invalid WaveGenSetting: {setting}")

    @property
    def meas_period_us(self) -> float:
        """Measurement period between shots in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.SYNC_PERIOD)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @meas_period_us.setter
    def meas_period_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.SYNC_PERIOD, cycles)

    @property
    def num_shots(self) -> int:
        """Number of shots"""

        return self._wavegen_get(self._WaveGenSetting.NUM_SHOTS)

    @num_shots.setter
    def num_shots(self, shots: int) -> None:
        self._wavegen_set(self._WaveGenSetting.NUM_SHOTS, shots)

    @property
    def num_samples(self) -> int:
        """Number of samples per shot"""

        return self.sample_count

    @num_samples.setter
    def num_samples(self, samples: int) -> None:
        self.sample_count = samples

        capture_duration_us = self._cycles_to_us(samples, self._ClockDomain.AFE)
        capture_duration_cycles_core = self._us_to_cycles(
            capture_duration_us, self._ClockDomain.FPGA_CORE
        )

        # Account for FIFO start capture delay and AFE acquisition time margin
        capture_duration_cycles_core += self._FIFO_START_CAPTURE_DELAY_CYCLES
        capture_duration_cycles_core += self._AFE_CAPTURE_TIME_MARGIN_CYCLES

        self._wavegen_set(
            self._WaveGenSetting.AFE_CAPTURE_DURATION, capture_duration_cycles_core
        )

    @property
    def start_capture_delay_global_us(self) -> float:
        """Start capture delay in microseconds (global)"""

        delay_cycles = self._wavegen_get(self._WaveGenSetting.CAPTURE_START)
        cycles_half_sync_per = self._wavegen_get(self._WaveGenSetting.SYNC_PERIOD)

        cycles = cycles_half_sync_per - delay_cycles
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @start_capture_delay_global_us.setter
    def start_capture_delay_global_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        cycles_half_sync_per = self._wavegen_get(self._WaveGenSetting.SYNC_PERIOD) >> 1

        if cycles > (cycles_half_sync_per - self._FIFO_RST_ADVANCE_CYCLES):
            raise ValueError(
                f"Specified delay is too large! Maximum allowable value: {self._cycles_to_us(cycles_half_sync_per - self._FIFO_RST_ADVANCE_CYCLES, self._ClockDomain.FPGA_CORE)} us"
            )
        elif cycles < self._FIFO_RST_ADVANCE_CYCLES:
            raise ValueError(
                f"Specified delay is too small! Minimum allowable value: {self._cycles_to_us(self._FIFO_RST_ADVANCE_CYCLES, self._ClockDomain.FPGA_CORE)} us"
            )

        delay_cycles = cycles_half_sync_per - cycles
        self._wavegen_set(self._WaveGenSetting.CAPTURE_START, delay_cycles)

    @property
    def start_capture_delay_afe_us(self) -> float:
        """Start capture delay in microseconds (AFE)"""

        cycles = self._wavegen_get(self._WaveGenSetting.AFE_CAPTURE_START)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @start_capture_delay_afe_us.setter
    def start_capture_delay_afe_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.AFE_CAPTURE_START, cycles)

    @property
    def tx_wakeup_us(self) -> float:
        """TX Beamforming wakeup time in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.TX_WAKEUP)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @tx_wakeup_us.setter
    def tx_wakeup_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.TX_WAKEUP, cycles)

    @property
    def tx_sleep_us(self) -> float:
        """TX Beamforming sleep time in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.TX_SLEEP)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @tx_sleep_us.setter
    def tx_sleep_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.TX_SLEEP, cycles)

    @property
    def afe_active_start_us(self) -> float:
        """AFE active start time in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.AFE_ACTIVE_START)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @afe_active_start_us.setter
    def afe_active_start_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.AFE_ACTIVE_START, cycles)

    @property
    def afe_active_duration_us(self) -> float:
        """AFE active duration in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.AFE_ACTIVE_DURATION)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @afe_active_duration_us.setter
    def afe_active_duration_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.AFE_ACTIVE_DURATION, cycles)

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: TR_EN signal
    # -------------------------------------------------------------------------------------------

    def _tx_tr_en_set(
        self,
        manual: bool,
        enable: bool | None = None,
    ) -> None:
        """Set TR_EN signal control for TX chips

        Args:
            manual (Optional[bool]): If True, control fast powerdown manually
            enable (Optional[bool]): If True, enable TR_EN manually (Ignored if `manual` is False)

        Raises:
            ValueError: If `manual` is False and `enable` is not provided
        """

        self.regmap.afe_tx_rst_reg.tx_en_src.value = int(manual)
        if manual:
            if enable is None:
                raise ValueError(
                    "When manual is True, 'enable' parameter must be provided"
                )
            self.regmap.afe_tx_rst_reg.tx_en_ctrl.value = int(enable)
        else:
            self.regmap.afe_tx_rst_reg.tx_en_ctrl.value = (
                0  # Ignored when manual is False
            )

    def _tx_tr_en_get(self) -> tuple[bool, bool | None]:
        """Get TR_EN signal control status for TX chips

        Returns:
            status (tuple[bool, Optional[bool]]): A tuple containing:
                - manual (bool): Whether TR_EN is controlled manually
                - enable (Optional[bool]): Whether TR_EN is enabled manually (None if controlled by waveform generator)
        """

        manual = bool(self.regmap.afe_tx_rst_reg.tx_en_src.value)
        if not manual:
            return manual, None
        else:
            enable = bool(self.regmap.afe_tx_rst_reg.tx_en_ctrl.value)
            return manual, enable

    @property
    def tx_tr_en(self) -> bool | None:
        """TR_EN signal mode (True: enabled, False: disabled, None: waveform generator controls)"""

        return self._tx_tr_en_get()[1]

    @tx_tr_en.setter
    def tx_tr_en(self, enable: bool | None) -> None:
        if enable is None:
            self._tx_tr_en_set(manual=False)
        else:
            self._tx_tr_en_set(manual=True, enable=enable)

    @property
    def tr_en_enable(self) -> bool:
        return bool(self._wavegen_get(self._WaveGenSetting.TR_EN_ENABLED))

    @tr_en_enable.setter
    def tr_en_enable(self, enable: bool) -> None:
        self._wavegen_set(self._WaveGenSetting.TR_EN_ENABLED, int(enable))

    @property
    def tr_en_refresh_period_us(self) -> float:
        """TR_EN signal refresh period in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.TR_EN_REFRESH_PERIOD)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @tr_en_refresh_period_us.setter
    def tr_en_refresh_period_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.TR_EN_REFRESH_PERIOD, cycles)

    @property
    def tr_en_active_duration_us(self) -> float:
        """TR_EN signal active duration in microseconds"""

        cycles = self._wavegen_get(self._WaveGenSetting.TR_EN_ACTIVE_DURATION)
        return self._cycles_to_us(cycles, self._ClockDomain.FPGA_CORE)

    @tr_en_active_duration_us.setter
    def tr_en_active_duration_us(self, us: float) -> None:
        cycles = self._us_to_cycles(us, self._ClockDomain.FPGA_CORE)
        self._wavegen_set(self._WaveGenSetting.TR_EN_ACTIVE_DURATION, cycles)

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: TGC
    # -------------------------------------------------------------------------------------------

    def _tgc_set(self, setting: _TGCSetting, value: int) -> None:
        """Set TGC parameter

        Args:
            setting (TGCSetting): The TGC setting to configure
            value (int): The value to set for the specified setting

        Raises:
            ValueError: If an invalid setting is provided
        """

        match setting:
            case self._TGCSetting.CLK_DIVIDER:
                self.regmap.tgc_reg_1.tgc_clk_divider.value = value

            case self._TGCSetting.CAPTURE_TIME:
                self.regmap.tgc_reg_2.tgc_capture_time.value = value

            case self._TGCSetting.DELAY_START:
                self.regmap.tgc_reg_4.tgc_delay_start.value = value

            case self._TGCSetting.DELAY_FINISH:
                self.regmap.tgc_reg_3.tgc_delay_finish.value = value

            case _:
                raise ValueError(f"Invalid TGCSetting: {setting}")

    def _tgc_get(self, setting: _TGCSetting) -> int:
        """Get TGC parameter

        Args:
            setting (TGCSetting): The TGC setting to query

        Returns:
            value (int): The current value of the specified setting

        Raises:
            ValueError: If an invalid setting is provided
        """

        match setting:
            case self._TGCSetting.CLK_DIVIDER:
                assert isinstance(self.regmap.tgc_reg_1.tgc_clk_divider.value, int), (
                    "Expected integer value for CLK_DIVIDER"
                )  # To satisfy type checker

                return self.regmap.tgc_reg_1.tgc_clk_divider.value

            case self._TGCSetting.CAPTURE_TIME:
                assert isinstance(self.regmap.tgc_reg_2.tgc_capture_time.value, int), (
                    "Expected integer value for CAPTURE_TIME"
                )  # To satisfy type checker

                return self.regmap.tgc_reg_2.tgc_capture_time.value

            case self._TGCSetting.DELAY_START:
                assert isinstance(self.regmap.tgc_reg_4.tgc_delay_start.value, int), (
                    "Expected integer value for DELAY_START"
                )  # To satisfy type checker

                return self.regmap.tgc_reg_4.tgc_delay_start.value

            case self._TGCSetting.DELAY_FINISH:
                assert isinstance(self.regmap.tgc_reg_3.tgc_delay_finish.value, int), (
                    "Expected integer value for DELAY_FINISH"
                )  # To satisfy type checker

                return self.regmap.tgc_reg_3.tgc_delay_finish.value

            case _:
                raise ValueError(f"Invalid TGCSetting: {setting}")

    def tgc_settings_set(
        self,
        match_with_wavegen: bool,
        slope_db_per_us: float,
        start_delay_us: float = 0.0,
        capture_time_us: float = 0.0,
        finish_delay_us: float = 0.0,
    ) -> None:
        if match_with_wavegen:
            if start_delay_us != 0.0:
                warnings.warn(
                    "start_delay_us is ignored when match_with_wavegen is True"
                )
            if capture_time_us != 0.0:
                warnings.warn(
                    "capture_time_us is ignored when match_with_wavegen is True"
                )
            if finish_delay_us != 0.0:
                warnings.warn(
                    "finish_delay_us is ignored when match_with_wavegen is True"
                )

            start_delay_cycles = self._wavegen_get(self._WaveGenSetting.CAPTURE_START)
            capture_duration_cycles = self._wavegen_get(
                self._WaveGenSetting.AFE_CAPTURE_DURATION
            )
            finish_delay_cycles = self._AFE_DEFAULT_TGC_DELAY_FINISH_CYCLES
        else:
            start_delay_cycles = self._us_to_cycles(
                start_delay_us, self._ClockDomain.FPGA_CORE
            )
            capture_duration_cycles = self._us_to_cycles(
                capture_time_us, self._ClockDomain.FPGA_CORE
            )
            finish_delay_cycles = self._us_to_cycles(
                finish_delay_us, self._ClockDomain.FPGA_CORE
            )

        gain_step_period_us = self._AFE_POS_TGC_GAIN_DB_PER_STEP / slope_db_per_us
        clk_divider = self._us_to_cycles(
            gain_step_period_us, self._ClockDomain.FPGA_CORE
        )

        self._tgc_set(self._TGCSetting.CLK_DIVIDER, clk_divider)
        self._tgc_set(self._TGCSetting.DELAY_START, start_delay_cycles)
        self._tgc_set(
            self._TGCSetting.CAPTURE_TIME, capture_duration_cycles + start_delay_cycles
        )
        self._tgc_set(
            self._TGCSetting.DELAY_FINISH,
            finish_delay_cycles + capture_duration_cycles + start_delay_cycles,
        )

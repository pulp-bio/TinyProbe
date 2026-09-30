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

import logging

from ..regmap_base import RegisterMapInterface
from .components import (
    HAL_FPGA_LVDS,
    HAL_FPGA_ClockingTiming,
    HAL_FPGA_Power,
    HAL_FPGA_Reset,
    HAL_FPGA_Trigger,
)
from .regmap import Regmap_FPGA


class HAL_FPGA(
    HAL_FPGA_ClockingTiming,
    HAL_FPGA_LVDS,
    HAL_FPGA_Power,
    HAL_FPGA_Reset,
    HAL_FPGA_Trigger,
):
    """High-Level Abstraction for FPGA control"""

    def __init__(self, interface: RegisterMapInterface):
        self.regmap = Regmap_FPGA(interface)
        self._log = logging.getLogger().getChild("hal").getChild("fpga")

        self.regmap.reset()

    def default_setup(
        self,
        lvds_lanes: list[int],
        num_samples: int = HAL_FPGA_LVDS.NUM_SAMPLES_MAX,
        meas_period_us: float = 5000.0,
        num_shots: int = 1,
        afe_clk_fast: bool = True,
        tx_bf_clk_fast: bool = True,
        fpga_core_clk_fast: bool = False,
        capture_delay_afe_us: float = 0.0,
    ) -> None:
        """Generate default FPGA configuration command sequence

        Args:
            lvds_lanes (list[int]): List of enabled LVDS lane indices (0-15)
            num_samples (int): Number of samples per shot
            meas_period_us (float): Measurement period between shots in microseconds
            num_shots (int): Number of shots
            afe_clk_fast (bool): AFE PLL frequency setting (True: fast, False: slow)
            tx_bf_clk_fast (bool): TX BF PLL frequency setting (True: fast, False: slow)
            fpga_core_clk_fast (bool): FPGA core PLL frequency setting (True: fast, False: slow)
            capture_delay_afe_us (float): AFE capture start delay in microseconds
        """

        # Configure PLLs

        ## AFE PLL: Controlled by waveform generator
        self._pll_set(self._ClockDomain.AFE, fast=afe_clk_fast, wavegen_ctrl=True)

        ## TX BF PLL: Manually always enabled
        self._pll_set(
            self._ClockDomain.TX_BF,
            fast=tx_bf_clk_fast,
            wavegen_ctrl=False,
            enable=True,
            enable_buffer=True,
        )

        ## FPGA Core PLL
        self._pll_set(self._ClockDomain.FPGA_CORE, fast=fpga_core_clk_fast)

        # Configure LVDS lanes
        self.lvds_lanes = lvds_lanes

        # Configure sample count
        self.num_samples = num_samples

        # Configure waveform generator

        ## Refresh counter
        self.tr_en_enable = True
        self.tr_en_refresh_period_us = 5000.0
        self.tr_en_active_duration_us = 10.0

        ## Number of shots
        self.num_shots = num_shots

        ## Measurement period
        self.meas_period_us = meas_period_us

        ## TX timings
        self.tx_wakeup_us = 10.0
        self.tx_sleep_us = 3.2

        ## AFE timings
        self.afe_active_start_us = 3.0
        self.afe_active_duration_us = 50.0

        # AFE Fast and Global powerdown modes
        self.powerdown_afe_fast = None  # Waveform generator controls
        self.powerdown_afe_global = True  # Powered down manually

        # AFE capture start delay
        self.start_capture_delay_afe_us = capture_delay_afe_us

        # Triggers
        self.trigger_external_enabled = False
        self.trigger_output_source = self.TriggerSourceOutput.TRIG_OUT_TX_BF_SYNC
        self.trigger_mcu_source = self.TriggerSourceMCU.MCU_INT_FIFO_WR_DONE

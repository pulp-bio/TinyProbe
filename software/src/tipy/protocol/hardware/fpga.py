"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
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

from pydantic import BaseModel, field_validator

from ...hardware.fpga.hal import HAL_FPGA
from .common import enum_validator


class ConfigFPGA(BaseModel):
    lvds_lanes: list[int] = list(range(16))
    fifo_depth: int = 400
    shot_period_ms: float = 5.0
    num_shots: int = 1
    afe_clk_hispeed: bool = False
    txbf_clk_hispeed: bool = True
    fpga_clk_hispeed: bool = False
    afe_startcapt_delay_us: int = 0
    mcu_interrupt_src: HAL_FPGA.TriggerSourceMCU = (
        HAL_FPGA.TriggerSourceMCU.MCU_INT_TX_BF_SYNC
    )

    @field_validator("mcu_interrupt_src", mode="before")
    def validate_mcu_interrupt_src(cls, v: object) -> HAL_FPGA.TriggerSourceMCU:
        return enum_validator(
            "mcu_interrupt_src", "MCU_INT_", v, HAL_FPGA.TriggerSourceMCU
        )

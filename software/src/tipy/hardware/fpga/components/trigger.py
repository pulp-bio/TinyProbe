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

from ..regmap import Regmap_FPGA


class HAL_FPGA_Trigger:
    """High-Level Abstraction for FPGA trigger control

    This class is responsible for managing FPGA trigger-related configurations, including:

    - External trigger settings
    - MCU trigger source selection
    - Output trigger source selection
    """

    regmap: Regmap_FPGA
    """Reference to the register map for the FPGA"""

    # -------------------------------------------------------------------------------------------
    # MARK: Enumerations
    # -------------------------------------------------------------------------------------------

    TriggerSourceMCU = Regmap_FPGA.EnumMim
    """MCU Trigger Source Enum Alias"""
    TriggerSourceOutput = Regmap_FPGA.EnumOtm
    """Output Trigger Source Enum Alias"""

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: Triggers
    # -------------------------------------------------------------------------------------------

    @property
    def trigger_external_enabled(self) -> bool:
        """External trigger enabled"""

        assert isinstance(
            self.regmap.ext_int_trig_reg.eit.value, Regmap_FPGA.EnumEit
        ), (
            "Expected integer value for external trigger enable register"
        )  # To satisfy type checker

        return (
            self.regmap.ext_int_trig_reg.eit.value
            == Regmap_FPGA.EnumEit.EXTERNAL_TRIGGER
        )

    @trigger_external_enabled.setter
    def trigger_external_enabled(self, en: bool) -> None:
        self.regmap.ext_int_trig_reg.eit.value = (
            Regmap_FPGA.EnumEit.EXTERNAL_TRIGGER
            if en
            else Regmap_FPGA.EnumEit.INTERNAL_SW_TRIGGER
        )

    @property
    def trigger_mcu_source(self) -> TriggerSourceMCU:
        """MCU trigger source"""

        val = self.regmap.ext_int_trig_reg.mim.value
        return self.TriggerSourceMCU(val)

    @trigger_mcu_source.setter
    def trigger_mcu_source(self, src: TriggerSourceMCU) -> None:
        self.regmap.ext_int_trig_reg.mim.value = src

    @property
    def trigger_output_source(self) -> TriggerSourceOutput:
        """Output trigger source"""

        val = self.regmap.ext_int_trig_reg.otm.value
        return self.TriggerSourceOutput(val)

    @trigger_output_source.setter
    def trigger_output_source(self, src: TriggerSourceOutput) -> None:
        self.regmap.ext_int_trig_reg.otm.value = src

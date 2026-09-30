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


class HAL_FPGA_Reset:
    """High-Level Abstraction for FPGA reset control

    This class is responsible for managing FPGA reset-related configurations, including:

    - AFE reset control
    - TX reset control
    """

    regmap: Regmap_FPGA
    """Reference to the register map for the FPGA"""

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: Resets
    # -------------------------------------------------------------------------------------------

    @property
    def reset_afe(self) -> bool:
        """Get AFE reset status"""

        return bool(self.regmap.afe_tx_rst_reg.afe.value)

    @reset_afe.setter
    def reset_afe(self, en: bool) -> None:
        """Set AFE reset status"""

        self.regmap.afe_tx_rst_reg.afe.value = int(en)

    @property
    def reset_tx(self) -> bool:
        """Get TX reset status"""

        return bool(self.regmap.afe_tx_rst_reg.tx.value)

    @reset_tx.setter
    def reset_tx(self, en: bool) -> None:
        """Set TX reset status"""

        self.regmap.afe_tx_rst_reg.tx.value = int(en)

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


class HAL_FPGA_Power:
    """High-Level Abstraction for FPGA power control

    This class is responsible for managing FPGA power-related configurations, including:

    - Powerdown control for AFE chip
    - Powerdown control for TX chip
    """

    regmap: Regmap_FPGA
    """Reference to the register map for the FPGA"""

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: Power Control
    # -------------------------------------------------------------------------------------------

    def _afe_pwd_set(
        self,
        fast: bool,
        manual: bool,
        enable: bool | None = None,
    ) -> None:
        """Set powerdown control for AFE and TX chips

        Args:
            fast (Optional[bool]): Control fast powerdown if True, else control global powerdown
            manual (Optional[bool]): If True, control fast powerdown manually
            enable (Optional[bool]): If True, enable powerdown manually (Ignored if `manual` is False)

        Raises:
            ValueError: If an invalid domain is specified
        """

        if fast:
            self.regmap.afe_tx_rst_reg.afe_fpwd_src.value = int(manual)
            if manual:
                if enable is None:
                    raise ValueError(
                        "When manual is True, 'enable' parameter must be provided"
                    )
                self.regmap.afe_tx_rst_reg.afe_fpwd_ctrl.value = int(enable)
            else:
                self.regmap.afe_tx_rst_reg.afe_fpwd_ctrl.value = (
                    0  # Ignored when manual is False
                )
        else:
            self.regmap.afe_tx_rst_reg.afe_gpwd_src.value = int(manual)
            if manual:
                if enable is None:
                    raise ValueError(
                        "When manual is True, 'enable' parameter must be provided"
                    )
                self.regmap.afe_tx_rst_reg.afe_gpwd_ctrl.value = int(enable)
            else:
                self.regmap.afe_tx_rst_reg.afe_gpwd_ctrl.value = (
                    0  # Ignored when manual is False
                )

    def _afe_pwd_get(self, fast: bool) -> tuple[bool, bool | None]:
        """Get powerdown control status for AFE and TX chips

        Args:
            fast (bool): If True, query fast powerdown status, else query global powerdown

        Returns:
            status (tuple[bool, Optional[bool]]): A tuple containing:
                - manual (bool): Whether powerdown is controlled manually
                - enable (Optional[bool]): Whether powerdown is enabled manually (None if not controlled manually)
        """

        if fast:
            manual = bool(self.regmap.afe_tx_rst_reg.afe_fpwd_src.value)
            if not manual:
                return manual, None
            else:
                enable = bool(self.regmap.afe_tx_rst_reg.afe_fpwd_ctrl.value)
                return manual, enable
        else:
            manual = bool(self.regmap.afe_tx_rst_reg.afe_gpwd_src.value)
            if not manual:
                return manual, None
            else:
                enable = bool(self.regmap.afe_tx_rst_reg.afe_gpwd_ctrl.value)
                return manual, enable

    @property
    def powerdown_afe_fast(self) -> bool | None:
        """AFE Fast powerdown mode (True: powered down, False: powered up, None: waveform generator controls)"""

        return self._afe_pwd_get(fast=True)[1]

    @powerdown_afe_fast.setter
    def powerdown_afe_fast(self, enable: bool | None) -> None:
        if enable is None:
            self._afe_pwd_set(fast=True, manual=False)
        else:
            self._afe_pwd_set(fast=True, manual=True, enable=enable)

    @property
    def powerdown_afe_global(self) -> bool | None:
        """AFE Global powerdown mode (True: powered down, False: powered up, None: waveform generator controls)"""

        return self._afe_pwd_get(fast=False)[1]

    @powerdown_afe_global.setter
    def powerdown_afe_global(self, enable: bool | None) -> None:
        if enable is None:
            self._afe_pwd_set(fast=False, manual=False)
        else:
            self._afe_pwd_set(fast=False, manual=True, enable=enable)

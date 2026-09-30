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


class HAL_FPGA_LVDS:
    """High-Level Abstraction for FPGA LVDS control

    This class is responsible for managing FPGA LVDS-related configurations, including:

    - Enabling/disabling LVDS lanes
    - Setting sample count for FIFO read/write operations
    """

    regmap: Regmap_FPGA
    """Reference to the register map for the FPGA"""

    # -------------------------------------------------------------------------------------------
    # MARK: Constants
    # -------------------------------------------------------------------------------------------

    NUM_LVDS_LANES = 16
    """Number of LVDS lanes supported"""
    NUM_SAMPLES_MAX = 2048
    """Maximum number of samples supported by the FPGA waveform capture."""

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: LVDS lane control
    # -------------------------------------------------------------------------------------------

    @property
    def lvds_lanes(self) -> list[int]:
        """Currently enabled LVDS lanes"""

        reg_value = self.regmap.lvds_ch_en.lvds_ch_en.value

        assert isinstance(reg_value, int), (
            "Expected integer value for LVDS channel enable register"
        )  # To satisfy type checker

        enabled_lanes: list[int] = []
        for id in range(self.NUM_LVDS_LANES):
            if reg_value & (1 << id):
                enabled_lanes.append(id)

        return enabled_lanes

    @lvds_lanes.setter
    def lvds_lanes(self, ids: list[int]) -> None:
        if any(id < 0 or id >= self.NUM_LVDS_LANES for id in ids):
            raise ValueError(
                f"LVDS lane IDs must be in the range 0-{self.NUM_LVDS_LANES - 1}"
            )

        self.regmap.lvds_ch_en.lvds_ch_en.value = sum(1 << id for id in ids)

    def lvds_lanes_enable(self, ids: list[int]) -> None:
        """Enable specified LVDS lanes

        Args:
            ids (list[int]): List of LVDS lane IDs to enable

        Raises:
            ValueError: If any ID is outside the valid range (0 to `NUM_LVDS_LANES` - 1)
        """

        if any(id < 0 or id >= self.NUM_LVDS_LANES for id in ids):
            raise ValueError(
                f"LVDS lane IDs must be in the range 0-{self.NUM_LVDS_LANES - 1}"
            )

        assert isinstance(self.regmap.lvds_ch_en.lvds_ch_en.value, int), (
            "Expected integer value for LVDS channel enable register"
        )  # To satisfy type checker

        self.regmap.lvds_ch_en.lvds_ch_en.value |= sum(1 << id for id in ids)

    def lvds_lanes_disable(self, ids: list[int]) -> None:
        """Disable specified LVDS lanes

        Args:
            ids (list[int]): List of LVDS lane IDs to disable

        Raises:
            ValueError: If any ID is outside the valid range (0 to `NUM_LVDS_LANES` - 1)
        """

        if any(id < 0 or id >= self.NUM_LVDS_LANES for id in ids):
            raise ValueError(
                f"LVDS lane IDs must be in the range 0-{self.NUM_LVDS_LANES - 1}"
            )

        assert isinstance(self.regmap.lvds_ch_en.lvds_ch_en.value, int), (
            "Expected integer value for LVDS channel enable register"
        )  # To satisfy type checker

        self.regmap.lvds_ch_en.lvds_ch_en.value &= ~sum(1 << id for id in ids)

    # -------------------------------------------------------------------------------------------
    # MARK: Settings: FIFO Read/Write Count
    # -------------------------------------------------------------------------------------------

    @property
    def sample_count(self) -> int:
        """Sample count for FIFO read/write operations"""

        assert isinstance(self.regmap.lvds_ch_en.fifo_rd_wr_cnt.value, int), (
            "Expected integer value for FIFO read/write count register"
        )  # To satisfy type checker

        return self.regmap.lvds_ch_en.fifo_rd_wr_cnt.value

    @sample_count.setter
    def sample_count(self, count: int) -> None:
        self.regmap.lvds_ch_en.fifo_rd_wr_cnt.value = (
            count  # Register map will handle value limits
        )

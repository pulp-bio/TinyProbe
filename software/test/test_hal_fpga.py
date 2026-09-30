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

import logging

import pytest

from tipy.control.methods import TinyprobeMethods
from tipy.hardware.fpga.hal import HAL_FPGA
from tipy.hardware.fpga.regmap import Interface

methods = TinyprobeMethods()


@pytest.fixture
def intf() -> Interface:
    return Interface(logging.getLogger().getChild("intf"))


@pytest.fixture
def hal(intf: Interface) -> HAL_FPGA:
    return HAL_FPGA(intf)


class TestHAL_FPGA:
    def test_init(self, intf: Interface):
        hal_fpga = HAL_FPGA(intf)
        assert hal_fpga.regmap._interface is intf

    def test_default_setup(self, hal: HAL_FPGA):
        hal.default_setup(lvds_lanes=list(range(16)))
        # assert len(cmds) > 0

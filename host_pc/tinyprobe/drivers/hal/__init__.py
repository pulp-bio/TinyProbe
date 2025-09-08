"""
    Copyright (C) 2025 ETH Zurich. All rights reserved.

    Author: Cedric Hirschi, ETH Zurich

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

   SPDX-License-Identifier: Apache-2.0
"""

from tinyprobe.drivers.ll.fpga_ll import TP_LL_FPGA
from tinyprobe.drivers.ll.afe5832lp_ll import TP_LL_AFE5832LP_GLB, TP_LL_AFE5832LP_DTGC
from tinyprobe.drivers.ll.tx7332_ll import TP_LL_TX7332

DRIVERS_HAL = {
    "FPGA": TP_LL_FPGA,
    "AFE5832LP": [TP_LL_AFE5832LP_GLB, TP_LL_AFE5832LP_DTGC],
    "TX7332": TP_LL_TX7332,
}


class TP_HAL(object):
    def __init__(self, name: str):
        self._name = name

        if name not in DRIVERS_HAL:
            raise ValueError(f"Unknown driver: {name}")

    def __str__(self):
        return self._name + " HAL Driver"

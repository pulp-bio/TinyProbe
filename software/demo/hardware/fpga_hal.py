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

from tipy.hardware.fpga.hal import HAL_FPGA
from tipy.hardware.regmap_base import Interface
from tipy.tools.logging import setup_logging

log = setup_logging("DEBUG")


intf = Interface(log.getChild("intf"))

log.info("Initializing FPGA HAL")
hal = HAL_FPGA(intf)

log.info("Performing default setup")
hal.default_setup(list(range(16)))

log.info("Setting number of shots to 100")
hal.num_shots = 100

log.info("Setting up TGC settings")
hal.tgc_settings_set(False, 0.5)

log.info("Changed registers:")
for addr, val in intf.pull().items():
    log.info(f"  {addr:#04x}: {val:#010x}")

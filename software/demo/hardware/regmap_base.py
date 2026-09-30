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

from tipy.hardware.regmap_base import Interface
from tipy.tools.logging import setup_logging

log = setup_logging("DEBUG")


intf = Interface(log.getChild("intf"))

intf.write(0x00, 3, 4, 12) # Write 4 bits at offset 3 of register 0x00 with value 12
intf.write(0x01, 0, 8, 255) # Write 8 bits at offset 0 of register 0x01 with value 255

log.info("Changed registers:")
for addr, val in intf.pull().items():
    log.info(f"  {addr:#04x}: {val:#010x}")

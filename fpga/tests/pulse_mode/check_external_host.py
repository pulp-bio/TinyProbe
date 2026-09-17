# Copyright 2026 LisaMaria Odermatt
# Copyright and related rights are licensed under the Solderpad Hardware
# License, Version 0.51 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
# or agreed to in writing, software, hardware and materials distributed under
# this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Authors:
#   LisaMaria Odermatt
# -----------------------------------------------------------------------------
# Description:
#   Check TiPy ultrasound and optoacoustic mode register settings without
#   connected hardware.
# -----------------------------------------------------------------------------

"""Run with the tipy virtualenv Python; no hardware is used."""
import ast
import logging
from pathlib import Path
from tipy.hardware.fpga.hal import HAL_FPGA
from tipy.hardware.regmap_base import Interface
from tipy.modality.hardware.fpga import ConfigFGPA

interface = Interface(logging.getLogger('external-test'))
hal = HAL_FPGA(interface)
for mode, bits in [('US', 0), ('OA', 1), ('OA_EXTERNAL', 3), ('US', 0)]:
    hal.default_setup(lvds_lanes=list(range(16)), num_accumulation=3, pulse_mode=mode)
    registers = interface.pull()
    assert (registers[12] >> 24) & 3 == bits, registers
    assert (registers[13] & 1) == (mode == 'OA_EXTERNAL')
    assert registers[11] & 255 == 3
    assert hal.pulse_mode == mode
    assert ConfigFGPA(pulse_mode=mode).pulse_mode == mode

root=Path(__import__('tipy').__file__).parent
for relative in ['hardware/fpga/regmap.py', 'hardware/fpga/hal.py',
                 'modality/hardware/fpga.py', 'modality/ultrasound_simple/flow.py',
                 'modality/ultrasound_combined/flow.py', 'modality/ultrasound_doppler/flow.py']:
    ast.parse((root/relative).read_text())
print('PASS: US/OA/OA_EXTERNAL register values, default setup, mode switching, accumulation count, config validation and Python syntax')

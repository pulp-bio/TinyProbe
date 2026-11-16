# Copyright 2026 ETH Zurich
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
#   Federico Villani
# -----------------------------------------------------------------------------
# Description:
#   Set the device and operating conditions, generate vendor cores, and
#   configure the Libero project.
# -----------------------------------------------------------------------------

# Board device and operating conditions.
set_device -family {IGLOO2} -die {M2GL050} -package {400 VF} -speed {STD} \
    -die_voltage {1.2} -part_range {IND} \
    -adv_options {TEMPR:10 25 60} -adv_options {VOLTR:IND} \
    -adv_options {RESTRICTSPIPINS:0}

# Generate the vendor cores from the local Libero vault.
create_and_configure_core -core_vlnv {Actel:SgCore:FCCC:2.0.201} -component_name {Clock_gen} -params {\
"ADVANCED_TAB_CHANGED:true"  \
"CLK0_PAD_IS_USED:false"  \
"GL0_IN_1_SRC:PLL"  \
"GL0_OUT_0_FREQ:20"  \
"GL0_OUT_1_FREQ:100"  \
"GL0_OUT_IS_GATED:true"  \
"GL1_IN_1_SRC:PLL"  \
"GL1_IS_USED:true"  \
"GL1_OUT_0_FREQ:20"  \
"GL1_OUT_1_FREQ:60"  \
"GL1_OUT_IS_GATED:true"  \
"GL2_IN_1_SRC:PLL"  \
"GL2_IS_USED:true"  \
"GL2_OUT_0_FREQ:10"  \
"GL2_OUT_1_FREQ:20"  \
"GPD0_IS_USED:true"  \
"GPD1_IS_USED:true"  \
"GPD2_IS_USED:true"  \
"GPD3_IS_USED:true"  \
"INIT:001C007F98000044574003F1842D484A0E739DE478140C3C04A03"  \
"NGMUX0_HOLD_IS_USED:true"  \
"NGMUX0_IS_USED:true"  \
"NGMUX1_HOLD_IS_USED:true"  \
"NGMUX1_IS_USED:true"  \
"NGMUX2_HOLD_IS_USED:true"  \
"NGMUX2_IS_USED:true"  \
"PLL_EXPOSE_RESETS:true"  \
"PLL_IN_FREQ:16"  \
"PLL_IN_SRC:OSC_XTAL"  \
"VCOFREQUENCY:600.000"  \
"XTLOSC_IS_USED:true"   }

create_and_configure_core -core_vlnv {Actel:SgCore:OSC:2.0.101} -component_name {EXT_OSC} -params {\
"XTLOSC_DRIVES_CCC:1"  \
"XTLOSC_FREQ:16.00"  \
"XTLOSC_IS_USED:1"   }

create_and_configure_core -core_vlnv {Actel:DirectCore:COREFIFO:2.8.101} -component_name {QSPI_STREAM_FIFO} -params {\
"CTRL_TYPE:2"  \
"PREFETCH:true"  \
"RDEPTH:32"  \
"READ_DVALID:true"  \
"RWIDTH:32"  \
"WDEPTH:32"  \
"WWIDTH:32"   }

create_and_configure_core -core_vlnv {Actel:DirectCore:COREFIFO:2.8.101} -component_name {RF_DATA_FIFO} -params {\
"AE_STATIC_EN:true"  \
"AEVAL:2"  \
"CTRL_TYPE:2"  \
"PREFETCH:true"  \
"READ_DVALID:true"  \
"RWIDTH:26"  \
"WWIDTH:26"   }

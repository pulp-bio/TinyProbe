# The following Solderpad notice applies to TinyProbe modifications.
# The original CC0 notice is retained below.
#
# Copyright 2021-2026 ETH Zurich
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
#   Sergei Vostrikov
#   LisaMaria Odermatt
#   Federico Villani
# -----------------------------------------------------------------------------
# Description:
#   Check waveform-generator timing, FIFO controls and transmitter/AFE
#   outputs.
# -----------------------------------------------------------------------------

# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer

PERIOD = 100
SET_DELAY = 0.1 * PERIOD
units = "ns"
async def reset_dut(clk_sig, reset_sig):
    # rst_ni is active low.  Drive the HDL handle itself, not the local
    # Python variable passed to this helper.
    reset_sig.value = 1
    await FallingEdge(clk_sig)
    await Timer(SET_DELAY, unit=units)
    reset_sig.value = 0
    await RisingEdge(clk_sig)
    await Timer(SET_DELAY, unit=units)
    reset_sig.value = 1
    await RisingEdge(clk_sig)
    print('Reset done!!')

@cocotb.test()
async def mem_ctrl_test(dut):
    """ Waveform Generator test """

    # SYNC_PERIOD_DEF     = int("0x07CF", 0) # = 5000 Hz
    SYNC_PERIOD_DEF     = 50000 # = 200 Hz
    CAPTURE_DELAY_DEF   = int("0x00", 0)
    TX_WAKE_UP_TIME_DEF = int("0x63", 0)
    TX_SLEEP_TIME_DEF   = int("0x20", 0)
    AFE_WAKE_UP_TIME    = int("0x1E", 0)
    AFE_CLK_ON_TIME     = int("0x01F4", 0)
    AFE_DATA_ACQ_TIME   = int("0x64", 0)

    TR_EN_PERIOD_DEF    = 50000 # = 200 Hz
    TR_EN_ON_TIME_DEF   = 240 # = 10 us


    # ns
    delay = 100
    long_delay = SYNC_PERIOD_DEF * 1/10**6 * 10 **9

    # Initialize clock
    clock = Clock(dut.clk, PERIOD, unit=units)

    cocotb.start_soon(clock.start())  # Start the clock

    ##################### Set default values #####################

    # dut.sync_period       <= SYNC_PERIOD_DEF
    dut.sync_period.value       = 11999
    dut.capture_delay.value     = CAPTURE_DELAY_DEF
    dut.tx_wake_up_time.value   = TX_WAKE_UP_TIME_DEF
    dut.tx_sleep_time.value     = TX_SLEEP_TIME_DEF
    dut.afe_wake_up_time.value  = AFE_WAKE_UP_TIME
    dut.afe_clk_on_time.value   = AFE_CLK_ON_TIME
    dut.afe_data_acq_time.value = AFE_DATA_ACQ_TIME

    dut.n_shots.value           = 11

    dut.tr_en_period.value      = TR_EN_PERIOD_DEF
    dut.tr_en_on_time.value     = TR_EN_ON_TIME_DEF
    dut.refresh_en.value        = 1

    dut.start_capture.value     = 0

    dut.start_cap_time.value    = 0

    dut.fifo_rd_busy.value      = 0

    ##################### Make a reset ##################### 

    # Some delay
    await Timer(delay, unit=units)

    await FallingEdge(dut.clk)  # Synchronize with the clock

    # Make a reset
    await reset_dut(dut.clk, dut.rst_n)

    ##################### Set start Capture time ##################### 
    await ClockCycles(dut.clk, random.randint(0, 2))
    # dut.start_cap_time    <= int(SYNC_PERIOD_DEF/2)
    dut.start_cap_time.value    = 0
    await ClockCycles(dut.clk, random.randint(0, 2))

    ##################### Start capture ##################### 

    # Some delay
    await ClockCycles(dut.clk, random.randint(0, SYNC_PERIOD_DEF))
    

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    dut.start_capture.value = 0

    # The start command must load the configured number of shots before the
    # first 11,999-cycle waveform period completes.
    await ClockCycles(dut.clk, 5)
    assert int(dut.dut.shot_cnt_q.value) == 11, "start_capture did not load n_shots"

    # Some long delay
    await ClockCycles(dut.clk, random.randint(SYNC_PERIOD_DEF, SYNC_PERIOD_DEF*2))

    ##################### Change params and Start capture again ##################### 

    await RisingEdge(dut.clk)
    # Data acquisition time = 70 uS
    dut.afe_data_acq_time.value = 700
    # Capture delay 10 uS
    dut.capture_delay.value     = 100
    # AFE clock on time before wake up = 20 uS
    dut.afe_clk_on_time.value   = 200

    # Set start Capture time
    await ClockCycles(dut.clk, random.randint(0, 2))
    dut.start_cap_time.value    = random.randint(0, int(SYNC_PERIOD_DEF/2))

    dut.fifo_rd_busy.value      = 1

    # Change parameters of the refreshing timer
    dut.refresh_en.value        = 0
    await ClockCycles(dut.clk, random.randint(1, SYNC_PERIOD_DEF))

    dut.tr_en_period.value      = int(TR_EN_PERIOD_DEF/2)
    dut.tr_en_on_time.value     = int(TR_EN_ON_TIME_DEF/2)
    dut.refresh_en.value        = 1

    dut.fifo_rd_busy.value      = 1

    # Some delay
    await ClockCycles(dut.clk, random.randint(1, SYNC_PERIOD_DEF))

    dut.fifo_rd_busy.value      = 0

    # Some delay
    await ClockCycles(dut.clk, random.randint(1, 2*SYNC_PERIOD_DEF))

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    dut.start_capture.value = 0

    # Some long delay
    await ClockCycles(dut.clk, random.randint(2*SYNC_PERIOD_DEF, 3*SYNC_PERIOD_DEF))

    ##################### Repeat Start capture ##################### 

    await RisingEdge(dut.clk)
    # Data acquisition time = 110 uS
    dut.afe_data_acq_time.value = 1100
    # Capture delay 12 uS
    dut.capture_delay.value     = 120
    # AFE clock on time before wake up = 22 uS
    dut.afe_clk_on_time.value   = 220


    # Wait one sync cycle
    await ClockCycles(dut.clk, SYNC_PERIOD_DEF)

    # Some delay
    await ClockCycles(dut.clk, random.randint(0, SYNC_PERIOD_DEF))

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    dut.start_capture.value = 0

    # Some long delay
    await ClockCycles(dut.clk, random.randint(2*SYNC_PERIOD_DEF, 3*SYNC_PERIOD_DEF))

    print('Finished')

# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import random
import struct
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles, Timer

PERIOD = 100
SET_DELAY = 0.1 * PERIOD
units = "ns"
async def reset_dut(clk_sig, reset_sig):
    await FallingEdge(clk_sig)
    await Timer(SET_DELAY, units=units)
    reset_sig <= 1
    await RisingEdge(clk_sig)
    await Timer(SET_DELAY, units=units)
    reset_sig <= 0
    print('Reset done!!')
    await FallingEdge(clk_sig)
    await Timer(SET_DELAY, units=units)
    reset_sig <= 1

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
    TR_EN_ON_TIME_DEF   = 500 # = 10 us


    # ns
    delay = 100
    long_delay = SYNC_PERIOD_DEF * 1/10**6 * 10 **9

    # Initialize clocks
    clock = Clock(dut.clk, PERIOD, units=units)  # Create a 10us period clock on port clk

    cocotb.fork(clock.start())  # Start the clock

    ##################### Set default values #####################

    # dut.sync_period       <= SYNC_PERIOD_DEF
    dut.sync_period       <= 11999
    dut.capture_delay     <= CAPTURE_DELAY_DEF
    dut.tx_wake_up_time   <= TX_WAKE_UP_TIME_DEF
    dut.tx_sleep_time     <= TX_SLEEP_TIME_DEF
    dut.afe_wake_up_time  <= AFE_WAKE_UP_TIME
    dut.afe_clk_on_time   <= AFE_CLK_ON_TIME
    dut.afe_data_acq_time <= AFE_DATA_ACQ_TIME

    dut.n_shots           <= 11

    dut.tr_en_period      <= TR_EN_PERIOD_DEF
    dut.tr_en_on_time     <= TR_EN_ON_TIME_DEF
    dut.refresh_en        <= 1

    dut.start_capture     <= 0

    dut.start_cap_time    <= 0

    dut.fifo_rd_busy      <= 0

    ##################### Make a reset ##################### 

    # Some delay
    await Timer(delay, units=units)

    await FallingEdge(dut.clk)  # Synchronize with the clock

    # Make a reset
    await reset_dut(dut.clk, dut.rst_n)

    ##################### Set start Capture time ##################### 
    await ClockCycles(dut.clk, random.randint(0, 2))
    # dut.start_cap_time    <= int(SYNC_PERIOD_DEF/2)
    dut.start_cap_time    <= 0
    await ClockCycles(dut.clk, random.randint(0, 2))

    ##################### Start capture ##################### 

    # Some delay
    await ClockCycles(dut.clk, random.randint(0, SYNC_PERIOD_DEF))
    

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture = 1
    await RisingEdge(dut.clk)
    dut.start_capture = 0

    # Some long delay
    await ClockCycles(dut.clk, random.randint(SYNC_PERIOD_DEF, SYNC_PERIOD_DEF*2))

    ##################### Change params and Start capture again ##################### 

    await RisingEdge(dut.clk)
    # Data acquisition time = 70 uS
    dut.afe_data_acq_time <= 700
    # Capture delay 10 uS
    dut.capture_delay     <= 100
    # AFE clock on time before wake up = 20 uS
    dut.afe_clk_on_time   <= 200

    # Set start Capture time
    await ClockCycles(dut.clk, random.randint(0, 2))
    dut.start_cap_time    <= random.randint(0, int(SYNC_PERIOD_DEF/2))

    dut.fifo_rd_busy      <= 1

    # Change parameters of the refreshing timer
    dut.refresh_en        <= 0
    await ClockCycles(dut.clk, random.randint(1, SYNC_PERIOD_DEF))

    dut.tr_en_period      <= int(TR_EN_PERIOD_DEF/2)
    dut.tr_en_on_time     <= int(TR_EN_ON_TIME_DEF/2)
    dut.refresh_en        <= 1

    dut.fifo_rd_busy      <= 1

    # Some delay
    await ClockCycles(dut.clk, random.randint(1, SYNC_PERIOD_DEF))

    dut.fifo_rd_busy      <= 0

    # Some delay
    await ClockCycles(dut.clk, random.randint(1, 2*SYNC_PERIOD_DEF))

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture = 1
    await RisingEdge(dut.clk)
    dut.start_capture = 0

    # Some long delay
    await ClockCycles(dut.clk, random.randint(2*SYNC_PERIOD_DEF, 3*SYNC_PERIOD_DEF))

    ##################### Repeat Start capture ##################### 

    await RisingEdge(dut.clk)
    # Data acquisition time = 110 uS
    dut.afe_data_acq_time <= 1100
    # Capture delay 12 uS
    dut.capture_delay     <= 120
    # AFE clock on time before wake up = 22 uS
    dut.afe_clk_on_time   <= 220


    # Wait one sync cycle
    await ClockCycles(dut.clk, SYNC_PERIOD_DEF)

    # Some delay
    await ClockCycles(dut.clk, random.randint(0, SYNC_PERIOD_DEF))

    # Start capture
    await RisingEdge(dut.clk)
    dut.start_capture = 1
    await RisingEdge(dut.clk)
    dut.start_capture = 0

    # Some long delay
    await ClockCycles(dut.clk, random.randint(2*SYNC_PERIOD_DEF, 3*SYNC_PERIOD_DEF))

    print('Finished')

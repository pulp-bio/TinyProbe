"""Functional test for the waveform_generator FSM wrapper."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, ReadOnly


async def reset_dut(dut):
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def fsm_counts_complete_shots_and_applies_control_modes(dut):
    """Check the remaining-shot counter, final transition, and output modes."""

    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.sync_period.value = 300
    dut.start_cap_time.value = 0
    dut.capture_delay.value = 0
    dut.start_capture.value = 0
    dut.n_shots.value = 4
    dut.fifo_rd_busy.value = 0
    dut.tx_wake_up_time.value = 100
    dut.tx_sleep_time.value = 32
    dut.refresh_en.value = 0
    dut.tr_en_period.value = 200
    dut.tr_en_on_time.value = 200
    dut.afe_wake_up_time.value = 30
    dut.afe_clk_on_time.value = 200
    dut.afe_data_acq_time.value = 100

    await reset_dut(dut)
    await ReadOnly()
    assert int(dut.dut.state_q.value) == 0, "FSM did not reset into STATE_A"
    assert int(dut.afe_fast_pdn.value) == 1, "active-low AFE reset value is wrong"

    # Start a four-shot sequence. The wrapper must enter acquisition and load
    # its remaining-shot counter without consuming a period_done event.
    await FallingEdge(dut.clk)
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    dut.start_capture.value = 0
    await ReadOnly()

    assert int(dut.dut.state_q.value) == 1, (
        "FSM did not enter SHOT_ACQUISITION when the sequence started"
    )
    assert int(dut.dut.shot_count_q.value) == 4, (
        "remaining-shot counter was not loaded with n_shots_i"
    )

    rollover_count = 0

    # At a falling edge, waveform_q, waveform_next, and control_word are the
    # values consumed by the next rising edge. Check every output's 2-bit mode.
    for _ in range(1600):
        await FallingEdge(dut.clk)
        await ReadOnly()
        previous_state = int(dut.dut.state_q.value)
        previous_q = int(dut.dut.waveform_q.value)
        next_waveform = int(dut.dut.waveform_next.value)
        control_word = int(dut.dut.control_word.value)
        period_done_before_edge = int(dut.period_done.value)

        expected_q = previous_q
        for output_index in range(11):
            mode = (control_word >> (2 * output_index)) & 0b11
            output_mask = 1 << output_index

            if mode == 0b00:  # HOLD
                pass
            elif mode == 0b01:  # FORCE_0
                expected_q &= ~output_mask
            elif mode == 0b10:  # FORCE_1
                expected_q |= output_mask
            else:  # FOLLOW_WAVE
                if next_waveform & output_mask:
                    expected_q |= output_mask
                else:
                    expected_q &= ~output_mask

        await RisingEdge(dut.clk)
        await ReadOnly()

        assert int(dut.dut.waveform_q.value) == expected_q, (
            "waveform_q did not apply the per-output control modes"
        )
        

        if period_done_before_edge:
            rollover_count += 1
            expected_count = 4 - rollover_count

            assert int(dut.dut.shot_count_q.value) == expected_count, (
                "remaining-shot counter did not decrement exactly once"
            )

            if expected_count > 0:
                assert previous_state == 1
                assert int(dut.dut.state_q.value) == 1, (
                    "FSM left SHOT_ACQUISITION before the final shot"
                )
            else:
                assert int(dut.dut.state_q.value) == 2, (
                    "FSM did not enter RESET after the final shot"
                )
                break

    assert rollover_count == 4, "did not observe all four completed shots"

    # RESET is now the stopped/waiting state after a completed sequence. Use a
    # scaled 3 us delay (300 cycles at 100 MHz) to represent the long MCU idle
    # period without making the simulation process 300 million clock edges.
    await ClockCycles(dut.clk, 300)
    await ReadOnly()
    assert int(dut.dut.state_q.value) == 2, (
        "FSM left RESET during the MCU idle period"
    )

    assert int(dut.dut.shot_count_q.value) == 0, (
        "remaining-shot counter was not cleared in RESET"
    )
    assert int(dut.fifo_start_capture.value) == 0
    assert int(dut.fifo_rst.value) == 0
    assert int(dut.fifo_wr_en.value) == 0
    assert int(dut.tx_bf_sync.value) == 0
    assert int(dut.tx_clk_buf_en.value) == 0
    assert int(dut.tx_sync_buf_en.value) == 0
    assert int(dut.afe_tx_trig.value) == 0
    assert int(dut.afe_tx_trig_buf_en.value) == 0
    assert int(dut.afe_clk_buf_en.value) == 0
    assert int(dut.afe_fast_pdn.value) == 1

    # A new rising edge reloads the shot counter and returns through
    # INITIAL_SETUP for one complete cycle before acquisition restarts.
    await FallingEdge(dut.clk)
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    dut.start_capture.value = 0
    await ReadOnly()
    assert int(dut.dut.state_q.value) == 0, (
        "FSM did not enter INITIAL_SETUP after the new start event"
    )
    assert int(dut.dut.shot_count_q.value) == 4, (
        "remaining-shot counter was not reloaded for the new sequence"
    )

    await RisingEdge(dut.clk)
    await ReadOnly()
    assert int(dut.dut.state_q.value) == 1, (
        "FSM did not restart acquisition after INITIAL_SETUP"
    )

    # Let the complete second sequence run. It must count another four shots
    # and return to RESET, demonstrating both wake-up and repeat operation.
    second_rollover_count = 0
    for _ in range(1600):
        await FallingEdge(dut.clk)
        await ReadOnly()
        period_done_before_edge = int(dut.period_done.value)

        await RisingEdge(dut.clk)
        await ReadOnly()

        if period_done_before_edge:
            second_rollover_count += 1
            expected_count = 4 - second_rollover_count
            assert int(dut.dut.shot_count_q.value) == expected_count, (
                "second sequence remaining-shot counter is incorrect"
            )

            if expected_count == 0:
                assert int(dut.dut.state_q.value) == 2, (
                    "FSM did not return to RESET after the second sequence"
                )
                break

    assert second_rollover_count == 4, (
        "second sequence did not complete all four shots"
    )

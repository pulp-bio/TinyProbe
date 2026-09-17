import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly, RisingEdge


def pack_frame(a, b):
    return (b << 10) | a


def complete_bytes(frames):
    bits = "".join(f"{word:020b}" for word in frames)
    complete_bit_count = len(bits) - len(bits) % 8
    return [
        int(bits[index:index + 8], 2)
        for index in range(0, complete_bit_count, 8)
    ]


async def initialize(dut, word_count):
    cocotb.start_soon(Clock(dut.afe_clk, 10, unit="ns").start())
    cocotb.start_soon(Clock(dut.core_clk, 17, unit="ns").start())
    dut.rst_n.value = 0
    dut.write_enable.value = 0
    dut.write_data.value = 0
    dut.read_count.value = word_count
    dut.start.value = 0
    dut.ready.value = 0
    await ClockCycles(dut.afe_clk, 5)
    await FallingEdge(dut.afe_clk)
    dut.rst_n.value = 1
    await ClockCycles(dut.core_clk, 3)


async def start_reader(dut):
    await FallingEdge(dut.core_clk)
    dut.start.value = 1
    await RisingEdge(dut.core_clk)
    await FallingEdge(dut.core_clk)
    dut.start.value = 0


async def write_words(dut, words, gaps):
    for word, gap in zip(words, gaps):
        await ClockCycles(dut.afe_clk, gap)
        while True:
            await FallingEdge(dut.afe_clk)
            if not int(dut.full.value):
                break
        dut.write_data.value = word
        dut.write_enable.value = 1
        await RisingEdge(dut.afe_clk)
        await FallingEdge(dut.afe_clk)
        dut.write_enable.value = 0


async def receive_bytes(dut, expected_count, ready_for_cycle, timeout=1000):
    observed = []
    for cycle in range(timeout):
        await FallingEdge(dut.core_clk)
        ready = int(ready_for_cycle(cycle))
        dut.ready.value = ready
        await RisingEdge(dut.core_clk)
        await ReadOnly()

        assert 0 <= int(dut.reshaper.state_q.value) <= 5
        if int(dut.valid.value) and ready:
            observed.append(int(dut.data.value))
        if len(observed) == expected_count:
            return observed
    raise AssertionError(
        f"reshaper stalled: got {len(observed)}/{expected_count} bytes; "
        f"state={int(dut.reshaper.state_q.value)}, "
        f"read_count={int(dut.reshaper.rd_cnt_q.value)}, "
        f"empty={int(dut.empty.value)}"
    )


async def assert_returns_idle(dut):
    for _ in range(20):
        await RisingEdge(dut.core_clk)
        await ReadOnly()
        if not int(dut.busy.value):
            return
    raise AssertionError("reshaper did not return to idle")


@cocotb.test()
async def registered_cdc_refill_does_not_repeat_previous_word(dut):
    words = [
        pack_frame(0, 0),
        pack_frame(48, 48),
        pack_frame(0x3FF, 0x3FF),
    ]
    expected = complete_bytes(words)
    await initialize(dut, len(words))
    await start_reader(dut)

    # Start empty, then leave a long gap before the final word. This forces
    # WAIT_NEXT_WORD and verifies the registered CDC output is not consumed
    # until the newly read word is available.
    writer = cocotb.start_soon(write_words(dut, words, [2, 1, 20]))
    observed = await receive_bytes(dut, len(expected), lambda _: True)
    await writer

    assert observed == expected, (
        f"refill repeated or corrupted a word: observed={observed}, "
        f"expected={expected}"
    )
    await assert_returns_idle(dut)


@cocotb.test()
async def full_buffer_and_output_backpressure_preserve_every_bit(dut):
    # Verify that backpressure does not lose or corrupt data while the CDC
    # buffer is full and the output is temporarily unable to accept bytes.
    words = [
        pack_frame(0x012, 0x155),
        pack_frame(0x123, 0x2AA),
        pack_frame(0x3AB, 0x001),
        pack_frame(48, 0x3FF),
    ]
    expected = complete_bytes(words)
    await initialize(dut, len(words))

    # Fill both CDC entries before starting the reader. The producer must then
    # wait for synchronized read-pointer feedback before writing more data.
    writer = cocotb.start_soon(write_words(dut, words, [0, 0, 0, 3]))
    await ClockCycles(dut.core_clk, 8)
    await start_reader(dut)

    rng = random.Random(0x48)
    observed = await receive_bytes(
        dut,
        len(expected),
        lambda cycle: cycle >= 12 and rng.randrange(4) != 0,
    )
    await writer

    assert observed == expected, (
        f"backpressure corrupted stream: observed={observed}, expected={expected}"
    )
    await assert_returns_idle(dut)

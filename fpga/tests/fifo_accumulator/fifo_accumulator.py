import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly, RisingEdge


def pack(a, b):
    return (b << 10) | a


def unpack_sum(word):
    return word & 0x3FFF, (word >> 14) & 0x3FFF


async def start_shot(dut, first):
    await FallingEdge(dut.clk)
    dut.first_shot.value = first
    dut.start_capture.value = 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.start_capture.value = 0
    await ClockCycles(dut.clk, 4)


async def send(dut, samples):
    for a, b in samples:
        await FallingEdge(dut.clk)
        dut.data_in.value = pack(a, b)
        dut.wr_en.value = 1
        await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.wr_en.value = 0


async def wait_done(dut, timeout=50):
    for _ in range(timeout):
        await RisingEdge(dut.clk)
        await ReadOnly()
        if int(dut.done.value):
            return
    raise AssertionError("shot accumulation did not complete")


@cocotb.test()
async def first_shot_writes_and_second_shot_accumulates(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst_n.value = 0
    dut.fifo_reset.value = 1
    dut.first_shot.value = 0
    dut.start_capture.value = 0
    dut.wr_en.value = 0
    dut.rd_en.value = 0
    dut.data_in.value = 0
    await ClockCycles(dut.clk, 3)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1
    dut.fifo_reset.value = 0

    shot1 = [(10, 20), (30, 40), (50, 60)]
    shot2 = [(1, 2), (3, 4), (5, 6)]
    await start_shot(dut, True)
    await send(dut, shot1)
    await wait_done(dut)

    await start_shot(dut, False)
    await send(dut, shot2)
    await wait_done(dut)

    observed = []
    for _ in range(3):
        await FallingEdge(dut.clk)
        dut.rd_en.value = 1
        await RisingEdge(dut.clk)
        await ReadOnly()
        got_word = None
        if int(dut.dvld.value):
            got_word = int(dut.data_out.value)

        await FallingEdge(dut.clk)
        dut.rd_en.value = 0

        if got_word is None:
            for _ in range(10):
                await RisingEdge(dut.clk)
                await ReadOnly()
                if int(dut.dvld.value):
                    got_word = int(dut.data_out.value)
                    break

        if got_word is None:
            raise AssertionError("FIFO read did not produce DVLD")
        observed.append(unpack_sum(got_word))

    expected = [(a+c, b+d) for (a, b), (c, d) in zip(shot1, shot2)]
    assert observed == expected, f"observed={observed}, expected={expected}"

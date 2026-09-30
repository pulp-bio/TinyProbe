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

import pytest

from tipy.control.methods import Method, TinyprobeMethods
from tipy.hardware.fpga.hal import HAL_FPGA
from tipy.runtime.session import DeviceMemory, Session, SessionHardware
from tipy.transport.implementations.dummy import TransportDummy


class TestDeviceMemory:
    def test_init(self):
        mem = DeviceMemory("test_device")
        assert mem.memory == {}

    def test_read_uninitialized(self):
        mem = DeviceMemory("test_device")
        value = mem.read(register_address=0x10, offset=0, width=8, reset_value=0x5)
        assert value == 0x5
        assert 0x10 in mem.memory
        assert mem.memory[0x10].bits[0] == 0x5
        assert not mem.memory[0x10].changed

    def test_write(self):
        mem = DeviceMemory("test_device")
        mem.write(register_address=0x10, offset=4, width=8, value=0x3)
        assert mem.memory[0x10].changed
        assert mem.memory[0x10].bits[4] == 0x3

    def test_pull_returns_changed_registers(self):
        mem = DeviceMemory("test_device")
        mem.write(register_address=0x10, offset=0, width=8, value=0x1)
        mem.write(register_address=0x10, offset=4, width=8, value=0x2)
        mem.write(register_address=0x20, offset=0, width=8, value=0x3)

        result = mem.pull()

        # 0x1 << 0 | 0x2 << 4 = 0x21
        assert result[0x10] == 0x21
        assert result[0x20] == 0x3
        assert len(result) == 2

    def test_pull_clears_dirty_flags(self):
        mem = DeviceMemory("test_device")
        mem.write(register_address=0x10, offset=0, width=8, value=0x1)

        first_pull = mem.pull()
        assert 0x10 in first_pull

        second_pull = mem.pull()
        assert 0x10 not in second_pull

    def test_pull_returns_sorted_by_address(self):
        mem = DeviceMemory("test_device")
        mem.write(register_address=0x30, offset=0, width=8, value=0x1)
        mem.write(register_address=0x10, offset=0, width=8, value=0x2)
        mem.write(register_address=0x20, offset=0, width=8, value=0x3)

        result = mem.pull()
        addresses = list(result.keys())

        assert addresses == [0x10, 0x20, 0x30]

    def test_push(self):
        mem = DeviceMemory("test_device")
        memory_state = {
            0x10: {0: 0x1, 4: 0x2},
            0x20: {0: 0x3},
        }

        mem.push(memory_state)

        assert 0x10 in mem.memory
        assert 0x20 in mem.memory
        assert mem.memory[0x10].changed
        assert mem.memory[0x10].bits == {0: 0x1, 4: 0x2}

    def test_reset(self):
        mem = DeviceMemory("test_device")
        mem.write(register_address=0x10, offset=0, width=8, value=0x1)

        mem.reset()

        assert mem.memory == {}


class TestSession:
    def make_transports(self):
        from tipy.transport.transport import TransportEndpoint

        transport_cmd = TransportDummy(TinyprobeMethods().methods)
        transport_cmd.set_device(
            TransportEndpoint(device="test-cmd", description="Test Command")
        )

        transport_bulk = TransportDummy()
        transport_bulk.set_device(
            TransportEndpoint(device="test-bulk", description="Test Bulk")
        )

        return transport_cmd, transport_bulk

    def test_init(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        assert session.transport_command is transport_cmd
        assert session.transport_bulk is transport_bulk
        assert isinstance(session.mem["fpga"], DeviceMemory)
        assert isinstance(session.mem["afe_glb"], DeviceMemory)
        assert isinstance(session.mem["afe_dtgc"], DeviceMemory)
        assert isinstance(session.mem["tx"], DeviceMemory)
        assert isinstance(session.hw, SessionHardware)
        assert isinstance(session.hw.fpga, HAL_FPGA)
        assert session.hw.fpga.regmap._interface is session.mem["fpga"]
        assert session.hw.memories is session.mem

    def test_append_and_collect_methods(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        method1 = Method(method="test.method1")
        method2 = Method(method="test.method2")

        session.append_method(method1)
        session.append_method(method2)

        collected = session.collect()
        assert len(collected) == 2
        assert collected[0] is method1
        assert collected[1] is method2

        # Should be cleared after collect
        collected_again = session.collect()
        assert len(collected_again) == 0

    def test_pull_fpga_only(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)
        # HAL initialization touches every register, we clear that here
        _ = session.mem["fpga"].pull()

        session.mem["fpga"].write(register_address=0x10, offset=0, width=8, value=0x5)

        changes = session.pull()

        assert "fpga" in changes
        assert changes["fpga"][0x10] == 0x5

        # Check that controlspi was called
        collected = session.collect()
        controlspi_calls = [m for m in collected if m.method == "controlspi"]
        assert len(controlspi_calls) == 1
        assert controlspi_calls[0].params is not None
        assert (
            controlspi_calls[0].params["domain"]
            == session._methods.Spidomain.FPGA.value
        )

        # Check that writefpga was called
        writefpga_calls = [m for m in collected if m.method == "writefpga"]
        assert len(writefpga_calls) == 1
        assert writefpga_calls[0].params is not None
        assert writefpga_calls[0].params["address"] == 0x10
        assert writefpga_calls[0].params["value"] == 0x5

    def test_pull_afe_glb_and_dtgc(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)
        # HAL initialization touches every register, we clear that here
        _ = session.mem["fpga"].pull()

        session.mem["afe_glb"].write(
            register_address=0x20, offset=0, width=8, value=0x3
        )
        session.mem["afe_dtgc"].write(
            register_address=0x30, offset=0, width=8, value=0x7
        )

        changes = session.pull()

        assert "afe_glb" in changes
        assert "afe_dtgc" in changes
        assert changes["afe_glb"][0x20] == 0x3
        assert changes["afe_dtgc"][0x30] == 0x7

        collected = session.collect()
        controlspi_calls = [m for m in collected if m.method == "controlspi"]
        assert len(controlspi_calls) == 1
        assert controlspi_calls[0].params is not None
        assert (
            controlspi_calls[0].params["domain"] == session._methods.Spidomain.AFE.value
        )

        writeafe_calls = [m for m in collected if m.method == "writeafe"]
        assert len(writeafe_calls) == 2

    def test_pull_tx(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)
        # HAL initialization touches every register, we clear that here
        _ = session.mem["fpga"].pull()

        session.mem["tx"].write(register_address=0x40, offset=0, width=8, value=0x9)

        changes = session.pull()

        assert "tx" in changes
        assert changes["tx"][0x40] == 0x9

        collected = session.collect()
        controlspi_calls = [m for m in collected if m.method == "controlspi"]
        assert len(controlspi_calls) == 1
        assert controlspi_calls[0].params is not None
        assert (
            controlspi_calls[0].params["domain"] == session._methods.Spidomain.TX.value
        )

        writetx_calls = [m for m in collected if m.method == "writetx"]
        assert len(writetx_calls) == 1
        assert writetx_calls[0].params is not None
        assert writetx_calls[0].params["address"] == 0x40
        assert writetx_calls[0].params["value"] == 0x9

    def test_pull_multiple_devices_with_mux(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        session.mem["fpga"].write(register_address=0x10, offset=0, width=8, value=0x1)
        session.mem["afe_glb"].write(
            register_address=0x20, offset=0, width=8, value=0x2
        )
        session.mem["tx"].write(register_address=0x30, offset=0, width=8, value=0x3)

        changes = session.pull()

        assert "fpga" in changes
        assert "afe_glb" in changes
        assert "tx" in changes

        collected = session.collect()
        controlspi_calls = [m for m in collected if m.method == "controlspi"]
        # Should switch mux 3 times: FPGA, AFE, TX
        assert len(controlspi_calls) == 3

    def test_pull_avoids_redundant_mux_switches(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        # First pull - sets mux to FPGA
        session.mem["fpga"].write(register_address=0x10, offset=0, width=8, value=0x1)
        session.pull()
        session.collect()

        # Second pull - should not switch mux again
        session.mem["fpga"].write(register_address=0x10, offset=0, width=8, value=0x2)
        session.pull()
        collected = session.collect()

        controlspi_calls = [m for m in collected if m.method == "controlspi"]
        assert len(controlspi_calls) == 0

    def test_execute_sends_methods(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        # Use actual methods that exist in TinyprobeMethods
        methods = [
            Method(method="delayms", params={"delay": 10}),
            Method(method="delayms", params={"delay": 20}),
        ]

        session.execute(methods)

        # Should have sent batch request
        assert len(session.command_client.batch_requests) == 2

    def test_execute_empty_list_does_nothing(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        session.execute([])

        assert len(session.command_client.batch_requests) == 0

    def test_batch_mode_accumulates_methods(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        # Use actual methods that exist in TinyprobeMethods
        methods1 = [Method(method="delayms", params={"delay": 10})]
        methods2 = [Method(method="delayms", params={"delay": 20})]

        with session.batch():
            session.execute(methods1)
            session.execute(methods2)

        # Should have accumulated and sent as one batch
        assert len(session.command_client.batch_requests) == 2

    def test_batch_mode_sends_nothing_if_exception(self):
        transport_cmd, transport_bulk = self.make_transports()
        session = Session(transport_cmd, transport_bulk)

        # Use actual methods that exist in TinyprobeMethods
        methods = [Method(method="delayms", params={"delay": 10})]

        with pytest.raises(ValueError), session.batch():
            session.execute(methods)
            raise ValueError("Test exception")

        # Should not have sent anything
        assert len(session.command_client.batch_requests) == 0


class TestSessionHardware:
    def test_init_binds_fpga_hal_to_memory(self):
        memories = {
            "fpga": DeviceMemory("fpga"),
            "afe_glb": DeviceMemory("afe_glb"),
        }
        hw = SessionHardware(memories)

        assert hw.memories is memories
        assert isinstance(hw.fpga, HAL_FPGA)
        assert hw.fpga.regmap._interface is memories["fpga"]

    def test_init_requires_fpga_memory(self):
        with pytest.raises(ValueError, match="FPGA memory is required"):
            SessionHardware({"tx": DeviceMemory("tx")})

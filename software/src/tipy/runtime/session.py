"""
Copyright (C) 2026 ETH Zurich. All rights reserved.

Authors:
    - Sergei Vostrikov, ETH Zurich
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

import logging
from dataclasses import dataclass

from tipy.transport.transport import TransportProtocol

from ..control.bulk import BulkReceiver
from ..control.command import CommandClient
from ..control.methods import Method, TinyprobeMethods
from ..control.rpc import RPCResponse
from ..hardware.fpga.hal import HAL_FPGA
from ..hardware.regmap_base import RegisterMapInterface


class DeviceMemory(RegisterMapInterface):
    @dataclass
    class Register:
        changed: bool
        bits: dict[int, int]

    def __init__(self, name: str):
        self.log = logging.getLogger().getChild("mem").getChild(name)
        self.memory: dict[
            int, DeviceMemory.Register
        ] = {}  # In form reg_addr: (changed, {bit_addr: bit_value})

    def read(
        self, register_address: int, offset: int, width: int, reset_value: int
    ) -> int:
        if register_address not in self.memory:
            self.memory[register_address] = self.Register(changed=False, bits={})

        if offset not in self.memory[register_address].bits:
            self.memory[register_address].bits[offset] = reset_value

        return self.memory[register_address].bits[offset]

    def write(self, register_address: int, offset: int, width: int, value: int) -> None:
        if register_address not in self.memory:
            self.memory[register_address] = self.Register(changed=True, bits={})

        self.memory[register_address].changed = True
        self.memory[register_address].bits[offset] = value

    def pull(self) -> dict[int, int]:
        changed_registers = {}
        for register_address, register in self.memory.items():
            if register.changed:
                changed_registers[register_address] = register.bits

        result = {
            address: sum(value << offset for offset, value in register.items())
            for address, register in changed_registers.items()
        }

        for register in self.memory.values():
            register.changed = False

        return dict(sorted(result.items()))

    def push(self, memory: dict[int, dict[int, int]]) -> None:
        self.memory = {}
        for address, register in memory.items():
            self.memory[address] = self.Register(changed=True, bits=register)

    def reset(self) -> None:
        self.memory = {}


class SessionHardware:
    def __init__(self, memories: dict[str, DeviceMemory]):
        if "fpga" not in memories:
            raise ValueError("FPGA memory is required for SessionHardware")
        self.memories = memories

        self.fpga = HAL_FPGA(memories["fpga"])
        # FIXME: Add AFE and TX HALs here when they are implemented


class Session:
    def __init__(
        self,
        transport_command: TransportProtocol,
        transport_bulk: TransportProtocol,
    ):
        self.transport_command = transport_command
        self.transport_bulk = transport_bulk

        self.mem = {
            "fpga": DeviceMemory("fpga"),
            "afe_glb": DeviceMemory("afe_glb"),
            "afe_dtgc": DeviceMemory("afe_dtgc"),
            "tx": DeviceMemory("tx"),
        }
        self.hw = SessionHardware(self.mem)

        self.command_client = CommandClient(self.transport_command)
        self.bulk_receiver = BulkReceiver(self.transport_bulk)

        self._queue: list[Method] = []
        self._methods = TinyprobeMethods(self.append_method)
        self._mux_position: TinyprobeMethods.Spidomain | None = None

        self._batch_mode = False
        self._batch_accumulated: list[Method] = []

        self._request_file = open("session_requests.log", "w")

    def append_method(self, method: Method) -> None:
        if self._batch_mode:
            self._batch_accumulated.append(method)
            logging.debug(f"Appended method to batch: {method.method} {method.params}")
            return

        self._queue.append(method)

    def collect(self) -> list[Method]:
        result = self._queue.copy()
        self._queue.clear()
        return result

    def _controlspi(self, target: TinyprobeMethods.Spidomain) -> None:
        if self._mux_position != target:
            self._methods.controlspi(target)
            self._mux_position = target

    def pull(self) -> dict[str, dict[int, int]]:
        changes: dict[str, dict[int, int]] = {}

        if "fpga" in self.mem:
            fpga_regs = self.mem["fpga"].pull()
            if fpga_regs:
                changes["fpga"] = fpga_regs
                self._controlspi(self._methods.Spidomain.FPGA)
                for addr, val in fpga_regs.items():
                    self._methods.writefpga(addr, val)

        if "afe_glb" in self.mem and "afe_dtgc" in self.mem:
            afe_glb = self.mem["afe_glb"].pull()
            if afe_glb:
                changes["afe_glb"] = afe_glb
            afe_dtgc = self.mem["afe_dtgc"].pull()
            if afe_dtgc:
                changes["afe_dtgc"] = afe_dtgc
            if afe_glb or afe_dtgc:
                self._controlspi(self._methods.Spidomain.AFE)
                for addr, val in afe_glb.items():
                    self._methods.writeafe(False, addr, val)
                for addr, val in afe_dtgc.items():
                    self._methods.writeafe(True, addr, val)

        if "tx" in self.mem:
            tx_regs = self.mem["tx"].pull()
            if tx_regs:
                changes["tx"] = tx_regs
                self._controlspi(self._methods.Spidomain.TX)
                for addr, val in tx_regs.items():
                    self._methods.writetx(addr, val)

        return changes

    def batch(self):
        """Context manager that accumulates all execute() calls and sends them as one batch.

        Usage::

            with session.batch():
                protocol_a.execute_acquire()
                protocol_b.execute_acquire()
        """

        session = self

        class _SessionBatch:
            def __enter__(self):
                session._batch_mode = True
                session._batch_accumulated = []
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                session._batch_mode = False
                accumulated = session._batch_accumulated
                session._batch_accumulated = []
                logging.debug(f"Executing batch of {len(accumulated)} methods")
                if exc_type is None and accumulated:
                    with session.command_client.batch():
                        for method in accumulated:
                            session.command_client.request(method)
                            session._request_file.write(
                                f"{method.method} {method.params}\n"
                            )
                        session._request_file.flush()
                return False

        return _SessionBatch()

    def execute(self, methods: list[Method]) -> None:
        if not methods:
            return

        if self._batch_mode:
            self._batch_accumulated.extend(methods)
            return

        with self.command_client.batch():
            for method in methods:
                self.command_client.request(method)
                self._request_file.write(f"{method.method} {method.params}\n")
            self._request_file.flush()

    def print_responses(
        self, errors_only: bool = False, title: str = "Command Log"
    ) -> None:
        RPCResponse.print_table(
            self.command_client.batch_requests,
            self.command_client.batch_responses,
            self.command_client.batch_response_times,
            errors_only=errors_only,
            title=title,
        )

    def receive(self):
        """Context manager that starts and stops bulk data reception.

        Usage::

            with session.receive():
                protocol.execute_acquire()
        """

        session = self

        class _SessionReceive:
            def __enter__(self):
                session.bulk_receiver.start()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                session.bulk_receiver.stop()
                return False

        return _SessionReceive()

    def get_received_data(self) -> tuple[list[float], list[bytes]]:
        return self.bulk_receiver.times, self.bulk_receiver.buffer

    def __del__(self):
        self._request_file.close()

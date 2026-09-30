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

import time
from typing import Self

from tipy.control.methods import TinyprobeMethods
from tipy.runtime.session import Session
from tipy.transport.implementations.dummy import TransportDummy
from tipy.transport.transport import TransportEndpoint, TransportProtocol


class PacketTransport(TransportProtocol):
    """A finite bulk-data transport for this local demo."""

    def __init__(self, packets: list[bytes]):
        self._open = False
        self._packets = packets

    @staticmethod
    def get_available() -> list[TransportEndpoint]:
        return []

    def set_device(self, device: TransportEndpoint) -> None:
        pass

    @property
    def open(self) -> bool:
        return self._open

    def __enter__(self) -> Self:
        self._open = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._open = False

    def _send(self, data: bytes) -> None:
        raise NotImplementedError("This demo transport only receives bulk data")

    def _receive(self, bufsize: int = 1024) -> bytes:
        if self._packets:
            return self._packets.pop(0)
        raise TimeoutError("No more demo packets")


command_transport = TransportDummy(TinyprobeMethods().methods)
command_transport.set_device(TransportEndpoint("demo-command", "Dummy command"))
bulk_transport = PacketTransport([b"first packet", b"second packet", b"third packet"])
session = Session(command_transport, bulk_transport)

# Stage a register change.  pull() creates the required SPI-mux and FPGA-write
# commands; execute() sends them through the dummy command transport.
session.mem["fpga"].write(register_address=0x10, offset=0, width=8, value=0x05)
changes = session.pull()
methods = session.collect()
session.execute(methods)
print("Register changes:", changes)
print("Commands sent:", [method.method for method in methods])

with session.receive():
    deadline = time.monotonic() + 1.0
    while len(session.get_received_data()[1]) < 3 and time.monotonic() < deadline:
        time.sleep(0.01)

times, packets = session.get_received_data()
print(f"Received {len(packets)} packets")
for timestamp, packet in zip(times, packets):
    print(f"  {timestamp:.3f}: {packet.decode()}")

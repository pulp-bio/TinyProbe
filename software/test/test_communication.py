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

from tipy.transport.implementations.dummy import (
    TransportDummy,
    TransportEndpoint,
)
from tipy.transport.implementations.udp import (
    DEFAULT_PORT,
    TransportUDP,
)
from tipy.transport.transport import TransportError


class TestCommunication:
    # TODO: Add tests for CommunicationInterfaceWiFi6 (Requires a test server or mock socket)
    def test_dummy_interface_open(self):
        interface = TransportDummy()
        device = TransportEndpoint(device="dummy_device", description="Dummy Device")

        interface.set_device(device)

        assert not interface.open

        with interface as comm:
            assert comm.open

        assert not interface.open


class DummyDatagramSocket:
    def __init__(self):
        self._closed = False
        self.timeout = None
        self.bound_to = None
        self.last_sent = b""

    def settimeout(self, timeout):
        self.timeout = timeout

    def bind(self, address):
        self.bound_to = address

    def fileno(self):
        return -1 if self._closed else 1

    def close(self):
        self._closed = True

    def send(self, data: bytes) -> int:
        self.last_sent = data
        return len(data)

    def recvfrom(self, bufsize: int):
        return (b"pong", self.bound_to)


class TestCommunicationUDP:
    def test_default_port_is_used_if_not_provided(self):
        interface = TransportUDP()
        device = TransportEndpoint(device="127.0.0.1", description="UDP Device")

        interface.set_device(device)

        assert interface.host == "127.0.0.1"
        assert interface.port == DEFAULT_PORT

    def test_udp_interface_open_send_receive(self, monkeypatch):
        sock = DummyDatagramSocket()
        monkeypatch.setattr(
            "tipy.transport.implementations.udp.socket.socket",
            lambda family, socktype: sock,
        )

        interface = TransportUDP(timeout=1.5)
        interface.set_device(
            TransportEndpoint(device="127.0.0.1:15000", description="UDP Device")
        )

        with interface as comm:
            assert comm.open
            assert sock.timeout == 1.5
            assert sock.bound_to == ("127.0.0.1", 15000)

            comm.send_raw(b"ping")
            assert sock.last_sent == b"ping"
            assert comm.receive_raw_exact(4) == b"pong"

        assert not interface.open

    def test_send_receive_without_open_raises(self):
        interface = TransportUDP()

        with pytest.raises(TransportError, match="not opened"):
            interface.send_frame(b"ping")

        with pytest.raises(TransportError, match="not opened"):
            interface.receive_frame()

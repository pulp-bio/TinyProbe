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

from typing import cast

import pytest

from tipy.control import methods_pb2
from tipy.control.command import CommandClient
from tipy.control.methods import MAX_COMMANDS_PER_PACKET, METHOD_NAMES, TinyprobeMethods
from tipy.control.rpc import (
    RPCResponse,
)
from tipy.transport.implementations.dummy import TransportDummy, TransportEndpoint
from tipy.transport.transport import TransportError, TransportProtocol

methods = TinyprobeMethods()


def make_server(
    max_packet_size: int = 1000,
    max_commands_per_packet: int = MAX_COMMANDS_PER_PACKET,
) -> tuple[CommandClient, TransportDummy]:
    device = TransportEndpoint(device="dummy_device", description="Dummy Device")
    interface = TransportDummy(methods.methods)
    interface.set_device(device)
    return (
        CommandClient(
            interface,
            max_packet_size=max_packet_size,
            max_commands_per_packet=max_commands_per_packet,
        ),
        interface,
    )


def command_names(frame: bytes) -> list[str]:
    request = methods_pb2.request()
    request.ParseFromString(TransportProtocol.unframe_payload(frame))
    return [cmd.WhichOneof("args") for cmd in request.cmd]


class TestRPCServer:
    def test_methods_are_descriptor_driven(self):
        descriptor = cast(object, methods_pb2.cmd.DESCRIPTOR)
        args_oneof = cast(
            object,
            descriptor.oneofs_by_name["args"],  # type: ignore
        )
        proto_methods = [field.name for field in args_oneof.fields]  # type: ignore

        assert list(METHOD_NAMES) == proto_methods
        assert methods.methods == proto_methods

    def test_command_client_default_command_limit_comes_from_methods(self):
        server, _ = make_server()

        assert server._max_commands_per_packet == MAX_COMMANDS_PER_PACKET

    def test_dummy_interface(self):
        cmds = [
            methods.controlpower(methods.Powerdomain.PLL_PWD, True),
            methods.delayns(1),
            methods.ping(),
            methods.setloglevel(methods.Loglevel.INFO),
            methods.delayms(1),
            methods.controlspi(methods.Spidomain.AFE),
            methods.triggershot(),
            methods.writeafe(False, 0x10, 0x1234),
            methods.writefpga(0x20, 0x12345678),
            methods.writetx(0x42, 0x5678),
        ]

        server, _ = make_server()

        assert server.methods == sorted(methods.methods)

        with server.batch():
            for cmd in cmds:
                server.request(cmd)

        requests = server.batch_requests
        responses = server.batch_responses

        assert requests == cmds
        assert len(responses) == len(cmds)
        assert all(isinstance(response, RPCResponse) for response in responses)
        assert all(response.ok for response in responses)

    def test_dynamic_methods_use_typed_defaults(self):
        server, interface = make_server()

        response = server.ping()

        assert response is not None
        assert response.ok
        cmd = interface._requests[-1].cmd[0]
        assert cmd.WhichOneof("args") == "ping"
        assert cmd.ping.probe_id == 1

    def test_dummy_interface_multiple_packet_batches_preserve_order(self):
        server, _ = make_server(max_packet_size=12)
        cmds = [methods.ping() for _ in range(12)]

        with server.batch():
            for cmd in cmds:
                server.request(cmd)

        assert server.batch_requests == cmds
        assert [response.method for response in server.batch_responses] == cmds

    def test_batch_packets_do_not_exceed_max_packet_size(self, monkeypatch):
        server, interface = make_server(max_packet_size=12)

        sent_packet_sizes: list[int] = []
        original_send = interface._send

        def record_send(data: bytes) -> None:
            sent_packet_sizes.append(len(data))
            original_send(data)

        monkeypatch.setattr(interface, "_send", record_send)

        with server.batch():
            server.request(methods.ping())
            server.request(methods.ping())
            server.request(methods.ping())

        assert sent_packet_sizes
        assert all(size <= server._max_packet_size for size in sent_packet_sizes)
        assert len(sent_packet_sizes) == 3

    def test_batch_packets_do_not_exceed_max_command_count(self, monkeypatch):
        server, interface = make_server(max_commands_per_packet=40)
        cmds = [methods.ping() for _ in range(41)]

        sent_command_counts: list[int] = []
        original_send = interface._send

        def record_send(data: bytes) -> None:
            sent_command_counts.append(len(command_names(data)))
            original_send(data)

        monkeypatch.setattr(interface, "_send", record_send)

        with server.batch():
            for cmd in cmds:
                server.request(cmd)

        assert sent_command_counts == [40, 1]
        assert server.batch_requests == cmds
        assert [response.method for response in server.batch_responses] == cmds

    def test_atomic_grouping(self, monkeypatch):
        server, interface = make_server(max_packet_size=100)

        sent_packets: list[bytes] = []
        original_send = interface._send

        def record_send(data: bytes) -> None:
            sent_packets.append(data)
            original_send(data)

        monkeypatch.setattr(interface, "_send", record_send)

        with server.batch():
            server.request(methods.ping())
            with server.atomic():
                server.request(methods.controlspi(methods.Spidomain.AFE))
                server.request(methods.writeafe(False, 0x10, 0x1234))
                server.request(methods.triggershot())
            server.request(methods.ping())

        packet_commands = [command_names(packet) for packet in sent_packets]

        assert len(server.batch_responses) == 5
        assert any(
            commands == ["ping", "controlspi", "writeafe", "triggershot", "ping"]
            or commands == ["controlspi", "writeafe", "triggershot"]
            for commands in packet_commands
        )

    def test_atomic_group_too_large(self):
        server, _ = make_server(max_packet_size=50)

        with (
            pytest.raises(ValueError, match="exceeds max_packet_size"),
            server.batch(),
            server.atomic(),
        ):
            for _ in range(10):
                server.request(methods.ping())

    def test_atomic_group_too_many_commands(self):
        server, _ = make_server(max_commands_per_packet=40)

        with (
            pytest.raises(ValueError, match="max_commands_per_packet"),
            server.batch(),
            server.atomic(),
        ):
            for _ in range(41):
                server.request(methods.ping())

    def test_invalid_max_commands_per_packet(self):
        device = TransportEndpoint(device="dummy_device", description="Dummy Device")
        interface = TransportDummy(methods.methods)
        interface.set_device(device)

        with pytest.raises(ValueError, match="at least 1"):
            CommandClient(interface, max_commands_per_packet=0)

    def test_atomic_requires_batch(self):
        server, _ = make_server()

        with pytest.raises(RuntimeError, match="inside a batch"), server.atomic():
            server.request(methods.ping())

    def test_unsupported_legacy_methods_are_removed(self):
        for name in ("enreplies", "setpowersave", "writespi", "custom"):
            assert not hasattr(methods, name)
            assert name not in methods.methods

    def test_frame_round_trip(self):
        payload = b"\x08\x00"
        frame = TransportProtocol.frame_payload(payload)

        assert frame == b"\xab\x0b\x00\x02" + payload
        assert TransportProtocol.unframe_payload(frame) == payload

    def test_bad_frames_raise_protocol_errors(self):
        with pytest.raises(TransportError, match="too short"):
            TransportProtocol.unframe_payload(b"\xab")

        with pytest.raises(TransportError, match="Invalid frame magic"):
            TransportProtocol.unframe_payload(b"\x00\x00\x00\x00")

        with pytest.raises(TransportError, match="length mismatch"):
            TransportProtocol.unframe_payload(b"\xab\x0b\x00\x02\x01")

    def test_receive_frame_reassembles_partial_reads(self):
        payload = b"\x08\x00"
        frame = TransportProtocol.frame_payload(payload)
        # Split so both the header and payload cross chunk boundaries.
        chunks = [frame[:1], frame[1:3], frame[3:5], frame[5:]]
        transport = _PartialReceiveTransport(chunks)

        assert transport.receive_frame() == payload


class _PartialReceiveTransport(TransportProtocol):
    """Byte transport that returns a framed stream as small _receive chunks."""

    def __init__(self, chunks: list[bytes]):
        self._chunks = list(chunks)
        self._open = True

    @staticmethod
    def get_available() -> list[TransportEndpoint]:
        return []

    def set_device(self, device: TransportEndpoint) -> None:
        return

    @property
    def open(self) -> bool:
        return self._open

    def __enter__(self):
        self._open = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._open = False

    def _send(self, data: bytes) -> None:
        return

    def _receive(self, bufsize: int = 1024) -> bytes:
        if not self._chunks:
            return b""
        chunk = self._chunks.pop(0)
        if len(chunk) > bufsize:
            self._chunks.insert(0, chunk[bufsize:])
            return chunk[:bufsize]
        return chunk

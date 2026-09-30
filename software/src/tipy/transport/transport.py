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

import struct
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

FRAME_MAGIC = b"\xab\x0b"
FRAME_HEADER = struct.Struct(">2sH")
FRAME_HEADER_SIZE = FRAME_HEADER.size
MAX_FRAME_PAYLOAD_SIZE = 0xFFFF


class TransportError(Exception):
    """Exception raised for transport errors"""


@dataclass(slots=True)
class TransportEndpoint:
    """Class representing a transport endpoint, e.g. a serial port or network address"""

    device: str
    description: str

    def __str__(self) -> str:
        return f"{self.device}: {self.description}"

    @staticmethod
    def from_str(s: str) -> "TransportEndpoint":
        parts = s.split(":", 1)
        device = parts[0]
        description = parts[1].strip() if len(parts) > 1 else ""
        return TransportEndpoint(device=device, description=description)


@runtime_checkable
class TransportProtocol(Protocol):
    """Protocol for transport interfaces"""

    @staticmethod
    def get_available() -> list[TransportEndpoint]: ...
    def set_device(self, device: TransportEndpoint) -> None: ...

    @property
    def open(self) -> bool: ...

    def __enter__(self) -> "TransportProtocol": ...  # noqa: PYI034
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...

    def _send(self, data: bytes) -> None: ...
    def _receive(self, bufsize: int = 1024) -> bytes: ...

    @staticmethod
    def frame_payload(payload: bytes) -> bytes:
        if len(payload) > MAX_FRAME_PAYLOAD_SIZE:
            raise TransportError(
                f"Payload length {len(payload)} exceeds maximum {MAX_FRAME_PAYLOAD_SIZE}"
            )

        return FRAME_HEADER.pack(FRAME_MAGIC, len(payload)) + payload

    @staticmethod
    def unframe_payload(frame: bytes) -> bytes:
        if len(frame) < FRAME_HEADER_SIZE:
            raise TransportError(
                f"Frame too short: got {len(frame)} bytes, expected at least {FRAME_HEADER_SIZE}"
            )

        magic, payload_length = FRAME_HEADER.unpack_from(frame)
        if magic != FRAME_MAGIC:
            raise TransportError(
                f"Invalid frame magic: got 0x{magic[0]:02X} 0x{magic[1]:02X}"
            )

        actual_length = len(frame) - FRAME_HEADER_SIZE
        if actual_length != payload_length:
            raise TransportError(
                f"Frame length mismatch: header says {payload_length}, got {actual_length}"
            )

        return frame[FRAME_HEADER_SIZE:]

    def receive_raw_upto(self, length: int) -> bytes:
        return self._receive(length)

    def receive_raw_exact(self, length: int) -> bytes:
        chunks: list[bytes] = []
        remaining = length

        while remaining > 0:
            chunk = self._receive(remaining)
            if not chunk:
                raise TransportError(
                    f"Connection closed while reading frame; {remaining} bytes missing"
                )
            chunks.append(chunk)
            remaining -= len(chunk)

        return b"".join(chunks)

    def receive_frame(self) -> bytes:
        header = self.receive_raw_exact(FRAME_HEADER_SIZE)
        magic, payload_length = FRAME_HEADER.unpack(header)
        if magic != FRAME_MAGIC:
            self.unframe_payload(header)
        payload = self.receive_raw_exact(payload_length)
        return payload

    def send_frame(self, payload: bytes) -> None:
        self._send(self.frame_payload(payload))

    def send_raw(self, payload: bytes) -> None:
        self._send(payload)

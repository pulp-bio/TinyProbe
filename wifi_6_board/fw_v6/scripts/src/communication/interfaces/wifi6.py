"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich

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

import socket

from ..communication import (
    CommunicationError,
    CommunicationDevice,
    CommunicationInterface,
)
from ...command.response import Response


DEFAULT_PORT = 50008


class CommunicationInterfaceWiFi6(CommunicationInterface):
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

        self.host: str = ""
        self.port: int = DEFAULT_PORT

        self.socket: socket.socket | None = None
        self.device: CommunicationDevice | None = None

    def get_available(self) -> list[CommunicationDevice]:
        # For WiFi6, we assume the device is always available via its IP address.
        return []

    def set_device(self, device: CommunicationDevice) -> None:
        self.device = device
        self.host = device.device.split(":")[0]
        self.port = (
            int(device.device.split(":")[1]) if ":" in device.device else DEFAULT_PORT
        )

    @property
    def open(self) -> bool:
        return self.socket is not None and self.socket.fileno() != -1

    def __enter__(self):
        if self.open:
            return self
        elif self.device is None:
            raise CommunicationError("No device set.")

        self.socket = socket.create_connection(
            (self.host, self.port), timeout=self.timeout
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.open:
            return
        elif self.socket:
            self.socket.close()
            self.socket = None

    def _send_bytes(self, data: bytes) -> None:
        if not self.open or self.socket is None:
            raise CommunicationError("Connection is not opened.")

        self.socket.sendall(data)

    def _receive_responses(self) -> list[Response]:
        if not self.open or self.socket is None:
            raise CommunicationError("Connection is not opened.")

        return Response.from_socket(self.socket)

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

import socket

from ...tools.mdns import get_devices
from ..transport import (
    TransportEndpoint,
    TransportError,
    TransportProtocol,
)

DEFAULT_PORT = 50007


class TransportUDP(TransportProtocol):
    """Transport over UDP"""

    def __init__(self, timeout: float = 1.0):
        """Initialize the TransportUDP

        Arguments:
            timeout (float): Socket timeout in seconds
        """

        self.timeout = timeout

        self.host: str = "0.0.0.0"
        self.port: int = DEFAULT_PORT

        self.socket: socket.socket | None = None
        self.device: TransportEndpoint | None = TransportEndpoint(
            self.host + ":" + str(self.port), "Local"
        )

    @staticmethod
    def get_available() -> list[TransportEndpoint]:
        devices = get_devices()
        if devices is None:
            return []

        return [
            TransportEndpoint(
                device=address,
                description=f"Tinyprobe device at {address}",
            )
            for address in devices.parsed_addresses()
        ]

    def set_device(self, device: TransportEndpoint) -> None:
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
            raise TransportError("No device set.")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.socket.bind((self.host, self.port))
        except TimeoutError:
            raise TransportError(
                f"Binding to {self.host}:{self.port} timed out after {self.timeout} seconds"
            )
        except OSError as e:
            raise TransportError(f"Failed to bind to {self.host}:{self.port}: {e}")
        except Exception as e:
            raise TransportError(
                f"Unexpected error occurred while binding to {self.host}:{self.port}: {e}"
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.open:
            return
        elif self.socket:
            self.socket.close()
            self.socket = None

    def _send(self, data: bytes) -> None:
        if not self.open or self.socket is None:
            raise TransportError("Connection is not opened.")

        sent = self.socket.send(data)
        if sent != len(data):
            raise TransportError("Failed to send full UDP datagram.")

    def _receive(self, bufsize: int = 1024) -> bytes:
        if not self.open or self.socket is None:
            raise TransportError("Connection is not opened.")

        data, _ = self.socket.recvfrom(bufsize)
        return data

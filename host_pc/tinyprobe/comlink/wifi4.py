"""
    Copyright (C) 2025 ETH Zurich. All rights reserved.

    Author: Cedric Hirschi, ETH Zurich
            Sergei Vostrikov, ETH Zurich

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    SPDX-License-Identifier: Apache-2.0
"""

import socket
import logging
from typing import Optional

from tinyprobe.comlink import TPCom


TP_COM_MAX_UDP_PACKET_SIZE = 1472


class TPComWiFi4(TPCom):
    def __init__(
        self,
        ip: str,
        port: int = 50007,
        packet_size: int = 1002,
        timeout: int = 5,
        log: Optional[int | logging.Logger] = None,
    ):
        super().__init__(packet_size, log=log)

        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = None

    def open(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.socket.bind(("", self.port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, int(20 * 1e8))
            self.connected = True
            self._log.info(f"Bound to {self.ip}:{self.port}")
        except Exception as e:
            self._log.error(f"Failed to bind: {e}")
            self.socket = None
            self.connected = False

        return self.connected

    def close(self):
        if self.socket:
            self.socket.close()
            self.connected = False
            self._log.info(f"Disconnected from {self.ip}:{self.port}")
        else:
            self._log.warning("No active connection to disconnect.")

    def send(self, data: bytes) -> bool:
        if not self.connected:
            self._log.warning("Not connected. Cannot send data.")
            return False

        try:
            self.socket.sendto(data, (self.ip, self.port))
            return True
        except Exception as e:
            self._log.error(f"Failed to send data: {e}")
            return False

    def receive(self, length: int) -> bytes:
        if not self.connected:
            self._log.warning("Not connected. Cannot receive data.")
            return b""

        try:
            to_receive = length
            received_bytes = b""

            while to_receive > 0:
                chunk_size = min(to_receive, TP_COM_MAX_UDP_PACKET_SIZE)
                chunk, addr = self.socket.recvfrom(chunk_size)
                received_bytes += chunk
                to_receive -= len(chunk)

                if addr != (self.ip, self.port):
                    self._log.warning(
                        f"Received data from unexpected address: {addr}, expected {(self.ip, self.port)}"
                    )

            return received_bytes

        except socket.timeout:
            self._log.warning("Receive timed out.")
            return b""
        except Exception as e:
            self._log.error(f"Failed to receive data: {e}")
            return b""

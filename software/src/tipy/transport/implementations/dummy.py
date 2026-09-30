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

import logging

from ...control import methods_pb2
from ..transport import (
    TransportEndpoint,
    TransportError,
    TransportProtocol,
)


class TransportDummy(TransportProtocol):
    """Transport over a dummy protobuf RPC connection."""

    def __init__(self, available_methods: list[str] | None = None):
        self.device: TransportEndpoint | None = None

        self._log = logging.getLogger().getChild("dummy")

        self._open: bool = False
        self._requests: list[methods_pb2.request] = []
        self._response_buffer = b""
        self._available_methods = available_methods or []

    @staticmethod
    def get_available() -> list[TransportEndpoint]:
        return []

    def set_device(self, device: TransportEndpoint) -> None:
        self.device = device

    @property
    def open(self) -> bool:
        return self._open

    def __enter__(self):
        if self.open:
            return self
        if self.device is None:
            raise TransportError("No device set.")

        self._open = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.open:
            return

        self._open = False

    def _send(self, data: bytes) -> None:
        if not self.open:
            raise TransportError("Connection is not opened.")

        payload = self.unframe_payload(data)
        request = methods_pb2.request()
        request.ParseFromString(payload)
        self._requests.append(request)
        for cmd in request.cmd:
            c: methods_pb2.cmd = cmd
            cmd_string = ""
            method = c.WhichOneof("args")
            cmd_string += method + "("
            args = getattr(c, c.WhichOneof("args"))
            fields = args.ListFields()
            cmd_string += (
                ",".join(f"{field_desc.name}={field}" for field_desc, field in fields)
                + ")"
            )
            self._log.debug(cmd_string)

        response = methods_pb2.response()
        response.status.extend([methods_pb2.OK] * len(request.cmd))
        self._response_buffer += self.frame_payload(response.SerializeToString())

    def _receive(self, bufsize: int = 1024) -> bytes:
        if not self.open:
            raise TransportError("Connection is not opened.")

        data = self._response_buffer[:bufsize]
        self._response_buffer = self._response_buffer[bufsize:]
        return data

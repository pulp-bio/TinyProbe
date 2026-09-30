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
from typing import Self

from tipy.control.command import CommandClient
from tipy.control.methods import Method
from tipy.control.rpc import RPCResponse, methods_from_payload, serialize_responses
from tipy.transport.transport import TransportEndpoint, TransportProtocol


class DummyTransport(TransportProtocol):
    def __init__(self):
        self._open = False
        self._log = logging.getLogger().getChild("dummy")
        self._responses = []
        self._response_buffer = b""

    @staticmethod
    def get_available() -> list[TransportEndpoint]:
        return [TransportEndpoint(device="dummy", description="Dummy Protocol")]

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
        methods = methods_from_payload(self.unframe_payload(data))

        for method in methods:
            self._responses.append(RPCResponse(method=method, status=0))

    def _receive(self, bufsize: int = 1024) -> bytes:
        self._response_buffer += serialize_responses(self._responses)

        response = self._response_buffer[:bufsize]
        self._response_buffer = self._response_buffer[bufsize:]

        return response


transport = DummyTransport()
client = CommandClient(transport)

rsp = client.request(Method("ping"))
print(rsp)

rsp = client.request(Method("ping", params={"probe_id": 42}))
print(rsp)

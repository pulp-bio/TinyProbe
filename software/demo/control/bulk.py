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
import threading
import time
from typing import Self

from tipy.control.bulk import BulkConsumer, BulkEvent, BulkReceiver
from tipy.tools.logging import setup_logging
from tipy.transport.transport import TransportEndpoint, TransportProtocol


class DummyTransport(TransportProtocol):
    def __init__(self):
        self._open = False
        self._log = logging.getLogger().getChild("dummy")
        self._iteration = 0

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

    def send(self, data: bytes) -> None:
        pass

    def receive(self, bufsize: int = 1024) -> bytes:
        result = f"Dummy data {self._iteration}".encode()
        self._log.debug(f"Sending  at {time.time():.1f}: '{result.decode()}'")
        self._iteration += 1
        threading.Event().wait(0.1)  # Simulate some delay
        return result


log = setup_logging("DEBUG")


transport = DummyTransport()
receiver = BulkReceiver(transport, buffer_size=64)

receiver.start()


def print_received(event: BulkEvent):
    timestamp, data = event
    threading.Event().wait(0.5)  # Simulate processing time
    log.info(f"Received at {timestamp:.1f}: '{data.decode()}'")


try:
    consumer_1 = BulkConsumer("Consumer 1", print_received, queue_size=1)
    consumer_1.start()
    receiver.add_consumer(consumer_1)
    consumer_2 = BulkConsumer("Consumer 2", print_received, queue_size=5)
    consumer_2.start()
    receiver.add_consumer(consumer_2)

    time.sleep(3)

finally:
    receiver.stop()

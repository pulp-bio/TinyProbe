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

import queue
import time

from tipy.control.bulk import BulkConsumer, BulkReceiver
from tipy.transport.transport import TransportProtocol


class QueueInterface(TransportProtocol):
    def __init__(self):
        self._open = False
        self._queue: queue.Queue[bytes] = queue.Queue()

    @property
    def open(self) -> bool:
        return self._open

    @staticmethod
    def get_available():
        return []

    def set_device(self, device) -> None:
        return

    def __enter__(self):
        self._open = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._open = False

    def _send(self, data: bytes) -> None:
        return

    def _receive(self, bufsize: int = 1024) -> bytes:
        try:
            return self._queue.get(timeout=0.05)
        except queue.Empty as e:
            raise TimeoutError() from e

    def feed(self, data: bytes) -> None:
        self._queue.put(data)


def _wait_until(predicate, timeout: float = 1.0) -> None:
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return
        time.sleep(0.01)

    raise AssertionError("Condition was not met within timeout")


class TestDataServer:
    def test_consumer_gets_timestamped_data(self):
        intf = QueueInterface()
        server = BulkReceiver(intf)
        consumer = BulkConsumer("main", queue_size=2)

        server.add_consumer(consumer)
        server.start()

        intf.feed(b"frame-1")
        intf.feed(b"frame-2")

        _wait_until(lambda: len(consumer.events) >= 2)

        server.stop()

        assert len(consumer.events) >= 2

        first_two = consumer.events[:2]
        assert first_two[0][1] == b"frame-1"
        assert first_two[1][1] == b"frame-2"
        assert isinstance(first_two[0][0], float)
        assert isinstance(first_two[1][0], float)

    def test_remove_consumer_stops_delivery(self):
        intf = QueueInterface()
        server = BulkReceiver(intf)
        consumer = BulkConsumer("secondary")

        server.add_consumer(consumer)
        server.start()

        intf.feed(b"frame-before-remove")
        _wait_until(lambda: len(consumer.events) == 1)

        server.remove_consumer(consumer)
        before = len(consumer.events)

        intf.feed(b"frame-after-remove")
        time.sleep(0.15)

        server.stop()

        assert len(consumer.events) == before

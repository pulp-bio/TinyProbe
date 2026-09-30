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
from collections.abc import Callable
from queue import Full, Queue

from ..transport.transport import TransportProtocol

BulkEvent = tuple[float, bytes]


class BulkConsumer:
    def __init__(
        self,
        name: str,
        handler: Callable[[BulkEvent], None] | None = None,
        queue_size: int = 1,
    ):
        self._log = logging.getLogger().getChild("consumer").getChild(name)

        self._name = name
        self._handler = handler
        self._queue: Queue[BulkEvent | None] = Queue(maxsize=queue_size)
        self._thread: threading.Thread | None = None
        self._events: list[BulkEvent] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def events(self) -> list[BulkEvent]:
        return self._events

    def push(self, event: BulkEvent, block: bool) -> None:
        self._queue.put(event, block=block)

    def _consumer_thread(self):
        self._log.debug("Consumer '%s' start", self._name)

        while True:
            item = self._queue.get()

            if item is None:
                break

            self._events.append(item)
            if self._handler is not None:
                self._handler(item)

        self._log.debug("Consumer '%s' exit", self._name)

    def start(self):
        if self.running:
            return

        self._thread = threading.Thread(target=self._consumer_thread)
        self._thread.start()

    def stop(self):
        if self._thread is None:
            return

        self._queue.put(None)
        self._thread.join()
        self._thread = None


class BulkReceiver:
    def __init__(
        self, intf: TransportProtocol, buffer_size: int = 1400, block: bool = False
    ):
        self._log = logging.getLogger().getChild("bulk")

        self._intf = intf
        self._buffer_size = buffer_size
        self._block = block

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._consumers: list[BulkConsumer] = []
        self._consumers_lock = threading.Lock()

        self._times: list[float] = []
        self._buffer: list[bytes] = []

    def _server_thread(self):
        self._log.debug("BulkReceiver start")

        try:
            with self._intf:
                while not self._stop_event.is_set():
                    try:
                        chunk = self._intf.receive_raw_upto(self._buffer_size)
                    except TimeoutError:
                        continue

                    timestamp = time.time()
                    self._times.append(timestamp)
                    self._buffer.append(chunk)

                    event = (timestamp, chunk)
                    with self._consumers_lock:
                        for consumer in self._consumers:
                            try:
                                consumer.push(event, self._block)
                            except Full:
                                pass
        except Exception as e:
            self._log.error(f"BulkReceiver error: {e}")

        self._log.debug("BulkReceiver exit")

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def times(self) -> list[float]:
        return self._times

    @property
    def buffer(self) -> list[bytes]:
        return self._buffer

    def add_consumer(self, consumer: BulkConsumer):
        with self._consumers_lock:
            if consumer in self._consumers:
                return

            self._consumers.append(consumer)

        consumer.start()

    def remove_consumer(self, consumer: BulkConsumer):
        with self._consumers_lock:
            if consumer not in self._consumers:
                return

            self._consumers.remove(consumer)

        consumer.stop()

    def start(self):
        if self.running:
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._server_thread)
        self._thread.start()

    def stop(self):
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join()
            self._thread = None

        with self._consumers_lock:
            consumers = list(self._consumers)

        for consumer in consumers:
            consumer.stop()

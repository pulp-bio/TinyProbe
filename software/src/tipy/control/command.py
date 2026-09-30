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
import time

from ..transport.transport import TransportProtocol
from .methods import MAX_COMMANDS_PER_PACKET, METHOD_NAMES, Method, TinyprobeMethods
from .rpc import (
    RPCResponse,
    response_from_payload,
    serialize_methods,
)


class _AtomicGroup:
    """Wrapper for methods that must stay together in one packet."""

    def __init__(self, requests: list[Method]):
        self.requests = requests

    def __repr__(self):
        return f"_AtomicGroup({len(self.requests)} requests)"


class CommandClient:
    CONNECTION_DELAY_S = 0.0

    def __init__(
        self,
        intf: TransportProtocol,
        max_packet_size: int = 1000,
        max_commands_per_packet: int = MAX_COMMANDS_PER_PACKET,
        do_cache_methods: bool = True,
    ):
        if max_commands_per_packet < 1:
            raise ValueError("max_commands_per_packet must be at least 1")

        self._log = logging.getLogger().getChild("command")

        self._intf = intf
        self._max_packet_size = max_packet_size
        self._max_commands_per_packet = max_commands_per_packet
        self._do_cache_methods = do_cache_methods
        self._method_factory = TinyprobeMethods()

        self._do_batch_requests = False
        self._batch_requests: list[Method | _AtomicGroup] = []
        self._last_batch_requests: list[Method | _AtomicGroup] = []
        self._batch_responses: list[RPCResponse] = []
        self._batch_response_times: list[float] = []

        self._do_atomic_requests = False
        self._atomic_requests: list[Method] = []

    @property
    def cache_methods(self) -> bool:
        return self._do_cache_methods

    @property
    def methods(self) -> list[str]:
        return sorted(METHOD_NAMES)

    def request(self, method: Method) -> RPCResponse | None:
        self._validate_method(method)

        if not self._do_batch_requests:
            responses = self._send_methods([method])
            return responses[0] if responses else None

        if self._do_atomic_requests:
            self._atomic_requests.append(method)
        else:
            self._batch_requests.append(method)
        return None

    def notify(self, method: Method) -> None:
        self.request(method)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(f"'Client' object has no attribute '{name}'")
        if name in {
            "request",
            "notify",
            "methods",
            "batch_response_times",
            "batch_requests",
            "batch_responses",
        }:
            return super().__getattribute__(name)
        if self._do_cache_methods and name not in self.methods:
            raise AttributeError(f"'Client' does not provide method '{name}'")

        factory = getattr(self._method_factory, name, None)

        def method(*args, **kwargs):
            if factory is not None:
                return self.request(factory(*args, **kwargs))
            return self.request(Method(method=name, params=kwargs))

        return method

    def batch(self):
        class BatchContextManager:
            def __init__(self, server: CommandClient):
                self.server = server

            def __enter__(self):
                self.server._do_batch_requests = True
                self.server._batch_requests = []
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.server._do_batch_requests = False
                    self.server._batch_requests = []
                    return False

                self.server._last_batch_requests = self.server._batch_requests.copy()

                if self.server._do_batch_requests and self.server._batch_requests:
                    self.server._batch_response_times = []
                    self.server._batch_responses = self._batched_request(
                        self.server._batch_requests.copy()
                    )

                self.server._do_batch_requests = False
                self.server._batch_requests = []
                return True

            def _batched_request(
                self, requests: list[Method | _AtomicGroup]
            ) -> list[RPCResponse]:
                responses: list[RPCResponse] = []

                while requests:
                    batch_requests: list[Method] = []

                    while requests:
                        next_item = requests[0]

                        if isinstance(next_item, _AtomicGroup):
                            group = next_item.requests
                            projected = [*batch_requests, *group]
                            if self.server._packet_fits(projected):
                                requests.pop(0)
                                batch_requests.extend(group)
                            elif not batch_requests:
                                self.server._raise_atomic_group_limit(group)
                            else:
                                break
                        else:
                            projected = [*batch_requests, next_item]
                            if self.server._packet_fits(projected):
                                requests.pop(0)
                                batch_requests.append(next_item)
                            elif not batch_requests:
                                self.server._raise_request_limit([next_item])
                            else:
                                break

                    start_time = time.time()
                    batch_responses = self.server._send_methods(batch_requests)
                    response_time = time.time() - start_time

                    responses.extend(batch_responses)
                    self.server._batch_response_times.extend(
                        [response_time] * len(batch_responses)
                    )

                return responses

        return BatchContextManager(self)

    def atomic(self):
        """Context manager for request groups that must stay in one packet."""

        class AtomicContextManager:
            def __init__(self, server: CommandClient):
                self.server = server

            def __enter__(self):
                if not self.server._do_batch_requests:
                    raise RuntimeError(
                        "atomic() can only be used inside a batch() context"
                    )
                if self.server._do_atomic_requests:
                    raise RuntimeError("Nested atomic() contexts are not supported")

                self.server._do_atomic_requests = True
                self.server._atomic_requests = []
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    self.server._do_atomic_requests = False
                    self.server._atomic_requests = []
                    return False

                if self.server._atomic_requests:
                    self.server._batch_requests.append(
                        _AtomicGroup(self.server._atomic_requests.copy())
                    )

                self.server._do_atomic_requests = False
                self.server._atomic_requests = []
                return True

        return AtomicContextManager(self)

    @property
    def batch_requests(self) -> list[Method]:
        flattened: list[Method] = []
        for item in self._last_batch_requests:
            if isinstance(item, _AtomicGroup):
                flattened.extend(item.requests)
            else:
                flattened.append(item)
        return flattened

    @property
    def batch_responses(self) -> list[RPCResponse]:
        if self._do_batch_requests:
            raise RuntimeError("Batch requests are still in progress")
        return self._batch_responses

    @property
    def batch_response_times(self) -> list[float]:
        return self._batch_response_times.copy()

    def _validate_method(self, method: Method) -> None:
        if self._do_cache_methods and method.method not in METHOD_NAMES:
            raise AttributeError(
                f"Method '{method.method}' is not supported by methods.proto"
            )

    def _packet_size(self, methods: list[Method]) -> int:
        return len(self._intf.frame_payload(serialize_methods(methods)))

    def _packet_fits(self, methods: list[Method]) -> bool:
        return (
            len(methods) <= self._max_commands_per_packet
            and self._packet_size(methods) <= self._max_packet_size
        )

    def _raise_atomic_group_limit(self, methods: list[Method]) -> None:
        if len(methods) > self._max_commands_per_packet:
            raise ValueError(
                f"Atomic group of {len(methods)} requests exceeds "
                f"max_commands_per_packet ({self._max_commands_per_packet} commands)"
            )

        group_size = self._packet_size(methods)
        raise ValueError(
            f"Atomic group of {len(methods)} requests ({group_size} bytes) exceeds "
            f"max_packet_size ({self._max_packet_size} bytes)"
        )

    def _raise_request_limit(self, methods: list[Method]) -> None:
        if len(methods) > self._max_commands_per_packet:
            raise ValueError(
                f"Request packet with {len(methods)} commands exceeds "
                f"max_commands_per_packet ({self._max_commands_per_packet} commands)"
            )

        request_size = self._packet_size(methods)
        raise ValueError(
            f"Request ({request_size} bytes) exceeds max_packet_size "
            f"({self._max_packet_size} bytes)"
        )

    def _send_methods(self, methods: list[Method]) -> list[RPCResponse]:
        if not methods:
            return []

        if len(methods) > self._max_commands_per_packet:
            raise ValueError(
                f"Request packet with {len(methods)} commands exceeds "
                f"max_commands_per_packet ({self._max_commands_per_packet} commands)"
            )

        frame = self._intf.frame_payload(serialize_methods(methods))
        if len(frame) > self._max_packet_size:
            raise ValueError(
                f"Request packet ({len(frame)} bytes) exceeds max_packet_size "
                f"({self._max_packet_size} bytes)"
            )

        payload = serialize_methods(methods)
        with self._intf as comm:
            comm.send_frame(payload)
            message = comm.receive_frame()

        return response_from_payload(message, methods)

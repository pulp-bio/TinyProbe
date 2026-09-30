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

from collections.abc import Iterable
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from . import methods_pb2
from .methods import (
    METHOD_NAMES,
    Method,
    RPCStatus,
    is_ok_status,
    method_field_names,
    proto_scalar,
    status_name,
)

__all__ = [
    "METHOD_NAMES",
    "RPCProtocolError",
    "RPCResponse",
    "RPCStatus",
    "cmd_from_method",
    "request_from_methods",
    "response_from_payload",
    "serialize_methods",
]


class RPCProtocolError(ValueError):
    """Raised when a protobuf RPC frame or response is malformed."""


@dataclass(slots=True)
class RPCResponse:
    method: Method
    status: int

    @property
    def ok(self) -> bool:
        return is_ok_status(self.status)

    @property
    def status_name(self) -> str:
        return status_name(self.status)

    @staticmethod
    def print_table(
        requests: list[Method],
        responses: list["RPCResponse"],
        response_times: list[float] | None = None,
        errors_only: bool = False,
        title: str = "Device Responses",
    ) -> None:
        table = Table(title=title)
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Method", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Params", style="magenta")
        table.add_column("Time", style="yellow")

        for index, request in enumerate(requests):
            response = responses[index] if index < len(responses) else None
            if response is not None and errors_only and response.ok:
                continue

            status = response.status_name if response is not None else "NO_RESPONSE"
            style = "green" if response is not None and response.ok else "red"
            response_time = ""
            if response_times is not None and index < len(response_times):
                response_time = f"{response_times[index]:.3f}s"

            table.add_row(
                str(index),
                request.method,
                f"[{style}]{status}[/{style}]",
                str(request.params or {}),
                response_time,
            )

        Console().print(table)


def request_from_methods(methods: Iterable[Method]) -> methods_pb2.request:
    request = methods_pb2.request()
    request.cmd.extend(cmd_from_method(method) for method in methods)
    return request


def serialize_methods(methods: Iterable[Method]) -> bytes:
    return request_from_methods(methods).SerializeToString()


def methods_from_payload(payload: bytes) -> list[Method]:
    request = methods_pb2.request()
    request.ParseFromString(payload)
    return [Method(method=cmd.WhichOneof("args"), params=cmd) for cmd in request.cmd]


def response_from_payload(payload: bytes, requests: list[Method]) -> list[RPCResponse]:
    response = methods_pb2.response()
    response.ParseFromString(payload)

    if len(response.status) != len(requests):
        raise RPCProtocolError(
            f"Response status count {len(response.status)} does not match "
            f"request command count {len(requests)}"
        )

    return [
        RPCResponse(method=request, status=int(status))
        for request, status in zip(requests, response.status)
    ]


def serialize_responses(responses: Iterable[RPCResponse]) -> bytes:
    response = methods_pb2.response()
    response.status.extend(int(r.status) for r in responses)
    return response.SerializeToString()


def cmd_from_method(method: Method) -> methods_pb2.cmd:
    if method.method not in METHOD_NAMES:
        raise AttributeError(
            f"Method '{method.method}' is not supported by methods.proto"
        )

    cmd = methods_pb2.cmd()
    args = getattr(cmd, method.method)
    allowed_fields = set(method_field_names(method.method))
    params = method.params or {}

    unknown_fields = set(params) - allowed_fields
    if unknown_fields:
        unknown = ", ".join(sorted(unknown_fields))
        raise ValueError(f"Unknown parameter(s) for {method.method}: {unknown}")

    for name, value in params.items():
        setattr(args, name, proto_scalar(value))

    # Empty/default-valued protobuf submessages still need oneof presence.
    args.SetInParent()

    return cmd

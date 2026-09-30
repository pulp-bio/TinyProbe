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

from tipy.control.methods import Method
from tipy.control.rpc import (
    RPCResponse,
    RPCStatus,
    methods_from_payload,
    response_from_payload,
    serialize_methods,
    serialize_responses,
)

methods = [
    Method("ping", {"probe_id": 42}),
    Method("delayms", {"delay": 100}),
]

methods_serialized = serialize_methods(methods)
print("Methods serialized: ", methods_serialized.hex(" ", 2))

methods_deserialized = methods_from_payload(methods_serialized)
print("Methods deserialized: ", methods_deserialized)

responses = []
for method in methods_deserialized:
    responses.append(RPCResponse(method=method, status=RPCStatus.OK))

responses_serialized = serialize_responses(responses)
print("Responses serialized: ", responses_serialized.hex(" ", 2))

responses_deserialized = response_from_payload(
    responses_serialized, methods_deserialized
)
print("Responses deserialized: ", responses_deserialized)

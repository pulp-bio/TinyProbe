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
"""

from dataclasses import dataclass
import struct


ENDIANNESS = "<"  # Little-endian
HEADER = "BH"  # Network byte order (little-endian)


@dataclass
class Command:
    _id: int = 255
    _format: str = ""

    def from_dict(self, data: dict):
        args = data.get("args", [])
        # print(f"Loading command {self.__class__.__name__} with args: {args}")

        fields = [
            field
            for field in self.__dataclass_fields__.values()
            if not field.name.startswith("_")
        ]

        for field, value in zip(fields, args):
            # print(f"Setting {field.name} to {value}")
            setattr(self, field.name, value)

    def pack(self) -> bytes:
        # Get all args in self
        args = [
            getattr(self, field.name)
            for name, field in self.__dataclass_fields__.items()
            if not name.startswith("_") or callable(getattr(self, name))
        ]

        # Get size of the packed data
        size = struct.calcsize(ENDIANNESS + self._format)
        return struct.pack(ENDIANNESS + HEADER + self._format, self._id, size, *args)

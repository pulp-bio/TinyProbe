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


@dataclass
class PingCommand(Command):
    _id: int = 0
    _format: str = "B"

    probe_id: int = 1


@dataclass
class ActivateReplies(Command):
    _id: int = 1
    _format: str = "B"

    replies_on: int = 1


@dataclass
class SwitchSpiMux(Command):
    _id: int = 2
    _format: str = "B"

    mux_code: int = 0


@dataclass
class WriteSpiPacket(Command):
    _id: int = 3
    _format: str = "s"

    bytes_array: bytes = b""


@dataclass
class WriteFPGAReg(Command):
    _id: int = 4
    _format: str = "BI"

    addr: int = 0
    val: int = 0


@dataclass
class WriteAfeReg(Command):
    _id: int = 5
    _format: str = "BBH"

    dtgc_die: bool = False
    addr: int = 0
    val: int = 0


@dataclass
class WriteTxReg(Command):
    _id: int = 6
    _format: str = "HI"

    addr: int = 0
    val: int = 0


@dataclass
class DelayNs(Command):
    _id: int = 7
    _format: str = "Q"

    delay: int = 0


@dataclass
class SleepMs(Command):
    _id: int = 8
    _format: str = "I"

    delay: int = 0


@dataclass
class ControlPower(Command):
    _id: int = 9
    _format: str = "BB"

    domain_id: int = 0
    enable: bool = False


@dataclass
class TriggerShot(Command):
    _id: int = 10
    _format: str = "HHBBHBB"

    n_shots: int = 1
    n_packets: int = 82
    dc_dc_off_delay_us: int = 61  # in 0.1us
    read_fifo_delay_us: int = 200
    trig_pack_id: int = 65535
    sw_trigger: bool = True
    dc_dc_pwd_at_rx: bool = True


@dataclass
class SetPowersaveMode(Command):
    _id: int = 11
    _format: str = "BB"

    domain: int = 0
    enable: bool = False

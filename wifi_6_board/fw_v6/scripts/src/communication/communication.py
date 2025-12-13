"""
Copyright (C) 2025 ETH Zurich. All rights reserved.

Author: Cedric Hirschi, ETH Zurich

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
from typing import Protocol, runtime_checkable

from rich.progress import track

from ..command.command import Command
from ..command.sequence import CommandSequence
from ..command.response import Response


class CommunicationError(Exception):
    pass


@dataclass(slots=True)
class CommunicationDevice:
    device: str
    description: str

    def __str__(self) -> str:
        return f"{self.device}: {self.description}"

    @staticmethod
    def from_str(s: str) -> "CommunicationDevice":
        parts = s.split(":", 1)
        device = parts[0]
        description = parts[1].strip() if len(parts) > 1 else ""
        return CommunicationDevice(device=device, description=description)


@runtime_checkable
class CommunicationInterface(Protocol):
    def get_available(self) -> list[CommunicationDevice]: ...
    def set_device(self, device: CommunicationDevice) -> None: ...

    @property
    def open(self) -> bool: ...

    def __enter__(self) -> "CommunicationInterface": ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...

    def _send_bytes(self, data: bytes) -> None: ...
    def _receive_responses(self) -> list[Response]: ...

    def send(
        self, command: Command | CommandSequence | list[Command]
    ) -> list[list[Response]]:
        if not self.open:
            raise CommunicationError("Connection is not opened.")

        packed_commands: list[bytes] = []
        num_commands: list[int] = []

        if not isinstance(command, CommandSequence):
            command_sequence = CommandSequence()
            command_sequence.add_command(command)
        else:
            command_sequence = command

        packed_commands, num_commands = command_sequence.pack()

        responses: list[list[Response]] = []

        for i in track(
            range(len(packed_commands)),
            description="Sending packets",
            transient=True,
        ):
            packed_command = packed_commands[i]
            num = num_commands[i]

            self._send_bytes(packed_command)

            for _ in track(
                range(num),
                description="Receiving responses",
                transient=True,
            ):
                response = self._receive_responses()
                if len(response) == 0:
                    raise TimeoutError("No response received from the device.")

                responses.append(response)

        return responses

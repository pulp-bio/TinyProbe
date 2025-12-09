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

import struct

from .commands import Command


PACKET_SIZE = 1000


class CommandSequence:
    def __init__(self, commands: list[Command] = []):
        self.commands = commands

    def add_command(self, commands: "Command | list[Command] | CommandSequence"):
        if isinstance(commands, list) and all(isinstance(c, Command) for c in commands):
            self.commands.extend(commands)  # type: ignore
        elif isinstance(commands, Command):
            self.commands.append(commands)
        elif isinstance(commands, CommandSequence):
            self.commands.extend(commands.commands)
        else:
            raise TypeError(
                "commands must be a Command, list of Command instances, or CommandSequence"
            )

    def pack(self) -> tuple[list[bytes], list[int]]:
        packed_commands: list[bytes] = [command.pack() for command in self.commands]

        # Group commands such that each group is smaller than 1000 bytes
        grouped_commands: list[list[bytes]] = []
        current_group: list[bytes] = []
        current_size = 0

        for command in packed_commands:
            if len(command) > PACKET_SIZE:
                raise ValueError(
                    f"Command size {len(command)} exceeds maximum packet size {PACKET_SIZE}"
                )

            if current_size + len(command) + 2 > PACKET_SIZE:
                grouped_commands.append(current_group)
                current_group = []
                current_size = 0
            current_group.append(command)
            current_size += len(command)

        if current_group:
            grouped_commands.append(current_group)

        result: list[bytes] = []
        for group in grouped_commands:
            packed_command = struct.pack("<H", len(group))
            packed_command += b"".join(group)
            result.append(packed_command)

        return result, [len(group) for group in grouped_commands]

    def __len__(self):
        return len(self.commands)

    def __str__(self):
        return f"CommandSequence(num_commands={len(self.commands)})"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.commands)

    def __getitem__(self, index: int) -> Command:
        return self.commands[index]

    def __setitem__(self, index: int, value: Command):
        self.commands[index] = value

import socket

from rich.progress import track
from rich import print

from commands import Command
from command_sequence import CommandSequence
from response import Response


class CommunicationDevice:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None

    def __enter__(self):
        self.socket = socket.create_connection(
            (self.host, self.port), timeout=self.timeout
        )
        print(f"Connected to {self.host}:{self.port}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.socket:
            self.socket.close()
            self.socket = None
            print(f"Disconnected from {self.host}:{self.port}")

    def send(
        self, command: Command | CommandSequence | list[Command]
    ) -> list[Response]:
        if not self.socket:
            raise ConnectionError("Not connected to the device.")

        packed_commands: list[bytes] = []
        num_commands: list[int] = []

        if isinstance(command, list):
            packed_command, num_commands = CommandSequence(command).pack()
            packed_commands.extend(packed_command)
            num_commands.extend(num_commands)

        elif isinstance(command, CommandSequence):
            packed_command, num_commands = command.pack()
            packed_commands.extend(packed_command)
            num_commands.extend(num_commands)
        elif isinstance(command, Command):
            packed_commands.append(command.pack())
            num_commands = [1]
        else:
            raise TypeError("Invalid command type.")

        responses: list[Response] = []

        for i in track(
            range(len(packed_commands)),
            description="Sending packets",
            transient=True,
        ):
            packed_command = packed_commands[i]
            num = num_commands[i]

            self.socket.sendall(packed_command)

            # start_time = time.time()

            for _ in track(
                range(num),
                description="Receiving responses",
                transient=True,
            ):
                response = Response.from_socket(self.socket)
                responses.append(response)

        return responses

import socket
import time

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
    ) -> list[list[Response]]:
        if not self.socket:
            raise ConnectionError("Not connected to the device.")

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

            self.socket.sendall(packed_command)

            # start_time = time.time()

            for _ in track(
                range(num),
                description="Receiving responses",
                transient=True,
            ):
                response = Response.from_socket(self.socket)
                if len(response) == 0:
                    raise TimeoutError("No response received from the device.")

                responses.append(response)

            # time.sleep(0.5)  # Small delay between command packets

        return responses

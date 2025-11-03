from dataclasses import dataclass
import struct
import time
import socket

from rich.table import Table
from rich.console import Console


@dataclass
class Response:
    command_id: int
    is_ok: bool
    data: bytes = b""
    error_code: int = 0
    response_time: float = 0.0
    execution_time: float = 0.0

    @staticmethod
    def from_bytes(data: bytes) -> "Response":
        command_id = data[0]
        status = data[1:3]
        if status == b"OK":
            response_size = struct.unpack("<H", data[3:5])[0]
            response_data = data[5 : 5 + response_size]
            return Response(command_id, True, data=response_data)
        else:  # status == b"ER"
            error_code = data[3]
            return Response(command_id, False, error_code=error_code)

    @staticmethod
    def from_socket(sock: socket.socket) -> "Response":
        try:
            command_id = sock.recv(1)[0]
            response_time = time.time()
            status = sock.recv(2)
            execution_time = time.time()
            if status == b"OK":
                # response_size_bytes = sock.recv(2)
                # response_size = struct.unpack("<H", response_size_bytes)[0]
                # response_data = sock.recv(response_size)
                return Response(
                    command_id,
                    True,
                    # data=response_data,
                    response_time=response_time,
                    execution_time=execution_time,
                )
            else:  # status == b"ER"
                error_code = sock.recv(4)
                return Response(
                    command_id,
                    False,
                    error_code=struct.unpack("<I", error_code)[0],
                    response_time=response_time,
                    execution_time=execution_time,
                )
        except socket.timeout:
            raise TimeoutError("Response timed out.")

    @staticmethod
    def print_table(responses: list["Response"]) -> None:
        table = Table(title="Device Responses")
        table.add_column("IDX", justify="right", style="dim", no_wrap=True)
        table.add_column("Cmd. ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Data", style="green")
        table.add_column("Error", justify="right", style="red")
        table.add_column("Resp. Time", justify="right", style="dim")
        table.add_column("Exec. Time", justify="right", style="dim")

        prev_time = responses[0].response_time

        for i, response in enumerate(responses):
            status = "OK" if response.is_ok else "ERROR"
            data_str = response.data.hex() if response.data else ""
            error_code_str = str(response.error_code) if not response.is_ok else ""

            response_time = response.response_time - prev_time
            prev_time = response.response_time
            execution_time = response.execution_time - prev_time
            prev_time = response.execution_time

            table.add_row(
                str(i),
                str(response.command_id),
                status,
                data_str,
                error_code_str,
                str(f"{response_time * 1e3:.1f} ms"),
                str(f"{execution_time * 1e3:.1f} ms"),
            )

        console = Console()
        console.print(table)

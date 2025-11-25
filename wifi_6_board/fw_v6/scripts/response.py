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
    def from_socket(sock: socket.socket) -> list["Response"]:
        result = []
        
        while True:
            try:
                command_id = sock.recv(1)[0]
                response_time = time.time()
                status = sock.recv(2)
                execution_time = time.time()

                match status:

                    case b"OK":
                        result.append(Response(
                            command_id,
                            True,
                            # data=response_data,
                            response_time=response_time,
                            execution_time=execution_time,
                        ))
                        break

                    case b"ER":
                        error_code = sock.recv(4)
                        result.append(Response(
                            command_id,
                            False,
                            error_code=struct.unpack("<I", error_code)[0],
                            response_time=response_time,
                            execution_time=execution_time,
                        ))
                        break

                    case b"DT":
                        num_packets = sock.recv(1)
                        packets = []
                        for _ in range(num_packets[0]):
                            packets.append(sock.recv(1400))

                        result.append(Response(
                            command_id,
                            True,
                            data=b"".join(packets),
                            response_time=response_time,
                            execution_time=execution_time,
                        ))

            except socket.timeout:
                # raise TimeoutError("Response timed out.")
                break

        return result

    @staticmethod
    def print_table(responses: list[list["Response"]]) -> None:
        table = Table(title="Device Responses")
        table.add_column("IDX", justify="right", style="dim", no_wrap=True)
        table.add_column("Cmd. ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Data", style="green")
        table.add_column("Error", justify="right", style="red")
        table.add_column("Resp. Time", justify="right", style="dim")
        table.add_column("Exec. Time", justify="right", style="dim")

        prev_time = responses[0][-1].response_time

        for i, response in enumerate(responses):
            num_responses = len(response)
            last_response = response[-1]

            data_str = f"{num_responses-1} pkt(s)" if num_responses > 2 else ""

            status = "OK" if last_response.is_ok else "ERROR"
            error_code_str = str(last_response.error_code) if not last_response.is_ok else ""

            response_time = last_response.response_time - prev_time
            prev_time = last_response.response_time
            execution_time = last_response.execution_time - prev_time
            prev_time = last_response.execution_time

            table.add_row(
                str(i),
                str(last_response.command_id),
                status,
                data_str,
                error_code_str,
                str(f"{response_time * 1e3:.1f} ms"),
                str(f"{execution_time * 1e3:.1f} ms"),
            )

        console = Console()
        console.print(table)

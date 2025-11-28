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
import struct
import time
import socket

from rich.table import Table
from rich.console import Console
from rich.panel import Panel


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

                match status:
                    case b"OK":
                        execution_time = time.time()

                        result.append(
                            Response(
                                command_id,
                                True,
                                # data=response_data,
                                response_time=response_time,
                                execution_time=execution_time,
                            )
                        )
                        break

                    case b"ER":
                        error_code = sock.recv(4)

                        execution_time = time.time()

                        result.append(
                            Response(
                                command_id,
                                False,
                                error_code=struct.unpack("<I", error_code)[0],
                                response_time=response_time,
                                execution_time=execution_time,
                            )
                        )
                        break

                    case b"DT":
                        num_packets = sock.recv(1)
                        packets = []
                        for _ in range(num_packets[0]):
                            packets.append(sock.recv(1400))

                        execution_time = time.time()

                        result.append(
                            Response(
                                command_id,
                                True,
                                data=b"".join(packets),
                                response_time=response_time,
                                execution_time=execution_time,
                            )
                        )

            except socket.timeout:
                # raise TimeoutError("Response timed out.")
                break

        return result

    @staticmethod
    def print_table(
        responses: list[list["Response"]], start_time: float, errors_only: bool = False
    ) -> None:
        table = Table(title="Device Responses")
        table.add_column("IDX", justify="right", style="dim", no_wrap=True)
        table.add_column("Cmd. ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Data", style="green")
        table.add_column("Error", justify="right", style="red")
        table.add_column("Resp. Time", justify="right", style="dim")
        table.add_column("Exec. Time", justify="right", style="dim")

        prev_time = start_time

        i = -1
        for i, response in enumerate(responses):
            num_responses = len(response)
            last_response = response[-1]

            data_str = f"{num_responses-1} pkt(s)" if num_responses > 2 else ""

            status = "OK" if last_response.is_ok else "ERROR"
            error_code_str = (
                str(last_response.error_code) if not last_response.is_ok else ""
            )

            if errors_only and last_response.is_ok:
                continue

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

        if table.row_count == 0:
            console.print(
                Panel.fit(
                    "[green]All commands executed successfully without errors.[/green]",
                    title="Device Responses",
                    subtitle=f"Total Commands: {i+1}",
                )
            )
        else:
            console.print(table)

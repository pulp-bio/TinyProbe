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

import socket
import threading
from typing import Any
import time
import datetime

from rich import print

from src import (
    TriggerShot,
    PingCommand,
    CommunicationInterfaceWiFi6,
    CommunicationDevice,
    Response,
)
from src.command_sequences.load import load_sequence_config, load_sequence_acquire


received_packets: list[tuple[bytes, float, Any]] = []


def udp_receiver(port: int, stop_event: threading.Event):
    global received_packets

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", port))
    udp_socket.settimeout(1.0)

    last_bytes = 0

    while not stop_event.is_set() or last_bytes:
        try:
            data, addr = udp_socket.recvfrom(1400)
            last_bytes = len(data)
            # print(
            #     f"Received UDP packet from {addr}: 0x{data.hex()} ({data.decode(errors='ignore')!r})"
            # )
            received_packets.append((data, time.monotonic(), addr))
        except socket.timeout:
            last_bytes = 0
            continue

    udp_socket.close()


def to_human(num_bytes: int) -> str:
    if num_bytes >= 1e12:
        return f"{num_bytes/1e12:.4f} TB"
    elif num_bytes >= 1e9:
        return f"{num_bytes/1e9:.4f} GB"
    elif num_bytes >= 1e6:
        return f"{num_bytes/1e6:.4f} MB"
    elif num_bytes >= 1e3:
        return f"{num_bytes/1e3:.4f} kB"

    return str(num_bytes)


def main():
    # NUM_SHOTS = 10
    # cmd = [
    #     TriggerShot(n_shots=NUM_SHOTS)
    #     # PingCommand(),
    # ] * 1

    # One shot is 63 packets (always 3 packets (1400, 1400, 1202) together for 4002 bytes)
    # -> 21 * 4002 = 84042 bytes per shot

    # addr = ("192.168.50.223", 50008)
    addr = ("192.168.0.213", 50008)

    interface = CommunicationInterfaceWiFi6()
    interface.set_device(
        CommunicationDevice(device=f"{addr[0]}:{addr[1]}", description="WiFi6 Device")
    )

    stop_event = threading.Event()
    udp_thread = threading.Thread(target=udp_receiver, args=(50007, stop_event))
    udp_thread.start()

    try:
        with interface:
            cmds_config = load_sequence_config()
            start_time = time.time()
            response = interface.send(cmds_config)
            # response = interface.send(cmd)
            Response.print_table(response, start_time, errors_only=True)

            cmds_acquire = load_sequence_acquire()

            input("\nPress enter to start acquisition...")

            start_time = time.time()
            response = interface.send(cmds_acquire)
            Response.print_table(response, start_time, errors_only=True)

    except Exception as e:
        print(f"[red]Error:[/red] {e}")
    finally:
        stop_event.set()
        udp_thread.join(2.0)
    # # Wait for potential packets to arrive
    # time.sleep(5.0)

    # for packet, addr in received_packets:
    #     print(f"From {addr}: 0x{packet.hex()} ({packet.decode(errors='ignore')!r})")
    # data_responses = []
    # for resp in response:
    #     data_responses.extend([r for r in resp if r.data != b""])

    total_bytes = sum(len(packet) for packet, _, _ in received_packets)
    # # total_bytes = sum(len(r.data) for r in data_responses)
    # expected_bytes = NUM_SHOTS * len(list(filter(lambda c: isinstance(c, TriggerShot), cmd))) * 84042

    expected_bytes = 0
    for command in cmds_acquire.commands:  # type: ignore
        if isinstance(command, TriggerShot):
            expected_bytes += command.n_packets * command.n_shots * 420210 / 410

    expected_bytes = int(expected_bytes)

    print(f"Total received: {to_human(total_bytes)}")
    print(f"      Expected: {to_human(expected_bytes)}", end="\t")
    if total_bytes == expected_bytes:
        print("[green]MATCH[/green]")
    else:
        print("[red]MISMATCH[/red]")
    min_time = min(t for _, t, _ in received_packets) if received_packets else 0
    max_time = max(t for _, t, _ in received_packets) if received_packets else 0
    duration = max_time - min_time
    data_rate = total_bytes * 8 / duration if duration > 0 else 0
    print(f"Duration: {duration:.3f} s, Data rate: {data_rate/1e6:.3f} Mbps")
    # print(
    #     f"UDP responses: {[packet.decode(errors='ignore') for packet, _ in received_packets]}"
    # )

    # If received data is not empty, save as binary
    if received_packets:
        filename = f"data/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
        with open(filename, "wb") as f:
            for packet, _, _ in received_packets:
                f.write(packet)
        print(f"Saved received data to '{filename}'")


if __name__ == "__main__":
    main()

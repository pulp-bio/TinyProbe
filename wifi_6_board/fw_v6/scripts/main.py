import socket
import threading
from typing import Any
import time
import math

from rich import print

from commands import (
    PingCommand,
    ActivateReplies,
    SwitchSpiMux,
    WriteSpiPacket,
    WriteFPGAReg,
    WriteAfeReg,
    WriteTxReg,
    DelayNs,
    SleepMs,
    ControlPower,
    TriggerShot,
    SetPowersaveMode,
)
from command_sequence import CommandSequence
from response import Response
from communication_device import CommunicationDevice


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
    NUM_SHOTS = 15
    cmd = [
        TriggerShot(n_shots=NUM_SHOTS)
    ] * 200

    # One shot is 63 packets (always 3 packets (1400, 1400, 1202) together for 4002 bytes)
    # -> 21 * 4002 = 84042 bytes per shot

    # addr = ("192.168.50.223", 50008)
    addr = ("192.168.50.234", 50008)

    device = CommunicationDevice(*addr)

    stop_event = threading.Event()
    udp_thread = threading.Thread(target=udp_receiver, args=(50007, stop_event))
    udp_thread.start()

    try:
        with device:
            start_time = time.time()
            cmds_packed = CommandSequence(cmd)  # type: ignore
            response = device.send(cmds_packed)

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
    # total_bytes = sum(len(r.data) for r in data_responses)
    expected_bytes = NUM_SHOTS * len(list(filter(lambda c: isinstance(c, TriggerShot), cmd))) * 84042
    print(f"Total received: {to_human(total_bytes)}")
    print(f"      Expected: {to_human(expected_bytes)}", end='\t')
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


if __name__ == "__main__":
    main()

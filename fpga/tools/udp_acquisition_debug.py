#!/usr/bin/env python3
# Copyright 2026 LisaMaria Odermatt
# Copyright and related rights are licensed under the Solderpad Hardware
# License, Version 0.51 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://solderpad.org/licenses/SHL-0.51. Unless required by applicable law
# or agreed to in writing, software, hardware and materials distributed under
# this License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# Authors:
#   LisaMaria Odermatt
# -----------------------------------------------------------------------------
# Description:
#   Receive TinyProbe UDP acquisition packets and validate packet and sample
#   contents.
# -----------------------------------------------------------------------------

"""Standalone TinyProbe UDP acquisition receiver and packet validator."""

from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path


def local_ipv4_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            addresses.add(info[4][0])
    except socket.gaierror:
        pass

    # This also finds the interface selected for the probe network without
    # transmitting application data.
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.168.50.1", 9))
        addresses.add(probe.getsockname()[0])
    except OSError:
        pass
    finally:
        probe.close()

    return sorted(addresses)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Receive and validate TinyProbe acquisition UDP packets."
    )
    parser.add_argument("--bind", default="0.0.0.0", help="Local bind address")
    parser.add_argument("--port", type=int, default=50007, help="UDP port")
    parser.add_argument("--packets", type=int, default=16, help="Expected packets")
    parser.add_argument(
        "--packet-size", type=int, default=1002, help="Expected UDP datagram size"
    )
    parser.add_argument(
        "--idle-timeout",
        type=float,
        default=10.0,
        help="Stop after this many seconds without a packet",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("tinyprobe_capture.bin"), help="Output file"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("Local IPv4 addresses:")
    for address in local_ipv4_addresses():
        print(f"  {address}")
    print(
        f"\nBinding UDP {args.bind}:{args.port}. Close TiPy first so it does not own the port."
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((args.bind, args.port))
    except OSError as exc:
        print(f"ERROR: could not bind UDP socket: {exc}", file=sys.stderr)
        return 2

    sock.settimeout(0.5)
    print("Listening. Trigger Shot Acquisition now...\n")

    received: dict[tuple[int, int], bytes] = {}
    sources: set[tuple[str, int]] = set()
    last_packet_time = time.monotonic()
    first_packet_time: float | None = None

    try:
        while len(received) < args.packets:
            try:
                packet, source = sock.recvfrom(max(65535, args.packet_size))
            except socket.timeout:
                idle = time.monotonic() - last_packet_time
                if idle >= args.idle_timeout:
                    print(f"Timeout: no UDP packet for {idle:.1f} seconds.")
                    break
                continue

            now = time.monotonic()
            if first_packet_time is None:
                first_packet_time = now
            last_packet_time = now
            sources.add(source)

            shot = packet[0] if len(packet) >= 1 else -1
            index = packet[1] if len(packet) >= 2 else -1
            key = (shot, index)
            duplicate = key in received
            received[key] = packet
            preview = packet[2:10].hex(" ").upper() if len(packet) > 2 else ""
            size_state = "OK" if len(packet) == args.packet_size else "BAD SIZE"
            print(
                f"RX {len(packet):4d} bytes from {source[0]}:{source[1]} "
                f"shot={shot:3d} packet={index:3d} {size_state}"
                f"{' DUPLICATE' if duplicate else ''} payload={preview}"
            )
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        sock.close()

    ordered_keys = sorted(received)
    with args.output.open("wb") as output:
        for key in ordered_keys:
            output.write(received[key])

    indices = sorted(index for shot, index in received if shot == 0)
    expected_indices = set(range(args.packets))
    missing = sorted(expected_indices - set(indices))
    bad_sizes = [key for key, packet in received.items() if len(packet) != args.packet_size]

    print("\nSummary")
    print(f"  Unique packets: {len(received)}/{args.packets}")
    print(f"  Sources:        {', '.join(f'{ip}:{port}' for ip, port in sorted(sources)) or 'none'}")
    print(f"  Missing shot 0: {missing or 'none'}")
    print(f"  Bad sizes:      {bad_sizes or 'none'}")
    print(f"  Saved:          {args.output.resolve()}")

    success = len(received) == args.packets and not missing and not bad_sizes
    print("  Result:         " + ("PASS" if success else "FAIL"))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())

import logging
import time
import datetime
import socket
import threading
from typing import Any

from rich.logging import RichHandler

from src.communication.communication import CommunicationDevice
from src.communication.interfaces.wifi6 import CommunicationInterfaceWiFi6
from src.command.response import Response
from src.config.models import TPConfig
from src.config.flows.configure_acquire import (
    fpga_settings,
    tx_settings,
    afe_settings,
    acquisition_settings,
)

log = logging.getLogger("tp").getChild("standalone")
log.setLevel(logging.INFO)
log.handlers = []
console_handler = RichHandler(
    rich_tracebacks=True, show_time=False, show_path=False, tracebacks_show_locals=True
)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s.%(funcName)s\t%(message)s")
console_handler.setFormatter(formatter)
log.addHandler(console_handler)


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


def main(config: str) -> None:
    log.info("Starting standalone acquisition script")

    with open(config, "r") as f:
        json_str = f.read()
    config_data = TPConfig.model_validate_json(json_str)

    log.info("Generating command sequences")
    try:
        cmds_fpga = fpga_settings(config_data.fpga)
        cmds_tx = tx_settings(config_data.tx)
        cmds_afe = afe_settings(config_data.afe, config_data.fpga)
        cmds_acq = acquisition_settings(config_data)
    except Exception as e:
        log.exception(f"Error generating settings configuration: {e}")
        return

    log.debug("FPGA Commands:")
    log.debug(f"  Total commands: {len(cmds_fpga)}")
    # for cmd in cmds_fpga:
    #     log.debug(f"  {cmd}")
    log.debug("TX Commands:")
    # for cmd in cmds_tx:
    #     log.debug(f"  {cmd}")
    log.debug(f"  Total commands: {len(cmds_tx)}")
    log.debug("AFE Commands:")
    # for cmd in cmds_afe:
    #     log.debug(f"  {cmd}")
    log.debug(f"  Total commands: {", ".join(list(str(len(cmd)) for cmd in cmds_afe))}")
    log.debug("Acquisition Commands:")
    # for cmd in cmds_acq:
    #     log.debug(f"  {cmd}")
    log.debug(f"  Total commands: {len(cmds_acq)}")

    stop_event = threading.Event()
    udp_thread = threading.Thread(target=udp_receiver, args=(50007, stop_event))
    udp_thread.start()

    log.info("Executing command sequences")
    try:
        intf = CommunicationInterfaceWiFi6()
        intf.set_device(
            CommunicationDevice(
                device=f"{config_data.connection.ip}:{50008}",
                description="WiFi6 Device",
            )
        )

        with intf:
            log.info("Sending FPGA configuration commands")
            time_start = time.time()
            response_fpga = intf.send(cmds_fpga)

            responses_flat = []
            for response_list in response_fpga:
                responses_flat.extend(response_list)

            if any([response.error_code for response in responses_flat]):
                Response.print_table(response_fpga, time_start, errors_only=True)

            log.info("Sending TX configuration commands")
            time_start = time.time()
            response_tx = intf.send(cmds_tx)

            responses_flat = []
            for response_list in response_tx:
                responses_flat.extend(response_list)

            if any([response.error_code for response in responses_flat]):
                Response.print_table(response_tx, time_start, errors_only=True)

            log.info("Sending AFE configuration commands")
            for cmd_afe in cmds_afe:
                time_start = time.time()
                response_afe = intf.send(cmd_afe)

                responses_flat = []
                for response_list in response_afe:
                    responses_flat.extend(response_list)

                if any([response.error_code for response in responses_flat]):
                    Response.print_table(response_afe, time_start, errors_only=True)

            input("Press Enter to start acquisition...")

            log.info("Starting acquisition")
            time_start = time.time()
            response_acq = intf.send(cmds_acq)

            responses_flat = []
            for response_list in response_acq:
                responses_flat.extend(response_list)

            if any([response.error_code for response in responses_flat]):
                Response.print_table(response_acq, time_start, errors_only=True)

            log.info("Command sequences executed successfully")
    except Exception as e:
        log.exception(f"Error during command execution: {e}")
    finally:
        stop_event.set()
        udp_thread.join(2.0)

    total_bytes = sum(len(packet) for packet, _, _ in received_packets)
    # # total_bytes = sum(len(r.data) for r in data_responses)
    # expected_bytes = NUM_SHOTS * len(list(filter(lambda c: isinstance(c, TriggerShot), cmd))) * 84042

    min_time = min(t for _, t, _ in received_packets) if received_packets else 0
    max_time = max(t for _, t, _ in received_packets) if received_packets else 0
    duration = max_time - min_time
    data_rate = total_bytes * 8 / duration if duration > 0 else 0
    log.info(
        f"{total_bytes} bytes in {duration:.3f} s, Data rate: {data_rate/1e6:.3f} Mbps"
    )
    # print(
    #     f"UDP responses: {[packet.decode(errors='ignore') for packet, _ in received_packets]}"
    # )

    log.debug("Received packets:")
    for packet, t, addr in received_packets:
        log.debug(f"  From {addr} at {t:.3f}: {len(packet)} bytes")

    # If received data is not empty, save as binary
    if received_packets:
        filename = (
            f"{args.output_dir}/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
        )
        with open(filename, "wb") as f:
            for packet, _, _ in received_packets:
                f.write(packet)
        with open(f"{args.output_dir}/latest.bin", "wb") as f:
            for packet, _, _ in received_packets:
                f.write(packet)

        # import numpy as np

        # np.save(
        #     filename,
        #     np.concatenate(
        #         [
        #             np.frombuffer(packet, dtype=np.uint8)
        #             for packet, _, _ in received_packets
        #         ]
        #     ),
        # )

        # np.save(
        #     "data/latest."
        # )

        log.info(
            f"Saved received data to '{filename}' and '{args.output_dir}/latest.bin'"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Standalone acquisition script using configuration file"
    )
    parser.add_argument(
        "config",
        type=str,
        help="Path to the configuration JSON file",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="Directory to save the output data",
        default="data",
    )
    args = parser.parse_args()
    main(args.config)

import time
import logging
from typing import Optional

from tinyprobe.protocol.commands import TinyProbeCmdSeq, TriggerShot
from tqdm import tqdm

TP_COM_PACKET_BASE_SIZE = 1000


class TPCom:
    def __init__(self, packet_size: int, log: Optional[int | logging.Logger] = None):
        if isinstance(log, logging.Logger):
            self._log = log
        else:
            self._log = logging.getLogger(self.__class__.__name__)
            if isinstance(log, int):
                self._log.setLevel(log)

        self.packet_size = packet_size
        self.connected = False

    def open(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}/open\tNot implemented")

    def close(self):
        raise NotImplementedError(f"{self.__class__.__name__}/close\tNot implemented")

    def ping(self) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}/ping\tNot implemented")

    def send(self, data: bytes) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__}/send\tNot implemented")

    def receive(self, len: int) -> bytes:
        raise NotImplementedError(f"{self.__class__.__name__}/receive\tNot implemented")

    def send_cmd_seq(self, cmd_seq: TinyProbeCmdSeq, sleep_s: int = 1) -> bool:
        packets = cmd_seq.get_formatted_packets()
        if packets is None:
            self._log.warning("Failed to get formatted packets")
            return False
        packets = packets[0]

        n_shots_rx = 0
        for cmd in cmd_seq.cmd_list:
            if isinstance(cmd, TriggerShot):
                n_shots_rx += cmd.n_shots

        for packet in packets:
            if not self.send(packet):
                self._log.warning("Failed to send packet")
                return False
            if sleep_s is not None:
                time.sleep(sleep_s)

        self._log.info(f"Sent {len(packets)} packet(s)")
        return True

    def receive_shots(
        self, n_packets: int, n_shots: int, print_stats: bool = True
    ) -> tuple[bytes, float]:
        data = []
        pkgs_idx_list = []
        bytes_total = b""

        start_time = time.time()
        start_time_data = None

        concat_packets = (self.packet_size - 2) // TP_COM_PACKET_BASE_SIZE

        # Initialize progress bar for shots
        progress_bar = tqdm(
            total=n_shots, desc="Receiving Shots", unit="shots", ascii=True
        )

        while n_shots > 0:
            n_packets_concat = (n_packets + (concat_packets - 1)) // concat_packets
            while n_packets_concat > 0:
                packet = self.receive(self.packet_size)
                if packet == b"":
                    self._log.warning("Failed to receive packet")
                    progress_bar.close()
                    return bytes_total, 0

                pkg_idx = int.from_bytes(packet[:2], "little")
                for i in range(concat_packets):
                    data.append(
                        packet[
                            2 + i * TP_COM_PACKET_BASE_SIZE : 2
                            + (i + 1) * TP_COM_PACKET_BASE_SIZE
                        ]
                    )
                    pkgs_idx_list.append(pkg_idx * concat_packets + i)

                if start_time_data is None:
                    start_time_data = time.time()

                n_packets_concat -= 1

            n_shots -= 1
            progress_bar.update(1)

        progress_bar.close()

        end_time = time.time()

        for packet in data:
            bytes_total = bytes_total + packet

        if print_stats:
            self._log.info("Received:")
            self._log.info(
                f"  Packet size:            {len(bytes_total) // len(data)} B\n"
            )
            self._log.info(f"  Number of packets:      {len(data)}\n")
            self._log.info(f"  Total shot time:        {end_time - start_time:.2f} s\n")

            if start_time_data is not None:
                self._log.info(
                    f"  Data transmission time: {end_time - start_time_data:.2f} s"
                )

        return bytes_total, (end_time - start_time_data) if start_time_data else -1

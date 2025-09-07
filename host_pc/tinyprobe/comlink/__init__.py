import time

from tinyprobe.protocol.commands import TinyProbeCmdSeq, TriggerShot
from tqdm import tqdm

TP_COM_PACKET_BASE_SIZE = 1000


class TPCom:
    def __init__(self, packet_size: int):
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
        packets = cmd_seq.get_formatted_packets()[0]

        n_shots_rx = 0
        for cmd in cmd_seq.cmd_list:
            if isinstance(cmd, TriggerShot):
                n_shots_rx += cmd.n_shots

        for packet in packets:
            if not self.send(packet):
                print("[TP/Com/send]\tFailed to send packet")
                return False
            if sleep_s is not None:
                time.sleep(sleep_s)

        print("[TP/Com/send]\tSent", len(packets), "packet(s)")
        return True

    def receive_shots(
        self, n_packets: int, n_shots: int, print_stats: bool = True
    ) -> tuple[bytes, float]:
        data = []
        pkgs_idx_list = []
        bytes_total = b""

        start_time = time.time()

        indicator = 0

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
                    print("[TP/Com/recv]\tFailed to receive packet")
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

                if indicator == 0:
                    start_time_data = time.time()
                    indicator = 1

                n_packets_concat -= 1

            n_shots -= 1
            progress_bar.update(1)

        progress_bar.close()

        end_time = time.time()

        for packet in data:
            bytes_total = bytes_total + packet

        if print_stats:
            print(
                "[TP/Com/recv]\tReceived:\n"
                f"[TP/Com/recv]\t  Packet size:            {len(bytes_total) // len(data)} B\n"
                f"[TP/Com/recv]\t  Number of packets:      {len(data)}\n"
                f"[TP/Com/recv]\t  Total shot time:        {end_time - start_time:.2f} s\n"
                f"[TP/Com/recv]\t  Data transmission time: {end_time - start_time_data:.2f} s"
            )

        return bytes_total, (end_time - start_time_data)

import socket

from tinyprobe.comlink import TPCom


TP_COM_MAX_UDP_PACKET_SIZE = 1472


class TPComWiFi4(TPCom):
    def __init__(
        self,
        ip: str,
        port: int = 50007,
        packet_size: int = 1002,
        timeout: int = 5,
    ):
        super().__init__(packet_size)

        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.socket = None

    def open(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            self.socket.bind(("", self.port))
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, int(20 * 1e8))
            self.connected = True
            print(f"[TP/Com/WiFi4/open]\tConnected to {self.ip}:{self.port}")
        except Exception as e:
            print(f"[TP/Com/WiFi4/open]\tFailed to connect: {e}")
            self.socket = None
            self.connected = False

        return self.connected

    def close(self):
        if self.socket:
            self.socket.close()
            self.connected = False
            print(f"[TP/Com/WiFi4/close]\tDisconnected from {self.ip}:{self.port}")
        else:
            print("[TP/Com/WiFi4/close]\tNo active connection to disconnect.")

    def send(self, data: bytes) -> bool:
        if not self.connected:
            print("[TP/Com/WiFi4/send]\tNot connected. Cannot send data.")
            return False

        try:
            self.socket.sendto(data, (self.ip, self.port))
            return True
        except Exception as e:
            print(f"[TP/Com/WiFi4/send]\tFailed to send data: {e}")
            return False

    def receive(self, length: int) -> bytes:
        if not self.connected:
            print("[TP/Com/WiFi4/recv]\tNot connected. Cannot receive data.")
            return b""

        try:
            to_receive = length
            received_bytes = b""

            while to_receive > 0:
                chunk_size = min(to_receive, TP_COM_MAX_UDP_PACKET_SIZE)
                chunk, addr = self.socket.recvfrom(chunk_size)
                received_bytes += chunk
                to_receive -= len(chunk)

                if addr != (self.ip, self.port):
                    print(
                        f"[TP/Com/WiFi4/recv]\tReceived data from unexpected address: {addr}, expected {(self.ip, self.port)}"
                    )

            return received_bytes

        except socket.timeout:
            print("[TP/Com/WiFi4/recv]\tReceive timed out.")
            return b""
        except Exception as e:
            print(f"[TP/Com/WiFi4/recv]\tFailed to receive data: {e}")
            return b""

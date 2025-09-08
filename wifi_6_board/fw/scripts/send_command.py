import socket
import sys
import time
import argparse
# from scapy.all import sniff, UDP, IP
# from scapy.config import conf

TP_CMD_PING = 0
TP_CMD_EN_REPLIES = 1
TP_CMD_SW_MUX = 2
TP_CMD_WRITE_SPI = 3
TP_CMD_WRITE_FPGA = 4
TP_CMD_WRITE_AFE = 5
TP_CMD_WRITE_TX = 6
TP_CMD_DELAY_NS = 7
TP_CMD_SLEEP_MS = 8
TP_CMD_CTRL_PWR = 9
TP_CMD_TRIGGER_SHOT = 10
TP_CMD_ID_MAX = 11

TP_CMD_LENGTHS = [1, 1, 1, 1, 5, 4, 6, 8, 4, 2, 4]

CMD_PING = {
    "id": 0,
    "length": [1],
    "description": "Ping"
}

CMD_EN_REPLIES = {
    "id": 1,
    "length": [1],
    "description": "Enable Replies"
}

CMD_SLEEP_MS = {
    "id": 8,
    "length": [4],
    "description": "Sleep (ms)"
}

CMD_TRIGGER_SHOT = {
    "id": 10,
    "length": [2, 2],
    "description": "Trigger shot and data acquisition"
}

def parse_commands(commands, args):
    result = bytes()

    # first two bytes is the amount of commands
    result += len(commands).to_bytes(2, byteorder="little")

    for command, arg in zip(commands, args):
        # command id
        result += command["id"].to_bytes(1, byteorder="little")

        result += sum(command["length"]).to_bytes(2, byteorder="little")

        # print(f"Command: {command['description']} with id {command['id']} and lengths [{len(arg)}]")
        # print(f"       > {command['id'].to_bytes(1, byteorder='little')}, {sum(command['length']).to_bytes(2, byteorder='little')}")

        # command length
        for length, a in zip(command["length"], arg):
            # print(f"  Argument: {a} with length {length}")
            # print(f"       > {a.to_bytes(length, byteorder='little')}")
            result += a.to_bytes(length, byteorder="little")

    return result

received_data = b''

def send_udp_packet(dest_ip, dest_port, message, timeout):

    global received_data

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", dest_port))
    sock.settimeout(timeout)

    end_time = None
    num_packets = 0
    packet_sizes = []

    try:
        # Send the message
        sock.sendto(message, (dest_ip, dest_port))
        print(f"Message sent to {dest_ip}:{dest_port}")

        # Receive a response
        print("Waiting for response...")
        
        start_time = time.time()
        data, addr = sock.recvfrom(10000)
        while data:
            num_packets += 1
            packet_sizes.append(len(data))
            data, addr = sock.recvfrom(10000)
            end_time = time.time()
            received_data += data

    except socket.timeout:
        # print("Timeout occurred while waiting for response")
        if end_time is not None:
            # print("Received data: ", received_data[:100])

            print()
            print('     ', ' '.join(f"{i:02x}" for i in range(16)), ' ', 'ASCII')
            for i in range(0, len(received_data), 16):
                print(f"{i:04x}:", ' '.join(f"{b:02x}" for b in received_data[i:i+16]), '  ', end='')

                if i + 16 > len(received_data):
                    print('   ' * (16 - len(received_data) % 16), end='')

                print(''.join(chr(b) if 32 <= b <= 126 else '.' for b in received_data[i:i+16]))

            print()
            # print("Received data: ", received_data[:100])

            average_packet_size = sum(packet_sizes) / len(packet_sizes)
            total_received = sum(packet_sizes)
            throughput = total_received / (end_time - start_time)
            print(f"Received {total_received} bytes in {end_time - start_time} seconds ({throughput * 8 / 1000000:.2f} mbps)")
        else:
            print("No response received")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the socket
        sock.close()

    # # Define the destination port you want to filter
    # DEST_PORT = 2121  # Change this to the desired destination port
    # # DEST_IFACE = "ASIX USB to Gigabit Ethernet Family Adapter"
    # DEST_IFACE = "Intel(R) Wi-Fi 6 AX200 160MHz"

    # sock.sendto(message, (dest_ip, dest_port))
    # print(f"Message sent to {dest_ip}:{dest_port}")

    # print(f"Listening for UDP packets to port {DEST_PORT} for 5 seconds...")

    # # Capture packets for 10 seconds and store them in the list
    # captured_packets = sniff(filter=f"udp and dst port {DEST_PORT}", timeout=5, iface=DEST_IFACE)

    # if len(captured_packets) == 0:
    #     print("No packets captured")
    #     return
    # # Get time of first and last packet
    # start_time = captured_packets[0].time
    # end_time = captured_packets[-1].time

    # # Process the captured packets
    # num_packets = len(captured_packets)
    # average_size = sum([len(p) - 42 for p in captured_packets]) / num_packets
    # print(f"Captured {num_packets} packets of average length {int(average_size)} bytes in {end_time - start_time:.2f} seconds")
    # throughput = average_size * num_packets * 8 / 1000000 / (end_time - start_time)
    # print(f"Throughput: {throughput:.2f} mbps")

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Send a command to the target device")
    arg_parser.add_argument("dest_ip", type=str, help="Destination IP address")
    arg_parser.add_argument("dest_port", type=int, help="Destination port number")
    arg_parser.add_argument("--timeout", type=float, default=2, help="Timeout in seconds")
    args = arg_parser.parse_args()

    # print(conf.ifaces)
    
    # commands = [CMD_PING]
    # args = [[0]]
    commands = [CMD_PING, CMD_SLEEP_MS, CMD_PING, CMD_SLEEP_MS, CMD_PING, CMD_SLEEP_MS, CMD_PING]
    values = [[0], [100], [0], [100], [0], [100], [0]]
    # commands = [CMD_PING, CMD_SLEEP_MS, CMD_PING, CMD_TRIGGER_SHOT]
    # args = [[0], [1000], [0], [100, 10000]]
    # commands = [CMD_TRIGGER_SHOT]
    # args = [[num_acqs, num_packets]]
    # commands = [CMD_PING]
    # args = [[]]

    message = parse_commands(commands, values)

    # print(f"Sending message: {message}")

    send_udp_packet(args.dest_ip, args.dest_port, message, args.timeout)
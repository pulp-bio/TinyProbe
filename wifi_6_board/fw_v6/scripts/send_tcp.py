import socket


MESSAGE = b'Test message from TinyProbe TCP script'
PORT = 2121
IP = '192.168.50.223'

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((IP, PORT))
        print(f"Connected to {IP}:{PORT}")

        sock.sendall(MESSAGE)
        print(f"Sent message: {MESSAGE}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sock.close()
        print("Socket closed")

if __name__ == "__main__":
    main()
import socket
from config import HOST, PORT
from protocol.handshake import (
    send_greeting,
    receive_compatibility_response,
    receive_queue_request,
    send_queue_position
)

class EVEServer:
    def __init__(self, host=HOST, port=PORT, queue_position=1):
        self.host = host
        self.port = port
        self.queue_position = queue_position
        self.socket = None

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)

        print(f"[*] Server running on {self.host}:{self.port}")
        print("[*] Waiting for client...")

        while True:
            client, addr = self.socket.accept()
            print(f"\n[+] Connection from {addr}")
            self.handle_client(client)
            client.close()

    def handle_client(self, client):
        try:
            send_greeting(client)
            print("[1] Greeting sent")

            if not receive_compatibility_response(client):
                print("[-] Invalid compatibility response")
                return
            print("[2] ✅ Compatibility response OK")

            queue_req = receive_queue_request(client)
            if not queue_req or b'QC' not in queue_req:
                print("[-] Unexpected queue request")
                return
            print("[3] ✅ Queue check (QC) received")

            send_queue_position(client, self.queue_position)
            print(f"[4] Queue position sent: {self.queue_position}")

            print("\n🎉 SUCCESS! Client should show 'Status: OK'")

        except Exception as e:
            print(f"[-] Error: {e}")
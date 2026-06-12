import struct
from protocol.serializer import macho_dumps
from utils.socket_utils import recv_exact

def build_greeting():
    return (
        170472,
        414,
        0,
        13.08,
        958007,
        "EVE-TRANQUILITY@ccp",
        None
    )

def send_greeting(client_socket):
    payload = macho_dumps(build_greeting())
    framed = struct.pack('<I', len(payload)) + payload
    client_socket.sendall(framed)

def receive_compatibility_response(client_socket):
    header = recv_exact(client_socket, 4)
    if not header:
        return None
    length = struct.unpack('<I', header)[0]
    data = recv_exact(client_socket, length)
    if data and data.startswith(b'~\x00\x00\x00\x00\x14\x06'):
        return data
    return None

def receive_queue_request(client_socket):
    header = recv_exact(client_socket, 4)
    if not header:
        return None
    length = struct.unpack('<I', header)[0]
    return recv_exact(client_socket, length)

def send_queue_position(client_socket, position):
    payload = macho_dumps(position)
    framed = struct.pack('<I', len(payload)) + payload
    client_socket.sendall(framed)
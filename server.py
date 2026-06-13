import socket
import struct
import time
import logging
import hashlib
from config import HOST, PORT
from protocol.serializer import macho_dumps
from protocol.deserializer import macho_loads
from utils.socket_utils import recv_exact
from handlers.auth_handler import AuthHandler
from database.models.character import CharacterModel

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class EVEServer:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.auth_handler = AuthHandler()
        self.char_model = CharacterModel()
        
    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        
        logger.info(f"🚀 Placebo Server on {self.host}:{self.port}")
        
        while True:
            client, addr = server.accept()
            logger.info(f"📡 Connection from {addr}")
            self.handle_client(client, addr)
            client.close()
    
    def handle_client(self, client, addr):
        try:
            # ========== 1. VersionExchange ==========
            greeting = (170472, 414, 0, 13.08, 958007, "EVE-TRANQUILITY@ccp", None)
            self._send(client, greeting)
            logger.info("[1] VersionExchange sent")
            
            # ========== 2. Client Version ==========
            client_version = self._recv(client)
            logger.info(f"[2] Client version received")
            
            # ========== 3. QC ==========
            qc = self._recv(client)
            logger.info(f"[3] QC: {qc}")
            
            # ========== 4. Queue position ==========
            self._send(client, 1)
            logger.info("[4] Queue position sent")
            
            # ========== 5. Placebo request ==========
            logger.info("[5] Sending placebo request...")
            placebo_request = ('placebo', {})
            self._send(client, placebo_request)
            logger.info("[5] Placebo request sent")
            
            # ========== 6. OK CC ==========
            logger.info("[6] Waiting for OK CC...")
            ok_cc = self._recv(client)
            logger.info(f"[6] OK CC: {ok_cc}")
            
            # ========== 7. Server challenge ==========
            logger.info("[7] Sending server challenge...")
            server_challenge = "A" * 64
            signed_func = ""
            context = {}
            response_dict = {
                'challenge_responsehash': "placeholder_hash",
                'macho_version': 414,
                'boot_version': 13.08,
                'boot_build': 958007,
                'boot_codename': "EVE-TRANQUILITY",
                'boot_region': "ccp",
                'cluster_usercount': 0,
                'proxy_nodeid': 0,
                'user_logonqueueposition': 1,
                'config_vals': {}
            }
            
            server_challenge_packet = (server_challenge, signed_func, context, response_dict)
            self._send(client, server_challenge_packet)
            logger.info("[7] Server challenge sent")
            
            # ========== 8. Client challenge response ==========
            logger.info("[8] Waiting for client challenge response...")
            challenge_response = self._recv(client)
            logger.info(f"[8] Challenge response received")
            
            # Извлекаем clientChallenge
            client_challenge = None
            if isinstance(challenge_response, tuple) and len(challenge_response) >= 1:
                client_challenge = challenge_response[0]
            
            # ========== 9. Authentication Response ==========
            username = "test"
            password = "test"
            
            auth_response = self.auth_handler.handle_login(username, password, addr[0])
            if isinstance(auth_response, bytes):
                client.sendall(struct.pack('<I', len(auth_response)) + auth_response)
            else:
                self._send(client, auth_response)
            logger.info("[9] Auth response sent")
            
            # ========== 10. Final ACK ==========
            logger.info("[10] Waiting for final ack...")
            client.settimeout(5)
            try:
                final = self._recv(client)
                if final:
                    logger.info(f"[10] Final ack received")
            except socket.timeout:
                logger.info("[10] Timeout")
            finally:
                client.settimeout(None)
            
            # ========== 11. Character list from database ==========
            logger.info("[11] Fetching character list from database...")
            
            # Получаем персонажей для accountID = 1 (test user)
            characters_db = self.char_model.get_by_account(1)
            
            character_tuples = []
            for char in characters_db:
                char_tuple = (
                    char['characterID'],
                    char['characterName'],
                    char.get('typeID', 1383),
                    char.get('corporationID', 1000169),
                    char.get('balance', 0.0),
                    char.get('securityRating', 0.0),
                    char.get('locationID', 30000142),
                    char.get('skillPoints', 0),
                    char.get('gender', 0),
                    char.get('ancestryID', 1),
                    char.get('bloodlineID', 1),
                    char.get('raceID', 1),
                )
                character_tuples.append(char_tuple)
            
            characters = tuple(character_tuples)
            logger.info(f"[11] Sending {len(characters)} character(s): {[c[1] for c in character_tuples]}")
            self._send(client, characters)
            logger.info("[11] Character list sent")
            
            # ========== 12. Character selection ==========
            logger.info("[12] Waiting for character selection...")
            select_request = self._recv(client)
            logger.info(f"[12] Character selection: {select_request}")
            
            # Извлекаем ID выбранного персонажа
            selected_char_id = None
            if isinstance(select_request, tuple) and len(select_request) > 0:
                selected_char_id = select_request[0]
            elif isinstance(select_request, int):
                selected_char_id = select_request
            
            logger.info(f"[12] Selected character ID: {selected_char_id}")
            
            # ========== 13. Selection response ==========
            logger.info("[13] Sending character selection response...")
            select_response = (
                selected_char_id or 90000001,
                1,  # queue_position (1 = можно входить)
                {
                    'server': 'EVE-TRANQUILITY@ccp',
                    'address': '127.0.0.1',
                    'port': 26000,
                    'node_id': 0
                }
            )
            self._send(client, select_response)
            logger.info(f"[13] Character selection response sent for ID: {selected_char_id}")
            
            # ========== 14. Game loop ==========
            logger.info("[14] Entering game loop... Client should now see the game world!")
            
            # Держим соединение открытым
            while True:
                client.settimeout(60)
                try:
                    data = self._recv(client)
                    if data:
                        logger.debug(f"Game data: {data}")
                except socket.timeout:
                    # Отправляем ping
                    self._send(client, None)
                except:
                    break
                    
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
    
    def _send(self, client, obj):
        data = macho_dumps(obj)
        framed = struct.pack('<I', len(data)) + data
        client.sendall(framed)
        logger.debug(f"  Sent {len(data)} bytes")
    
    def _recv(self, client):
        header = recv_exact(client, 4)
        if not header:
            return None
        length = struct.unpack('<I', header)[0]
        logger.debug(f"  Expecting {length} bytes")
        data = recv_exact(client, length)
        if not data:
            return None
        logger.debug(f"  Received {len(data)} bytes")
        try:
            return macho_loads(data)
        except Exception as e:
            logger.warning(f"Deserialization error: {e}")
            return data


if __name__ == "__main__":
    server = EVEServer()
    server.start()
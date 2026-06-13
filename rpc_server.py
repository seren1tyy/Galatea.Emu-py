import socket
import struct
import logging
from config import HOST, PORT
from protocol.serializer import macho_dumps, macho_loads
from utils.socket_utils import recv_exact

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RPCNode:
    """Узел, обрабатывающий RPC вызовы от клиента."""
    
    def __init__(self, client_socket, addr):
        self.client = client_socket
        self.addr = addr
        self.services = {}
        self.user_id = None
        self.session_id = None
        
        # Регистрируем сервисы
        self._register_services()
    
    def _register_services(self):
        """Регистрация доступных сервисов."""
        from services.auth_service import AuthService
        from services.account_service import AccountService
        from services.character_service import CharacterService
        
        self.services['authentication'] = AuthService(self)
        self.services['account'] = AccountService(self)
        self.services['character'] = CharacterService(self)
    
    def handle(self):
        """Основной цикл обработки."""
        try:
            # Ждём вызовы
            while True:
                header = recv_exact(self.client, 4)
                if not header:
                    break
                
                length = struct.unpack('<I', header)[0]
                data = recv_exact(self.client, length)
                if not data:
                    break
                
                # Десериализуем вызов
                call_obj = macho_loads(data)
                logger.info(f"RPC Call: {call_obj}")
                
                # Обрабатываем
                response = self._dispatch_call(call_obj)
                
                # Отправляем ответ
                resp_data = macho_dumps(response)
                framed = struct.pack('<I', len(resp_data)) + resp_data
                self.client.sendall(framed)
                
        except Exception as e:
            logger.error(f"RPC error: {e}", exc_info=True)
        finally:
            self.client.close()
    
    def _dispatch_call(self, call_obj):
        """Маршрутизация вызова к соответствующему сервису."""
        # Формат вызова: (service_name, method_name, args, kwargs)
        if isinstance(call_obj, tuple) and len(call_obj) >= 3:
            service_name = call_obj[0]
            method_name = call_obj[1]
            args = call_obj[2] if len(call_obj) > 2 else ()
            kwargs = call_obj[3] if len(call_obj) > 3 else {}
            
            logger.info(f"Service: {service_name}, Method: {method_name}")
            logger.info(f"Args: {args}, Kwargs: {kwargs}")
            
            if service_name in self.services:
                service = self.services[service_name]
                if hasattr(service, method_name):
                    method = getattr(service, method_name)
                    try:
                        return method(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Method error: {e}")
                        return self._error_response(str(e))
                else:
                    logger.warning(f"Method {method_name} not found in {service_name}")
                    return self._error_response(f"Method {method_name} not found")
            else:
                logger.warning(f"Service {service_name} not found")
                return self._error_response(f"Service {service_name} not found")
        
        logger.warning(f"Invalid call format: {call_obj}")
        return self._error_response("Invalid call format")
    
    def _error_response(self, message):
        """Сформировать ответ с ошибкой."""
        return ("error", message)


class EVEServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = None
    
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        
        logger.info(f"🚀 RPC Server running on {self.host}:{self.port}")
        
        while True:
            client, addr = self.socket.accept()
            logger.info(f"📡 Connection from {addr}")
            node = RPCNode(client, addr)
            node.handle()


if __name__ == "__main__":
    server = EVEServer()
    server.start()
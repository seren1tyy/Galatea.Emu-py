"""RPC handler for EVE service calls."""

import logging
from protocol.serializer import macho_dumps
from protocol.deserializer import macho_loads

logger = logging.getLogger(__name__)


class RPCHandler:
    """Обработчик RPC вызовов от клиента."""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    def handle_call(self, call_data: bytes, client) -> bytes:
        """Обработать RPC вызов."""
        try:
            # Десериализуем вызов
            call_obj = macho_loads(call_data)
            logger.info(f"RPC Call: {call_obj}")
            
            # Формат вызова обычно: (service_name, method_name, args, kwargs)
            if isinstance(call_obj, tuple) and len(call_obj) >= 3:
                service_name = call_obj[0]
                method_name = call_obj[1]
                args = call_obj[2] if len(call_obj) > 2 else ()
                kwargs = call_obj[3] if len(call_obj) > 3 else {}
                
                logger.info(f"Service: {service_name}, Method: {method_name}")
                logger.info(f"Args: {args}")
                logger.info(f"Kwargs: {kwargs}")
                
                # Маршрутизация на соответствующий обработчик
                if service_name == "authentication":
                    return self._handle_auth(method_name, args, kwargs, client)
                elif service_name == "account":
                    return self._handle_account(method_name, args, kwargs, client)
                else:
                    logger.warning(f"Unknown service: {service_name}")
                    return self._error_response("Unknown service")
            
            return self._error_response("Invalid call format")
            
        except Exception as e:
            logger.error(f"RPC error: {e}", exc_info=True)
            return self._error_response(str(e))
    
    def _handle_auth(self, method: str, args, kwargs, client) -> bytes:
        """Обработка вызовов authentication сервиса."""
        logger.info(f"Auth method: {method}")
        
        if method == "Ping":
            # Возвращаем текущее время (как в EVEmu)
            import time
            response = int(time.time() * 10000000)  # FileTime format
            return macho_dumps(response)
        
        elif method == "GetPostAuthenticationMessage":
            # Возвращаем None или сообщение
            return macho_dumps(None)
        
        elif method == "AmUnderage":
            return macho_dumps(False)
        
        elif method == "AccruedTime":
            return macho_dumps(0)
        
        elif method == "SetLanguageID":
            return macho_dumps(None)
        
        else:
            logger.warning(f"Unhandled auth method: {method}")
            return macho_dumps(None)
    
    def _handle_account(self, method: str, args, kwargs, client) -> bytes:
        """Обработка вызовов account сервиса."""
        logger.info(f"Account method: {method}")
        
        if method == "GetCashBalance":
            # Возвращаем баланс ISK
            # Временно 1,000,000 ISK
            return macho_dumps(1000000.0)
        
        elif method == "GetKeyMap":
            # Возвращаем типы ключей аккаунта
            return macho_dumps({})  # Пустой словарь для начала
        
        elif method == "GetEntryTypes":
            # Возвращаем типы записей журнала
            return macho_dumps({})
        
        elif method == "GetJournal":
            # Возвращаем пустой журнал
            return macho_dumps([])
        
        else:
            logger.warning(f"Unhandled account method: {method}")
            return macho_dumps(None)
    
    def _error_response(self, message: str) -> bytes:
        """Сформировать ответ с ошибкой."""
        error_tuple = ("error", message)
        return macho_dumps(error_tuple)
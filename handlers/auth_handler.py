"""Authentication handler for EVE server emulator."""

import logging
import hashlib
from database.models.account import AccountModel
from database.models.character import CharacterModel
from database.models.session import SessionModel
from protocol.serializer import macho_dumps

logger = logging.getLogger(__name__)


class AuthHandler:
    """Обработчик аутентификации и управления сессиями."""
    
    def __init__(self):
        self.accounts = AccountModel()
        self.characters = CharacterModel()
        self.sessions = SessionModel()
    
    @staticmethod
    def generate_eve_password_hash(username: str, password: str) -> bytes:
        """Генерация хеша пароля как в EVE Online."""
        username_utf16 = username.lower().strip().encode('utf-16le')
        password_utf16 = password.encode('utf-16le')
        
        sha1 = hashlib.sha1()
        sha1.update(password_utf16)
        sha1.update(username_utf16)
        current_hash = sha1.digest()
        
        for _ in range(1000):
            sha1 = hashlib.sha1()
            sha1.update(current_hash)
            sha1.update(username_utf16)
            current_hash = sha1.digest()
        
        return current_hash
    
    def handle_login(self, username: str, password_or_hash, ip: str) -> bytes:
        """
        Обработка логина.
        
        Пароль может быть:
        - plain text (user_password)
        - хеш (user_password_hash)
        """
        logger.info(f"🔐 Login attempt: {username} from {ip}")
        
        # Нормализуем username
        normalized_username = username.lower().strip()
        account = self.accounts.get_by_username(normalized_username)
        
        if not account:
            logger.warning(f"❌ Account not found: {normalized_username}")
            return self._error_response("Invalid username or password")
        
        # Проверяем пароль
        password_ok = True
        
        # Если пришёл хеш (bytes), сравниваем с хешем в БД
        if isinstance(password_or_hash, bytes):
            stored_hash = account.get('hash')
            if stored_hash:
                if password_or_hash == stored_hash:
                    password_ok = True
                else:
                    logger.warning(f"Hash mismatch for: {normalized_username}")
        
        # Если пришёл plain text
        elif isinstance(password_or_hash, str):
            stored_password = account.get('password')
            if stored_password and stored_password == password_or_hash:
                password_ok = True
            else:
                # Пробуем сгенерировать хеш и сравнить
                generated_hash = self.generate_eve_password_hash(normalized_username, password_or_hash)
                stored_hash = account.get('hash')
                if stored_hash and generated_hash == stored_hash:
                    password_ok = True
        
        if not password_ok:
            logger.warning(f"❌ Invalid password for: {normalized_username}")
            return self._error_response("Invalid username or password")
        
        # Успешный логин
        # Формат AuthenticationRsp из AccountPkts.xml
        auth_response = (
            {  # server_info_dict
                'version.project': 'EVE',
                'version.build': 958007,
                'version.number': 13.08
            },
            account['accountID'],  # accountID
            account.get('role', 0),  # role
            None,  # substream (может быть None)
            0  # proxyNodeID
        )
        
        logger.info(f"✅ Login successful: {normalized_username} (ID: {account['accountID']})")
        
        # Сериализуем ответ
        return macho_dumps(auth_response)
    
    def _error_response(self, message: str) -> bytes:
        """Сформировать ответ с ошибкой."""
        error_tuple = ("error", message)
        return macho_dumps(error_tuple)
    
    def handle_character_list(self, session_id: str) -> bytes:
        """Обработка запроса списка персонажей."""
        return macho_dumps(())
    
    def handle_select_character(self, session_id: str, character_id: int) -> bytes:
        """Обработка выбора персонажа."""
        select_response = (
            character_id,
            1,
            {
                'server': 'EVE-TRANQUILITY@ccp',
                'address': '127.0.0.1',
                'port': 26000,
                'node_id': 0
            }
        )
        return macho_dumps(select_response)
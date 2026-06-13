# database/models/account.py

import hashlib
import secrets
from typing import Optional, Dict, Any, List
from database.db import get_db
import logging

logger = logging.getLogger(__name__)


class AccountModel:
    """Модель для управления аккаунтами."""
    
    TABLE = 'account'
    
    @staticmethod
    def generate_eve_password_hash(username: str, password: str) -> bytes:
        """Генерация хеша пароля как в EVE Online."""
        username_utf16 = username.lower().strip().encode('utf-16le')
        password_utf16 = password.encode('utf-16le')
        
        import hashlib
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
    
    def get_by_id(self, account_id: int) -> Optional[Dict]:
        """Получить аккаунт по ID."""
        db = get_db()
        return db.query_one(
            "SELECT * FROM account WHERE accountID = %s",
            (account_id,)
        )
    
    def get_by_username(self, username: str) -> Optional[Dict]:
        """Получить аккаунт по имени пользователя."""
        db = get_db()
        return db.query_one(
            "SELECT accountID, accountName, password, hash, role, banned, logonCount, lastLogin FROM account WHERE accountName = %s",
            (username,)
        )
    
    def authenticate(self, username: str, password: str, ip: str) -> Optional[Dict]:
        """Аутентификация пользователя."""
        db = get_db()
        
        normalized_username = username.lower().strip()
        account = self.get_by_username(normalized_username)
        
        if not account:
            logger.warning(f"Account not found: {normalized_username}")
            return None
        
        # Проверка пароля (простая для теста)
        stored_password = account.get('password')
        if stored_password and stored_password != password:
            logger.warning(f"Invalid password for: {normalized_username}")
            return None
        
        # Обновляем данные
        db.execute(
            "UPDATE account SET logonCount = logonCount + 1, lastLogin = CURRENT_TIMESTAMP, online = 1 WHERE accountID = %s",
            (account['accountID'],)
        )
        
        logger.info(f"✅ Login successful: {normalized_username}")
        return account
    
    def update_last_login(self, account_id: int, ip: str = None):
        """Обновить время последнего входа."""
        db = get_db()
        db.execute(
            "UPDATE account SET lastLogin = CURRENT_TIMESTAMP, online = 1 WHERE accountID = %s",
            (account_id,)
        )
"""Модель для управления сессиями."""

import secrets
import time
from typing import Optional, Dict
from database.db import get_db
import logging

logger = logging.getLogger(__name__)


class SessionModel:
    """Модель для управления сессиями (таблица может быть новой)."""
    
    def __init__(self):
        self._ensure_session_table()
    
    def _ensure_session_table(self):
        """Создать таблицу сессий, если её нет."""
        db = get_db()
        if not db.table_exists('user_sessions'):
            db.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id VARCHAR(64) PRIMARY KEY,
                    account_id INT UNSIGNED NOT NULL,
                    character_id INT UNSIGNED DEFAULT NULL,
                    username VARCHAR(43) NOT NULL,
                    created_at INT UNSIGNED NOT NULL,
                    last_activity INT UNSIGNED NOT NULL,
                    expires_at INT UNSIGNED NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    INDEX idx_account (account_id),
                    INDEX idx_expires (expires_at),
                    FOREIGN KEY (account_id) REFERENCES account(accountID) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """)
            logger.info("Created user_sessions table")
    
    def create_session(self, account_id: int, username: str, ip: str = None) -> str:
        """Создать новую сессию."""
        db = get_db()
        session_id = secrets.token_hex(32)
        now = int(time.time())
        expires_at = now + 7200  # 2 часа
        
        db.insert('user_sessions', {
            'session_id': session_id,
            'account_id': account_id,
            'username': username,
            'created_at': now,
            'last_activity': now,
            'expires_at': expires_at,
            'ip_address': ip
        })
        
        # Обновляем session_sid в таблице account
        db.execute(
            "UPDATE account SET session_sid = ? WHERE accountID = ?",
            (session_id, account_id)
        )
        
        logger.info(f"Created session {session_id[:16]}... for account {account_id}")
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Проверить валидность сессии."""
        db = get_db()
        now = int(time.time())
        
        session = db.query_one(
            "SELECT * FROM user_sessions WHERE session_id = ? AND expires_at > ?",
            (session_id, now)
        )
        
        if session:
            # Обновляем время активности
            db.execute(
                "UPDATE user_sessions SET last_activity = ? WHERE session_id = ?",
                (now, session_id)
            )
        
        return session
    
    def update_character(self, session_id: str, character_id: int):
        """Привязать персонажа к сессии."""
        db = get_db()
        db.execute(
            "UPDATE user_sessions SET character_id = ? WHERE session_id = ?",
            (character_id, session_id)
        )
    
    def destroy_session(self, session_id: str):
        """Уничтожить сессию (выход)."""
        db = get_db()
        db.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
        db.execute(
            "UPDATE account SET session_sid = NULL, online = 0 WHERE session_sid = ?",
            (session_id,)
        )
        logger.info(f"Destroyed session {session_id[:16]}...")
    
    def cleanup_expired_sessions(self):
        """Очистить просроченные сессии."""
        db = get_db()
        now = int(time.time())
        deleted = db.execute(
            "DELETE FROM user_sessions WHERE expires_at <= ?",
            (now,)
        )
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired sessions")
        return deleted

    def get_server_address(self) -> str:
        """Получить адрес сервера для ответа клиенту."""
        from config import HOST
        return HOST
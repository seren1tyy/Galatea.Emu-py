"""Базовый модуль для работы с MariaDB через PyMySQL (работает на Windows)."""

import pymysql
from pymysql.cursors import DictCursor
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
import logging
from config import DB_CONFIG

logger = logging.getLogger(__name__)


class Database:
    """Базовый класс для работы с MariaDB через PyMySQL."""
    
    def __init__(self, config: Dict = None):
        self.config = config or DB_CONFIG
        self._connection = None
    
    def connect(self) -> 'Database':
        """Установить соединение с БД."""
        try:
            self._connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                autocommit=self.config.get('autocommit', False),
                cursorclass=DictCursor,
                charset='utf8mb4'
            )
            logger.info(f"✅ Connected to MariaDB: {self.config['database']}")
            return self
        except pymysql.Error as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Закрыть соединение."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Disconnected from database")
    
    @contextmanager
    def get_cursor(self):
        """Контекстный менеджер для курсора."""
        if not self._connection:
            self.connect()
        
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: Tuple = None) -> int:
        """Выполнить запрос без возврата результатов."""
        with self.get_cursor() as cursor:
            affected = cursor.execute(query, params or ())
            return affected
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Выполнить массовую вставку."""
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def query_one(self, query: str, params: Tuple = None) -> Optional[Dict]:
        """Выполнить запрос и вернуть одну строку."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    
    def query_all(self, query: str, params: Tuple = None) -> List[Dict]:
        """Выполнить запрос и вернуть все строки."""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def insert(self, table: str, data: Dict) -> int:
        """Вставить одну запись."""
        columns = ', '.join(f"`{k}`" for k in data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
        
        with self.get_cursor() as cursor:
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid
    
    def update(self, table: str, data: Dict, where: str, where_params: Tuple = None) -> int:
        """Обновить записи."""
        set_clause = ', '.join([f"`{k}` = %s" for k in data.keys()])
        query = f"UPDATE `{table}` SET {set_clause} WHERE {where}"
        params = tuple(data.values()) + (where_params or ())
        return self.execute(query, params)
    
    def delete(self, table: str, where: str, params: Tuple = None) -> int:
        """Удалить записи."""
        query = f"DELETE FROM `{table}` WHERE {where}"
        return self.execute(query, params)
    
    def table_exists(self, table_name: str) -> bool:
        """Проверить существование таблицы."""
        result = self.query_one(
            "SELECT COUNT(*) as cnt FROM information_schema.tables "
            "WHERE table_schema = %s AND table_name = %s",
            (self.config['database'], table_name)
        )
        return result['cnt'] > 0 if result else False


# Синглтон
_db_instance = None


def get_db() -> Database:
    """Получить экземпляр Database (синглтон)."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.connect()
    return _db_instance
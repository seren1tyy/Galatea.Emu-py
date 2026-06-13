#!/usr/bin/env python3
"""
EVE Online Server Emulator
Simple implementation for protocol research and learning
"""

import sys
import logging
from server import EVEServer
from database.db import get_db

def setup_logging():
    """Настройка логирования."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('eve_server.log')
        ]
    )

def main():
    """Точка входа."""
    print("=" * 60)
    print("EVE Online Server Emulator")
    print("Database: galatea_db")
    print("=" * 60)
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Проверка подключения к БД
        db = get_db()
        db.connect()
        
        # Проверяем наличие таблиц
        if not db.table_exists('account'):
            logger.warning("Table 'account' not found! Run migrations first.")
            logger.warning("You can create tables using database/migrations/schema.sql")
            
            choice = input("Continue anyway? (y/n): ")
            if choice.lower() != 'y':
                return
        
        # Запуск сервера
        server = EVEServer()
        server.start()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
Инициализация базы данных MariaDB для эмулятора.
"""

import sys
import os
from database.db import get_db

def run_migration():
    """Выполнить миграцию schema.sql."""
    db = get_db()
    db.connect()
    
    schema_path = os.path.join('database', 'migrations', 'schema.sql')
    
    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    # Пробуем разные кодировки
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'latin1', 'cp866']
    
    schema_sql = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(schema_path, 'r', encoding=encoding) as f:
                schema_sql = f.read()
                used_encoding = encoding
                print(f"✅ Read schema with encoding: {encoding}")
                break
        except UnicodeDecodeError:
            continue
    
    if schema_sql is None:
        print("❌ Could not read schema file with any encoding")
        return False
    
    # Разбиваем на отдельные запросы
    statements = []
    current = []
    
    for line in schema_sql.split('\n'):
        line = line.strip()
        if not line or line.startswith('--'):
            continue
        
        current.append(line)
        
        if line.endswith(';'):
            statements.append(' '.join(current)[:-1])  # Убираем ;
            current = []
    
    # Выполняем каждый запрос
    with db.get_cursor() as cursor:
        for stmt in statements:
            try:
                cursor.execute(stmt)
                print(f"✅ Executed: {stmt[:50]}...")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
    
    print("\n🎉 Database initialization complete!")
    return True

if __name__ == "__main__":
    run_migration()
# Конфигурация MariaDB
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'galatea_user',
    'password': 'galatea',
    'database': 'galatea_db',
    'autocommit': False,
    'pool_size': 5,
    'pool_name': 'eve_pool'
}

HOST = '127.0.0.1'
PORT = 26000
QUEUE_POSITION = 1  # 1 = "можно подключаться"
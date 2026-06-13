"""IMAP4 handler for EVE client authentication."""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class IMAP4Handler:
    """
    Обработчик IMAP4 протокола для аутентификации EVE клиента.
    
    Клиент отправляет IMAP4 команды, ожидая ответы в формате:
    * OK [CAPABILITY ...]
    tag OK [...]
    tag NO [...]
    """
    
    def __init__(self, auth_handler):
        self.auth_handler = auth_handler
        self.state = 'NONAUTH'  # NONAUTH, AUTH, SELECTED, LOGOUT
        self.tag_counter = 0
        self.capabilities = [
            'IMAP4REV1',
            'LOGIN-REFERRALS',
            'AUTH=LOGIN',
            'AUTH=PLAIN',
            'AUTH=CRAM-MD5',
            'UIDPLUS',
            'IDLE',
            'LITERAL+'
        ]
    
    def process_command(self, command_line: str, client, addr) -> bytes:
        """Обработать IMAP4 команду."""
        logger.info(f"IMAP4 << {command_line.strip()}")
        
        # Парсим команду
        parts = command_line.strip().split()
        if not parts:
            return self._response('BAD', 'Invalid command')
        
        tag = parts[0]
        command = parts[1].upper() if len(parts) > 1 else None
        args = parts[2:] if len(parts) > 2 else []
        
        # Маршрутизация команд
        if command == 'CAPABILITY':
            return self._cmd_capability(tag)
        elif command == 'LOGIN':
            return self._cmd_login(tag, args, client, addr)
        elif command == 'LOGOUT':
            return self._cmd_logout(tag)
        elif command == 'NOOP':
            return self._cmd_noop(tag)
        elif command == 'SELECT':
            return self._cmd_select(tag, args)
        elif command == 'EXAMINE':
            return self._cmd_examine(tag, args)
        elif command == 'CLOSE':
            return self._cmd_close(tag)
        elif command == 'FETCH':
            return self._cmd_fetch(tag, args)
        elif command == 'LOGOUT':
            return self._cmd_logout(tag)
        else:
            logger.warning(f"Unknown IMAP4 command: {command}")
            return self._response(tag, 'BAD', f'Unknown command {command}')
    
    def _cmd_capability(self, tag: str) -> bytes:
        """CAPABILITY command."""
        caps = ' '.join(self.capabilities)
        response = f"* CAPABILITY {caps}\r\n{tag} OK CAPABILITY completed\r\n"
        return response.encode('utf-8')
    
    def _cmd_login(self, tag: str, args: List[str], client, addr) -> bytes:
        """LOGIN command - основная аутентификация."""
        if len(args) < 2:
            return self._response(tag, 'BAD', 'LOGIN requires username and password')
        
        # Убираем кавычки
        username = args[0].strip('"')
        password = args[1].strip('"')
        
        logger.info(f"IMAP4 LOGIN attempt: {username}")
        
        # Вызываем вашу аутентификацию
        result = self.auth_handler.handle_login(username, password, addr[0])
        
        if result and b'error' not in result:
            self.state = 'AUTH'
            # Ответ с успешным логином
            response = (
                f"* OK [CAPABILITY {' '.join(self.capabilities)}] LOGIN completed\r\n"
                f"{tag} OK LOGIN completed\r\n"
            )
            logger.info(f"✅ IMAP4 LOGIN successful for {username}")
        else:
            response = self._response(tag, 'NO', 'Authentication failed')
            logger.warning(f"❌ IMAP4 LOGIN failed for {username}")
        
        return response.encode('utf-8')
    
    def _cmd_logout(self, tag: str) -> bytes:
        """LOGOUT command."""
        self.state = 'LOGOUT'
        response = f"* BYE LOGOUT received\r\n{tag} OK LOGOUT completed\r\n"
        return response.encode('utf-8')
    
    def _cmd_noop(self, tag: str) -> bytes:
        """NOOP command."""
        return self._response(tag, 'OK', 'NOOP completed').encode('utf-8')
    
    def _cmd_select(self, tag: str, args: List[str]) -> bytes:
        """SELECT command - выбрать mailbox."""
        mailbox = args[0].strip('"') if args else 'INBOX'
        response = (
            f"* {self._get_message_count()} EXISTS\r\n"
            f"* 0 RECENT\r\n"
            f"* FLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft)\r\n"
            f"* OK [PERMANENTFLAGS (\\* \\Answered \\Flagged \\Deleted \\Seen \\Draft)]\r\n"
            f"* OK [UIDVALIDITY 1]\r\n"
            f"* OK [UIDNEXT 1]\r\n"
            f"{tag} OK [READ-WRITE] SELECT completed\r\n"
        )
        return response.encode('utf-8')
    
    def _cmd_examine(self, tag: str, args: List[str]) -> bytes:
        """EXAMINE command (read-only select)."""
        response = (
            f"* 0 EXISTS\r\n"
            f"* 0 RECENT\r\n"
            f"* FLAGS (\\Answered \\Flagged \\Deleted \\Seen \\Draft)\r\n"
            f"* OK [PERMANENTFLAGS ()]\r\n"
            f"* OK [UIDVALIDITY 1]\r\n"
            f"{tag} OK [READ-ONLY] EXAMINE completed\r\n"
        )
        return response.encode('utf-8')
    
    def _cmd_close(self, tag: str) -> bytes:
        """CLOSE command."""
        return self._response(tag, 'OK', 'CLOSE completed').encode('utf-8')
    
    def _cmd_fetch(self, tag: str, args: List[str]) -> bytes:
        """FETCH command - получить сообщения."""
        # Возвращаем пустой ответ
        response = f"{tag} OK FETCH completed\r\n"
        return response.encode('utf-8')
    
    def _get_message_count(self) -> int:
        """Получить количество сообщений (для SELECT)."""
        # TODO: Реальная логика
        return 0
    
    def _response(self, tag: str, status: str, message: str) -> str:
        """Сформировать IMAP4 ответ."""
        return f"{tag} {status} {message}\r\n"
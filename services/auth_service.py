import logging
from handlers.auth_handler import AuthHandler

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service - EVE authentication."""
    
    def __init__(self, rpc_node):
        self.node = rpc_node
        self.auth_handler = AuthHandler()
    
    def Login(self, username, password, *args, **kwargs):
        """Login method called by client."""
        logger.info(f"🔐 Login called: {username}")
        
        # Аутентификация
        account = self.auth_handler.accounts.authenticate(
            username, password, self.node.addr[0]
        )
        
        if not account:
            raise Exception("Invalid username or password")
        
        # Создаём сессию
        session_id = self.auth_handler.sessions.create_session(
            account['accountID'],
            account['accountName'],
            self.node.addr[0]
        )
        
        self.node.session_id = session_id
        self.node.user_id = account['accountID']
        
        # Возвращаем результат
        return (session_id, account['accountName'], account.get('role', 0))
    
    def Ping(self):
        """Ping method."""
        import time
        return int(time.time() * 1000000)
    
    def GetPostAuthenticationMessage(self):
        """Get message after auth."""
        return None
    
    def AmUnderage(self):
        """Age check."""
        return False
    
    def AccruedTime(self):
        """Accrued play time."""
        return 0
    
    def SetLanguageID(self, language_id):
        """Set language."""
        return None
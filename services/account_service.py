import logging

logger = logging.getLogger(__name__)


class AccountService:
    """Account service - balance, journal, etc."""
    
    def __init__(self, rpc_node):
        self.node = rpc_node
    
    def GetCashBalance(self, *args, **kwargs):
        """Get ISK balance."""
        # Заглушка
        return 1000000.0
    
    def GetKeyMap(self):
        """Get account key types."""
        return {}
    
    def GetEntryTypes(self):
        """Get journal entry types."""
        return {}
    
    def GetJournal(self, *args, **kwargs):
        """Get journal entries."""
        return []
    
    def GiveCash(self, *args, **kwargs):
        """Transfer ISK."""
        return None
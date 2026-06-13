import logging

logger = logging.getLogger(__name__)


class CharacterService:
    """Character service - character list, selection, etc."""
    
    def __init__(self, rpc_node):
        self.node = rpc_node
    
    def GetCharacterList(self):
        """Get characters for account."""
        from database.models.character import CharacterModel
        
        if not self.node.user_id:
            return []
        
        chars = CharacterModel().get_by_account(self.node.user_id)
        result = []
        for char in chars:
            result.append((
                char['characterID'],
                char['characterName'],
                char.get('typeID', 1383),
                char.get('corporationID', 0),
                char.get('balance', 0),
            ))
        return result
    
    def SelectCharacter(self, character_id):
        """Select character."""
        from database.models.character import CharacterModel
        
        char = CharacterModel().get_by_id(character_id)
        if char and char['accountID'] == self.node.user_id:
            self.node.character_id = character_id
            return (character_id, 1, {'server': '127.0.0.1', 'port': 26000})
        return None
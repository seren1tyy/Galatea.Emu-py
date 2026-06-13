"""Модель для работы с таблицей chrCharacters."""

from typing import Optional, Dict, Any, List
from database.db import get_db
import logging

logger = logging.getLogger(__name__)


class CharacterModel:
    """Модель для управления персонажами."""
    
    TABLE = 'chrCharacters'
    
    def get_by_id(self, character_id: int) -> Optional[Dict]:
        """Получить персонажа по ID."""
        db = get_db()
        return db.query_one(
            "SELECT * FROM chrCharacters WHERE characterID = ?",
            (character_id,)
        )
    
    def get_by_account(self, account_id: int) -> List[Dict]:
        """Получить всех персонажей аккаунта."""
        db = get_db()
        return db.query_all(
            "SELECT * FROM chrCharacters WHERE accountID = ? AND deletePrepareDateTime = 0",
            (account_id,)
        )
    
    def create_character(self, account_id: int, character_name: str, **kwargs) -> int:
        """Создать нового персонажа."""
        db = get_db()
        
        # Данные по умолчанию
        default_data = {
            'characterName': character_name,
            'accountID': account_id,
            'typeID': 1383,  # Тип "Character"
            'gender': 0,
            'balance': 1000000.0,
            'aurBalance': 0.0,
            'securityRating': 0.0,
            'skillPoints': 0,
            'corporationID': 1000169,  # Стартовая корпорация
            'bloodlineID': kwargs.get('bloodlineID', 1),
            'raceID': kwargs.get('raceID', 1),
            'ancestryID': kwargs.get('ancestryID', 1),
            'createDateTime': int(__import__('time').time()),
        }
        
        # Переопределяем переданными параметрами
        default_data.update(kwargs)
        
        character_id = db.insert(self.TABLE, default_data)
        logger.info(f"Created character {character_name} (ID: {character_id}) for account {account_id}")
        
        return character_id
    
    def update_character(self, character_id: int, data: Dict) -> bool:
        """Обновить данные персонажа."""
        db = get_db()
        affected = db.update(
            self.TABLE,
            data,
            "characterID = ?",
            (character_id,)
        )
        return affected > 0
    
    def delete_character(self, character_id: int) -> bool:
        """Мягкое удаление персонажа (установка флага удаления)."""
        db = get_db()
        
        # Проверяем существование
        char = self.get_by_id(character_id)
        if not char:
            return False
        
        # Устанавливаем время подготовки к удалению
        affected = db.update(
            self.TABLE,
            {'deletePrepareDateTime': int(__import__('time').time())},
            "characterID = ?",
            (character_id,)
        )
        
        logger.info(f"Character {character_id} marked for deletion")
        return affected > 0
    
    def set_location(self, character_id: int, location_id: int) -> bool:
        """Установить текущую локацию персонажа."""
        db = get_db()
        affected = db.update(
            self.TABLE,
            {
                'locationID': location_id,
                'stationID': location_id if location_id > 3000000 else 0,
                'solarSystemID': self._get_solar_system_by_station(location_id),
            },
            "characterID = ?",
            (character_id,)
        )
        return affected > 0
    
    def add_skill_points(self, character_id: int, points: int) -> bool:
        """Добавить скиллпоинты персонажу."""
        db = get_db()
        affected = db.execute(
            "UPDATE chrCharacters SET skillPoints = skillPoints + ? WHERE characterID = ?",
            (points, character_id)
        )
        return affected > 0
    
    def _get_solar_system_by_station(self, station_id: int) -> int:
        """Получить ID солнечной системы по ID станции."""
        # TODO: Реализовать через таблицу staStations
        # Пока заглушка
        return 30000142  # Jita IV - Moon 4
    
    def get_character_list_for_protocol(self, account_id: int) -> List[tuple]:
        """
        Получить список персонажей в формате, ожидаемом протоколом EVE.
        
        Returns:
            Список кортежей с данными персонажей для CharacterList ответа
        """
        characters = self.get_by_account(account_id)
        
        result = []
        for char in characters:
            # Формат соответствует ожиданиям клиента (нужно уточнить через сниффинг)
            char_tuple = (
                char['characterID'],
                char['characterName'],
                char.get('typeID', 1383),
                char.get('corporationID', 0),
                char.get('balance', 0.0),
                char.get('securityRating', 0.0),
                char.get('locationID', 0),
                char.get('skillPoints', 0),
                char.get('gender', 0),
                char.get('ancestryID', 0),
                char.get('bloodlineID', 0),
                char.get('raceID', 0),
                char.get('title', ''),
                char.get('description', ''),
                char.get('bounty', 0.0),
                char.get('aurBalance', 0.0),
            )
            result.append(char_tuple)
        
        return result
    
    def update_last_login(self, character_id: int):
        """Обновить время последнего входа."""
        db = get_db()
        db.execute(
            "UPDATE chrCharacters SET logonDateTime = ? WHERE characterID = ?",
            (int(__import__('time').time()), character_id)
        )
from abc import ABC, abstractmethod
from typing import Optional

from src.core.models import UserPreferences


class IPreferencesStorage(ABC):
    @abstractmethod
    def save_user(self, preferences: UserPreferences) -> bool:
        pass

    @abstractmethod
    def get_user(self, discord_channel_id: str) -> Optional[UserPreferences]:
        pass

    @abstractmethod
    def get_all_users(self) -> list[UserPreferences]:
        pass

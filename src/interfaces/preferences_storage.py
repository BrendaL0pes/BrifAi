"""Interface for user preferences storage."""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.models import UserPreferences


class IPreferencesStorage(ABC):
    """Abstract base class for persisting user preferences."""

    @abstractmethod
    def save_user(self, preferences: UserPreferences) -> bool:
        """Saves a user's preferences to the storage."""
        pass

    @abstractmethod
    def get_user(self, discord_channel_id: str) -> Optional[UserPreferences]:
        """Retrieves a user's preferences by their Discord channel ID."""
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserPreferences]:
        """Retrieves all registered users (useful for the daily scheduler)."""
        pass
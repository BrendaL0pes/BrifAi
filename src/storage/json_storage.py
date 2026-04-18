"""JSON implementation for user preferences storage."""
import json
from pathlib import Path
from typing import List, Optional, Dict

from src.core.models import UserPreferences
from src.interfaces.preferences_storage import IPreferencesStorage


class JsonPreferencesStorage(IPreferencesStorage):
    """Stores user preferences in a local JSON file."""

    def __init__(self, file_path: str = "data/preferences.json"):
        """Initializes the storage and ensures the file exists."""
        self.file_path = Path(file_path)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Creates the directory and file if they do not exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text("{}", encoding="utf-8")

    def _read_data(self) -> Dict[str, dict]:
        """Reads the raw dictionary from the JSON file."""
        content = self.file_path.read_text(encoding="utf-8")
        return json.loads(content) if content else {}

    def _write_data(self, data: Dict[str, dict]) -> None:
        """Writes the dictionary back to the JSON file."""
        content = json.dumps(data, indent=4, ensure_ascii=False)
        self.file_path.write_text(content, encoding="utf-8")

    def save_user(self, preferences: UserPreferences) -> bool:
        """Saves a user's preferences to the storage."""
        try:
            data = self._read_data()
            data[preferences.discord_channel_id] = preferences.__dict__
            self._write_data(data)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def get_user(self, discord_channel_id: str) -> Optional[UserPreferences]:
        """Retrieves a user's preferences by their Discord channel ID."""
        data = self._read_data()
        user_dict = data.get(discord_channel_id)
        return UserPreferences(**user_dict) if user_dict else None

    def get_all_users(self) -> List[UserPreferences]:
        """Retrieves all registered users."""
        data = self._read_data()
        return [UserPreferences(**u_dict) for u_dict in data.values()]
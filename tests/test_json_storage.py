"""Unit tests for JsonPreferencesStorage."""
import json
from pathlib import Path

from src.core.models import UserPreferences
from src.storage.json_storage import JsonPreferencesStorage


def test_save_and_load_user(tmp_path):
    file_path = tmp_path / "preferences.json"
    storage = JsonPreferencesStorage(str(file_path))

    preferences = UserPreferences(
        discord_channel_id="123456789",
        email_address="user@example.com",
        topics=["technology", "productivity"],
        keywords=["AI", "automation"],
        max_news_per_topic=4,
    )

    assert storage.save_user(preferences) is True

    loaded = storage.get_user("123456789")
    assert loaded == preferences

    all_users = storage.get_all_users()
    assert all_users == [preferences]


def test_get_user_returns_none_when_missing(tmp_path):
    file_path = tmp_path / "preferences.json"
    storage = JsonPreferencesStorage(str(file_path))

    assert storage.get_user("999") is None
    assert storage.get_all_users() == []


def test_invalid_json_file_is_recovered(tmp_path):
    file_path = tmp_path / "preferences.json"
    file_path.write_text("{ invalid json }", encoding="utf-8")

    storage = JsonPreferencesStorage(str(file_path))

    assert storage.get_all_users() == []

    preferences = UserPreferences(
        discord_channel_id="abc123",
        email_address="recovery@example.com",
        topics=["science"],
        keywords=["space"],
    )

    assert storage.save_user(preferences) is True
    assert storage.get_user("abc123") == preferences

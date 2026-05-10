"""Unit tests for DiscordBotManager onboarding flow."""
import pytest
from unittest.mock import MagicMock

from src.bot.discord_bot import DiscordBotManager
from src.core.models import UserPreferences


class DummyChannel:
    def __init__(self):
        self.sent_messages = []

    async def send(self, content):
        self.sent_messages.append(content)


class DummyAuthor:
    def __init__(self, user_id, bot=False):
        self.id = user_id
        self.bot = bot


class DummyMessage:
    def __init__(self, content, author, channel):
        self.content = content
        self.author = author
        self.channel = channel


@pytest.mark.asyncio
async def test_register_events_assigns_handler():
    client = MagicMock()
    manager = DiscordBotManager(client, MagicMock())

    manager.register_events()

    assert client.on_message == manager._on_message


@pytest.mark.asyncio
async def test_full_onboarding_flow_saves_preferences():
    storage = MagicMock()
    client = MagicMock()
    manager = DiscordBotManager(client, storage)

    author = DummyAuthor(user_id=42)
    channel = DummyChannel()

    await manager._on_message(DummyMessage("!start", author, channel))
    assert channel.sent_messages[-1] == manager.QUESTIONS["topics"]

    await manager._on_message(DummyMessage("technology, science", author, channel))
    assert channel.sent_messages[-1] == manager.QUESTIONS["keywords"]

    await manager._on_message(DummyMessage("AI, automation", author, channel))
    assert channel.sent_messages[-1] == manager.QUESTIONS["email"]

    await manager._on_message(DummyMessage("user@example.com", author, channel))
    assert channel.sent_messages[-1] == manager.QUESTIONS["channel"]

    await manager._on_message(DummyMessage("987654321", author, channel))

    storage.save_user.assert_called_once()
    saved_preferences = storage.save_user.call_args.args[0]
    assert isinstance(saved_preferences, UserPreferences)
    assert saved_preferences.discord_channel_id == "987654321"
    assert saved_preferences.email_address == "user@example.com"
    assert saved_preferences.topics == ["technology", "science"]
    assert saved_preferences.keywords == ["AI", "automation"]
    assert channel.sent_messages[-1].startswith("Preferences saved!")


@pytest.mark.asyncio
async def test_invalid_email_is_rejected_and_flow_retries():
    storage = MagicMock()
    client = MagicMock()
    manager = DiscordBotManager(client, storage)

    author = DummyAuthor(user_id=99)
    channel = DummyChannel()

    await manager._on_message(DummyMessage("!start", author, channel))
    await manager._on_message(DummyMessage("marketing", author, channel))
    await manager._on_message(DummyMessage("AI", author, channel))

    await manager._on_message(DummyMessage("not-an-email", author, channel))
    assert channel.sent_messages[-1] == "Please provide a valid email address."

    await manager._on_message(DummyMessage("user@example.com", author, channel))
    assert channel.sent_messages[-1] == manager.QUESTIONS["channel"]


@pytest.mark.asyncio
async def test_invalid_channel_id_is_rejected():
    storage = MagicMock()
    client = MagicMock()
    manager = DiscordBotManager(client, storage)

    author = DummyAuthor(user_id=100)
    channel = DummyChannel()

    await manager._on_message(DummyMessage("!start", author, channel))
    await manager._on_message(DummyMessage("security", author, channel))
    await manager._on_message(DummyMessage("AI", author, channel))
    await manager._on_message(DummyMessage("john@example.com", author, channel))

    await manager._on_message(DummyMessage("not-a-number", author, channel))
    assert channel.sent_messages[-1] == "Please provide a valid numeric channel ID."

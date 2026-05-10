import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

import discord

from src.bot.discord_bot import DiscordBotManager
from src.core.models import UserPreferences
from src.interfaces.preferences_storage import IPreferencesStorage


class MockStorage(IPreferencesStorage):
    def __init__(self):
        self.users = []

    def save_user(self, preferences: UserPreferences) -> bool:
        self.users.append(preferences)
        return True

    def get_user(self, discord_channel_id: str) -> UserPreferences | None:
        return next(
            (u for u in self.users if u.discord_channel_id == discord_channel_id), None
        )

    def get_all_users(self) -> list[UserPreferences]:
        return self.users


class TestDiscordBotManager(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock(spec=discord.Client)
        self.storage = MockStorage()
        self.manager = DiscordBotManager(self.client, self.storage)

    async def test_registration_flow(self):
        # Simula uma mensagem !register
        message = MagicMock(spec=discord.Message)
        message.author.bot = False
        message.author.id = 123
        message.content = "!register"
        message.channel = AsyncMock(spec=discord.TextChannel)
        message.channel.send = AsyncMock()

        await self.manager._on_message(message)
        message.channel.send.assert_called_with(
            "Quais tópicos de notícias você deseja receber? Separe-os por vírgula."
        )

        # Simula resposta com tópicos
        message.content = "tecnologia, política"
        await self.manager._on_message(message)
        message.channel.send.assert_called_with(
            "Quais palavras-chave você deseja incluir? Separe-as por vírgula ou responda `nenhuma`."
        )

        # Continue simulando os passos restantes...
        # (Adicione asserts para verificar se o estado avança e se save_user é chamado)

    def test_email_validation(self):
        self.assertTrue(self.manager._is_valid_email("test@example.com"))
        self.assertFalse(self.manager._is_valid_email("invalid-email"))

    def test_channel_parsing(self):
        self.assertEqual(self.manager._parse_channel_id("este canal", 456), 456)
        self.assertEqual(self.manager._parse_channel_id("<#789>", 456), 789)
        self.assertEqual(self.manager._parse_channel_id("123", 456), 123)
        self.assertIsNone(self.manager._parse_channel_id("invalid", 456))


if __name__ == "__main__":
    asyncio.run(unittest.main())

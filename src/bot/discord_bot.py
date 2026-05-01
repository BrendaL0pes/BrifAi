import discord

from src.core.models import UserPreferences
from src.storage.json_storage import JsonPreferencesStorage


class DiscordBotManager:
    def __init__(self, client: discord.Client, storage: JsonPreferencesStorage):
        self.client = client
        self.storage = storage

    def register_events(self) -> None:
        @self.client.event
        async def on_message(message: discord.Message):
            if message.author.bot:
                return

            if message.content.startswith("!register"):
                preferences = UserPreferences(
                    discord_channel_id=str(message.channel.id),
                    email_address="",
                    topics=[],
                    keywords=[],
                    max_news_per_topic=5,
                )
                self.storage.save_user(preferences)
                await message.channel.send("Channel registered for daily briefings.")

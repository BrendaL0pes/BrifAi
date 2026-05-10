import discord
from typing import Optional

from agno.agent import Agent
from agno.models.groq import Groq
from src.core.models import UserPreferences
from src.interfaces.preferences_storage import IPreferencesStorage


class DiscordBotManager:
    def __init__(self, client: discord.Client, storage: IPreferencesStorage) -> None:
        self.client = client
        self.storage = storage
        self.onboarding_agent = self._create_onboarding_agent()

    def _create_onboarding_agent(self) -> Agent:
        """Creates the Agno agent for conversational onboarding."""
        return Agent(
            name="BrifAI Onboarding Assistant",
            model=Groq(id="llama-3.1-8b-instant"),
            instructions=(
                "You are BrifAI's onboarding assistant. Help users set up their preferences "
                "for personalized news briefings. Ask about their interests, topics, keywords, "
                "and preferred delivery methods (Discord or Email). Guide them step by step. "
                "Be friendly and concise."
            ),
        )

    def register_events(self) -> None:
        @self.client.event
        async def on_message(message: discord.Message) -> None:
            if message.author.bot:
                return

            await self._handle_message(message)

    async def _handle_message(self, message: discord.Message) -> None:
        if message.content.startswith("!register"):
            await self._register_channel(message)
        elif message.content.startswith("!onboard"):
            await self._start_onboarding(message)
        else:
            await self._handle_conversation(message)

    async def _register_channel(self, message: discord.Message) -> None:
        preferences = UserPreferences(
            discord_channel_id=str(message.channel.id),
            email_address="",
            topics=[],
            keywords=[],
            max_news_per_topic=5,
        )
        success = self.storage.save_user(preferences)
        if success:
            await message.channel.send("Channel registered for daily briefings.")
        else:
            await message.channel.send("Failed to register channel.")

    async def _start_onboarding(self, message: discord.Message) -> None:
        response = self.onboarding_agent.run("Start onboarding for a new user.")
        await message.channel.send(str(response.content))

    async def _handle_conversation(self, message: discord.Message) -> None:
        # For conversational onboarding, use the agent
        response = self.onboarding_agent.run(message.content)
        await message.channel.send(str(response.content))

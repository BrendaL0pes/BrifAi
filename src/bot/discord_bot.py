from dataclasses import dataclass, field
from typing import Dict

import discord

from src.core.models import UserPreferences
from src.delivery.scheduler import BriefingScheduler
from src.interfaces.preferences_storage import IPreferencesStorage


@dataclass
class ConversationState:
    """Tracks the onboarding flow for a single Discord user."""
    step: int = 0
    partial: dict[str, str] = field(default_factory=dict)


class DiscordBotManager:
    """Manages conversational onboarding via Discord."""

    STEPS = ["topics", "keywords", "email", "channel"]
    QUESTIONS = {
        "topics": "What topics interest you? (comma-separated)",
        "keywords": "Any priority keywords? (comma-separated)",
        "email": "What is your email address?",
        "channel": "What Discord channel ID should receive briefings?",
    }

    def __init__(
        self,
        client: discord.Client,
        storage: IPreferencesStorage,
        scheduler: BriefingScheduler,
    ) -> None:
        self._client = client
        self._storage = storage
        self._scheduler = scheduler
        self._sessions: Dict[int, ConversationState] = {}

    def register_events(self) -> None:
        """Registers the message event handler on the injected client."""
        self._client.on_message = self._on_message

    async def _on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content.strip()
        user_id = message.author.id

        if content.lower() == "!start":
            await self._start_session(message, user_id)
            return

        if content.lower() == "!test":
            await self._run_test(message)
            return

        if user_id in self._sessions:
            await self._handle_step(message, user_id)

    async def _start_session(self, message: discord.Message, user_id: int) -> None:
        self._sessions[user_id] = ConversationState()
        await message.channel.send(self.QUESTIONS["topics"])

    async def _handle_step(self, message: discord.Message, user_id: int) -> None:
        state = self._sessions[user_id]
        current_step = self.STEPS[state.step]
        answer = message.content.strip()

        if not await self._process_answer(state, current_step, answer, message):
            return

        state.step += 1
        if state.step < len(self.STEPS):
            await message.channel.send(self.QUESTIONS[self.STEPS[state.step]])
            return

        await self._complete(message, user_id)

    async def _run_test(self, message: discord.Message) -> None:
        await message.channel.send("Running manual briefing test...")
        try:
            await self._scheduler.run_daily_job()
            await message.channel.send("Manual briefing test finished.")
        except Exception as exception:
            await message.channel.send(f"Manual briefing test failed: {exception}")

    async def _process_answer(
        self,
        state: ConversationState,
        step_name: str,
        answer: str,
        message: discord.Message,
    ) -> bool:
        if step_name == "topics":
            topics = self._parse_list(answer)
            if not topics:
                await message.channel.send("Please provide at least one topic.")
                return False
            state.partial[step_name] = ", ".join(topics)
            return True

        if step_name == "keywords":
            state.partial[step_name] = ", ".join(self._parse_list(answer))
            return True

        if step_name == "email":
            if not self._is_valid_email(answer):
                await message.channel.send("Please provide a valid email address.")
                return False
            state.partial[step_name] = answer
            return True

        if step_name == "channel":
            if not self._is_valid_channel_id(answer):
                await message.channel.send("Please provide a valid numeric channel ID.")
                return False
            state.partial[step_name] = answer
            return True

        return False

    async def _complete(self, message: discord.Message, user_id: int) -> None:
        partial = self._sessions.pop(user_id)
        preferences = UserPreferences(
            discord_channel_id=partial.partial["channel"],
            email_address=partial.partial["email"],
            topics=[topic.strip() for topic in partial.partial["topics"].split(",")],
            keywords=[keyword.strip() for keyword in partial.partial["keywords"].split(",") if keyword.strip()],
        )
        self._storage.save_user(preferences)
        await message.channel.send(
            "Preferences saved! You will receive your briefing at 7 AM daily."
        )

    def _parse_list(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email

    def _is_valid_channel_id(self, channel_id: str) -> bool:
        return channel_id.isdigit()

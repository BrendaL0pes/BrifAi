"""Discord bot manager for user preference registration and manual testing."""
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TYPE_CHECKING

import discord

from src.core.models import UserPreferences
from src.interfaces.preferences_storage import IPreferencesStorage

if TYPE_CHECKING:
    from src.delivery.scheduler import BriefingScheduler


@dataclass
class ConversationState:
    """Tracks the onboarding flow state for a single Discord user."""

    step: int = 0
    partial: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_timed_out(self, timeout_seconds: int = 120) -> bool:
        """Returns True if the conversation has exceeded the timeout."""
        return datetime.now(timezone.utc) - self.started_at > timedelta(seconds=timeout_seconds)


class DiscordBotManager:
    """Manages Discord bot interactions for user preference registration."""

    def __init__(
        self,
        client: discord.Client,
        storage: IPreferencesStorage,
        scheduler: "BriefingScheduler",
    ) -> None:
        """Initialize the bot manager with Discord client, storage and scheduler."""
        self._client = client
        self._storage = storage
        self._scheduler = scheduler
        self._conversations: dict[int, ConversationState] = {}

    def register_events(self) -> None:
        """Register event handlers on the injected Discord client."""
        self._client.on_message = self._on_message

    async def _on_message(self, message: discord.Message) -> None:
        """Handle incoming Discord messages and route to the correct flow."""
        if message.author.bot:
            return

        author_id = message.author.id
        content = message.content.strip().lower()

        if content.startswith("!register"):
            await self._start_registration(message)
            return

        if content == "!test":
            await self._run_test(message)
            return

        state = self._conversations.get(author_id)
        if state:
            if state.is_timed_out():
                del self._conversations[author_id]
                await message.channel.send(
                    "Registro cancelado por tempo esgotado. Envie `!register` novamente quando estiver pronto."
                )
                return
            await self._process_step(message, state)

    async def _run_test(self, message: discord.Message) -> None:
        """Manually triggers the daily briefing job for testing purposes."""
        await message.channel.send("Iniciando briefing manual...")
        try:
            await self._scheduler.run_daily_job()
            await message.channel.send("Briefing enviado com sucesso!")
        except Exception as e:
            await message.channel.send(f"Erro ao gerar briefing: {e}")

    async def _start_registration(self, message: discord.Message) -> None:
        """Start the user registration process."""
        self._conversations[message.author.id] = ConversationState()
        await self._ask_topics(message.channel)

    async def _process_step(
        self, message: discord.Message, state: ConversationState
    ) -> None:
        """Process the current step in the registration flow."""
        content = message.content.strip()

        if state.step == 0:
            await self._handle_topics_step(message, state, content)
        elif state.step == 1:
            await self._handle_keywords_step(message, state, content)
        elif state.step == 2:
            await self._handle_email_step(message, state, content)
        elif state.step == 3:
            await self._handle_channel_step(message, state, content)
        else:
            del self._conversations[message.author.id]
            await message.channel.send(
                "Ocorreu um erro no registro. Envie `!register` para iniciar novamente."
            )

    async def _ask_topics(self, channel: discord.abc.Messageable) -> None:
        """Ask the user for news topics."""
        await channel.send(
            "Quais tópicos de notícias você deseja receber? Separe-os por vírgula."
        )

    async def _ask_keywords(self, channel: discord.abc.Messageable) -> None:
        """Ask the user for priority keywords."""
        await channel.send(
            "Quais palavras-chave você deseja incluir? Separe-as por vírgula ou responda `nenhuma`."
        )

    async def _ask_email(self, channel: discord.abc.Messageable) -> None:
        """Ask the user for their email address."""
        await channel.send("Qual é o seu e-mail para receber briefings por e-mail?")

    async def _ask_channel(self, channel: discord.abc.Messageable) -> None:
        """Ask the user for the target Discord channel."""
        await channel.send(
            "Por favor informe o canal Discord que deve receber as notificações. "
            "Responda com o ID do canal, mencione o canal ou envie `este canal` para usar este mesmo canal."
        )

    async def _handle_topics_step(
        self, message: discord.Message, state: ConversationState, content: str
    ) -> None:
        """Handle the topics input step."""
        topics = [t.strip() for t in content.split(",") if t.strip()]
        if not topics:
            await message.channel.send(
                "Entrada inválida. Informe pelo menos um tópico. Separe-os por vírgula."
            )
            await self._ask_topics(message.channel)
            return
        state.partial["topics"] = topics
        state.step = 1
        await self._ask_keywords(message.channel)

    async def _handle_keywords_step(
        self, message: discord.Message, state: ConversationState, content: str
    ) -> None:
        """Handle the keywords input step."""
        if content.lower() in {"nenhuma", "não", "nao", "sem"}:
            keywords: list[str] = []
        else:
            keywords = [k.strip() for k in content.split(",") if k.strip()]
        state.partial["keywords"] = keywords
        state.step = 2
        await self._ask_email(message.channel)

    async def _handle_email_step(
        self, message: discord.Message, state: ConversationState, content: str
    ) -> None:
        """Handle the email input step."""
        if not self._is_valid_email(content):
            await message.channel.send(
                "E-mail inválido. Por favor envie um endereço de e-mail válido."
            )
            await self._ask_email(message.channel)
            return
        state.partial["email_address"] = content
        state.step = 3
        await self._ask_channel(message.channel)

    async def _handle_channel_step(
        self, message: discord.Message, state: ConversationState, content: str
    ) -> None:
        """Handle the channel input step."""
        channel_id = self._parse_channel_id(content, message.channel.id)
        if channel_id is None:
            await message.channel.send(
                "Canal inválido. Envie o ID do canal, mencione o canal ou responda `este canal`."
            )
            await self._ask_channel(message.channel)
            return
        state.partial["discord_channel_id"] = str(channel_id)
        await self._complete_registration(message, state)

    async def _complete_registration(
        self, message: discord.Message, state: ConversationState
    ) -> None:
        """Complete the registration and persist user preferences."""
        preferences = UserPreferences(**state.partial)
        saved = self._storage.save_user(preferences)
        del self._conversations[message.author.id]

        if saved:
            await message.channel.send(
                "Registro concluído! Suas preferências foram salvas com sucesso."
            )
        else:
            await message.channel.send(
                "Não foi possível salvar suas preferências. Tente novamente mais tarde."
            )

    @staticmethod
    def _is_valid_email(value: str) -> bool:
        """Validates email format using a simple regex."""
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))

    @staticmethod
    def _parse_channel_id(value: str, current_channel_id: int) -> Optional[int]:
        """Parses a channel ID from user input (raw ID, mention, or keyword)."""
        cleaned = value.strip()
        if cleaned.lower() in {"este canal", "aqui", "mesmo canal", "canal atual"}:
            return current_channel_id
        mention_match = re.match(r"^<#(\d+)>$", cleaned)
        if mention_match:
            return int(mention_match.group(1))
        if cleaned.isdigit():
            return int(cleaned)
        return None
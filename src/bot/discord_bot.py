import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

import discord

from src.core.models import UserPreferences
from src.interfaces.preferences_storage import IPreferencesStorage


@dataclass
class ConversationState:
    step: int = 0
    partial: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.utcnow)

    def is_timed_out(self, timeout_seconds: int = 120) -> bool:
        return datetime.utcnow() - self.started_at > timedelta(seconds=timeout_seconds)


class DiscordBotManager:
    def __init__(self, client: discord.Client, storage: IPreferencesStorage) -> None:
        self._client = client
        self.storage = storage
        self._conversations: dict[int, ConversationState] = {}

    def register_events(self) -> None:
        self._client.on_message = self._on_message

    async def _on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        author_id = message.author.id
        if message.content.startswith("!register"):
            await self._start_registration(message)
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

    async def _start_registration(self, message: discord.Message) -> None:
        self._conversations[message.author.id] = ConversationState()
        await self._ask_topics(message.channel)

    async def _process_step(self, message: discord.Message, state: ConversationState) -> None:
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
        await channel.send(
            "Quais tópicos de notícias você deseja receber? Separe-os por vírgula."
        )

    async def _ask_keywords(self, channel: discord.abc.Messageable) -> None:
        await channel.send(
            "Quais palavras-chave você deseja incluir? Separe-as por vírgula ou responda `nenhuma`."
        )

    async def _ask_email(self, channel: discord.abc.Messageable) -> None:
        await channel.send(
            "Qual é o seu e-mail para receber briefings por e-mail?"
        )

    async def _ask_channel(self, channel: discord.abc.Messageable) -> None:
        await channel.send(
            "Por favor informe o canal Discord que deve receber as notificações. "
            "Responda com o ID do canal, mencione o canal ou envie `este canal` para usar este mesmo canal."
        )

    async def _handle_topics_step(
        self,
        message: discord.Message,
        state: ConversationState,
        content: str,
    ) -> None:
        topics = [topic.strip() for topic in content.split(",") if topic.strip()]
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
        self,
        message: discord.Message,
        state: ConversationState,
        content: str,
    ) -> None:
        if content.lower() in {"nenhuma", "não", "nao", "sem"}:
            keywords: list[str] = []
        else:
            keywords = [keyword.strip() for keyword in content.split(",") if keyword.strip()]
        state.partial["keywords"] = keywords
        state.step = 2
        await self._ask_email(message.channel)

    async def _handle_email_step(
        self,
        message: discord.Message,
        state: ConversationState,
        content: str,
    ) -> None:
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
        self,
        message: discord.Message,
        state: ConversationState,
        content: str,
    ) -> None:
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
        self,
        message: discord.Message,
        state: ConversationState,
    ) -> None:
        preferences = UserPreferences(**state.partial)
        saved = self.storage.save_user(preferences)
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
        return bool(
            re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value)
        )

    @staticmethod
    def _parse_channel_id(value: str, current_channel_id: int) -> Optional[int]:
        cleaned = value.strip()
        if cleaned.lower() in {"este canal", "aqui", "mesmo canal", "canal atual"}:
            return current_channel_id

        mention_match = re.match(r"^<#(\d+)>$", cleaned)
        if mention_match:
            return int(mention_match.group(1))

        if cleaned.isdigit():
            return int(cleaned)

        return None

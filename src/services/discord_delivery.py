"""Discord delivery service for sending briefings to channels."""
import discord

from src.interfaces.discord_notifier import IDiscordNotifier

DISCORD_MAX_LENGTH = 2000


class DiscordDeliveryService(IDiscordNotifier):
    """Delivers briefings to Discord channels using an injected client."""

    def __init__(self, client: discord.Client) -> None:
        """Initializes the service with a shared Discord client."""
        self._client = client

    async def send_message(
        self, channel_id: str, markdown_content: str
    ) -> bool:
        """Fetches the channel and sends the briefing in chunks."""
        channel = await self._client.fetch_channel(int(channel_id))
        for chunk in self._split_content(markdown_content):
            await channel.send(chunk)
        return True

    def _split_content(
        self, content: str, limit: int = DISCORD_MAX_LENGTH - 100
    ) -> list[str]:
        """Splits content into Discord-safe chunks at line boundaries."""
        chunks, current = [], ""
        for line in content.splitlines(keepends=True):
            if len(current) + len(line) > limit:
                chunks.append(current)
                current = ""
            current += line
        if current:
            chunks.append(current)
        return chunks
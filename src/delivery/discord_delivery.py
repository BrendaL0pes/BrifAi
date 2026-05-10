import discord
from src.interfaces.discord_notifier import IDiscordNotifier


class DiscordDeliveryService(IDiscordNotifier):
    """Delivers briefings to Discord channels using the injected client."""

    def __init__(self, client: discord.Client) -> None:
        self._client = client

    async def send_message(self, channel_id: str, markdown_content: str) -> bool:
        """Fetches the Discord channel and sends the briefing message."""
        try:
            channel = await self._client.fetch_channel(int(channel_id))
            await channel.send(markdown_content)
            return True
        except Exception:
            return False

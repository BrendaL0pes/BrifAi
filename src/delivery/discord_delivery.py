import asyncio
from typing import Optional

import discord
from src.interfaces.discord_notifier import IDiscordNotifier


class DiscordDeliveryService(IDiscordNotifier):
    def __init__(self, client: discord.Client, default_channel_id: Optional[str] = None):
        self.client = client
        self.default_channel_id = default_channel_id

    def send_message(self, channel_id: str, markdown_content: str) -> bool:
        channel_id = channel_id or self.default_channel_id
        if not channel_id:
            return False

        channel = self.client.get_channel(int(channel_id))
        if channel is None:
            return False

        loop = getattr(self.client, "loop", None)
        if loop and loop.is_running():
            asyncio.create_task(channel.send(markdown_content))
            return True

        return False

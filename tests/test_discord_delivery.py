"""Unit tests for DiscordDeliveryService."""
import pytest

from src.delivery.discord_delivery import DiscordDeliveryService


class DummyChannel:
    def __init__(self):
        self.sent_messages = []

    async def send(self, content):
        self.sent_messages.append(content)
        return True


class DummyClient:
    def __init__(self, channel):
        self._channel = channel

    async def fetch_channel(self, channel_id):
        return self._channel


class BrokenClient:
    async def fetch_channel(self, channel_id):
        raise RuntimeError("Channel fetch failed")


@pytest.mark.asyncio
async def test_send_message_success():
    channel = DummyChannel()
    client = DummyClient(channel)
    service = DiscordDeliveryService(client)

    result = await service.send_message("123", "Hello Discord")

    assert result is True
    assert channel.sent_messages == ["Hello Discord"]


@pytest.mark.asyncio
async def test_send_message_returns_false_on_exception():
    client = BrokenClient()
    service = DiscordDeliveryService(client)

    result = await service.send_message("123", "Hello Discord")

    assert result is False

"""Unit tests for BriefingScheduler."""
import pytest

from src.core.models import Briefing, UserPreferences
from src.delivery.scheduler import BriefingScheduler


class DummyStorage:
    def __init__(self, users):
        self._users = users

    def get_all_users(self):
        return self._users


class DummyAgent:
    def __init__(self, briefing):
        self.generated = briefing

    async def generate_briefing(self, user):
        return self.generated


class DummyEmailSender:
    def __init__(self):
        self.called = []

    def send_briefing(self, email, content):
        self.called.append((email, content))


class FailingEmailSender(DummyEmailSender):
    def send_briefing(self, email, content):
        raise RuntimeError("SMTP failure")


class DummyDiscordNotifier:
    def __init__(self):
        self.called = []

    async def send_message(self, channel_id, content):
        self.called.append((channel_id, content))
        return True


@pytest.mark.asyncio
async def test_run_daily_job_sends_email_and_discord():
    preferences = UserPreferences(
        discord_channel_id="123",
        email_address="user@example.com",
        topics=["news"],
        keywords=["ai"],
    )
    briefing = Briefing(
        user_email=preferences.email_address,
        discord_channel_id=preferences.discord_channel_id,
        content_markdown="# Test briefing",
    )

    storage = DummyStorage([preferences])
    agent = DummyAgent(briefing)
    email_sender = DummyEmailSender()
    notifier = DummyDiscordNotifier()

    scheduler = BriefingScheduler(storage, agent, [email_sender], [notifier])
    await scheduler.run_daily_job()

    assert email_sender.called == [(preferences.email_address, briefing.content_markdown)]
    assert notifier.called == [(preferences.discord_channel_id, briefing.content_markdown)]


@pytest.mark.asyncio
async def test_run_daily_job_continues_when_email_fails():
    preferences = UserPreferences(
        discord_channel_id="123",
        email_address="user@example.com",
        topics=["news"],
        keywords=["ai"],
    )
    briefing = Briefing(
        user_email=preferences.email_address,
        discord_channel_id=preferences.discord_channel_id,
        content_markdown="# Test briefing",
    )

    storage = DummyStorage([preferences])
    agent = DummyAgent(briefing)
    failing_email = FailingEmailSender()
    notifier = DummyDiscordNotifier()

    scheduler = BriefingScheduler(storage, agent, [failing_email], [notifier])
    await scheduler.run_daily_job()

    assert notifier.called == [(preferences.discord_channel_id, briefing.content_markdown)]

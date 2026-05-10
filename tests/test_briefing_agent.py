"""Unit tests for BriefingAgent."""
import pytest
from dataclasses import dataclass

from src.agent.briefing_agent import BriefingAgent
from src.core.models import NewsArticle, UserPreferences


@dataclass
class DummyResponse:
    content: str


class DummyAgent:
    def __init__(self, name, model, instructions, tools):
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools

    async def arun(self, prompt):
        self.prompt = prompt
        return DummyResponse(content="# Generated briefing")


class DummyFetcher:
    async def fetch_recent_news(self, topic, keywords, max_results):
        return [
            NewsArticle(
                title="Test Article",
                url="https://example.com",
                summary="Summary text",
                source="Example",
            )
        ]


class DummyGroq:
    def __init__(self, id):
        self.id = id


@pytest.mark.asyncio
async def test_generate_briefing_uses_agent_and_fetcher(monkeypatch):
    monkeypatch.setattr("src.agent.briefing_agent.Agent", DummyAgent)
    monkeypatch.setattr("src.agent.briefing_agent.Groq", DummyGroq)

    fetcher = DummyFetcher()
    agent = BriefingAgent(fetcher=fetcher, model_id="dummy-model")

    preferences = UserPreferences(
        discord_channel_id="999",
        email_address="user@example.com",
        topics=["finance", "startups"],
        keywords=["AI"],
        max_news_per_topic=2,
    )

    briefing = await agent.generate_briefing(preferences)

    assert briefing.user_email == preferences.email_address
    assert briefing.discord_channel_id == preferences.discord_channel_id
    assert briefing.content_markdown == "# Generated briefing"
    assert agent._agent.prompt.startswith("Generate a briefing for topics:")

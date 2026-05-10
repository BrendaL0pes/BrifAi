from src.agent.briefing_agent import BriefingAgent
from src.core.models import NewsArticle
from src.interfaces.news_fetcher import INewsFetcher


class FakeFetcher(INewsFetcher):
    def __init__(self, articles: list[NewsArticle]):
        self.articles = articles

    def fetch_recent_news(
        self,
        topic: str,
        keywords: list[str],
        max_results: int,
    ) -> list[NewsArticle]:
        return self.articles[:max_results]


def build_articles() -> list[NewsArticle]:
    return [
        NewsArticle(
            title="AI reaches new milestone",
            summary="A new model improved summarization quality.",
            source="Tech Daily",
            url="https://example.com/ai",
        ),
        NewsArticle(
            title="Teams adopt automation",
            summary="More companies are adopting AI workflows.",
            source="Business World",
            url="https://example.com/automation",
        ),
    ]


def test_create_briefing_uses_llm_runner():
    captured = {}

    def runner(prompt: str) -> str:
        captured["prompt"] = prompt
        return "# Briefing\n\n## Executive Summary\nLLM summary"

    agent = BriefingAgent(
        fetcher=FakeFetcher(build_articles()),
        llm_runner=runner,
    )

    briefing = agent.create_briefing(topic="AI", keywords=["agents"], max_results=2)

    assert briefing == "# Briefing\n\n## Executive Summary\nLLM summary"
    assert "Topic: AI" in captured["prompt"]
    assert "Keywords: agents" in captured["prompt"]


def test_create_briefing_returns_empty_message_without_articles():
    agent = BriefingAgent(fetcher=FakeFetcher([]))

    briefing = agent.create_briefing(topic="sports")

    assert briefing == "# Daily Briefing\n\nNo recent articles were found for `sports` at this time."


def test_create_briefing_falls_back_when_llm_fails():
    def runner(_: str) -> str:
        raise RuntimeError("model unavailable")

    agent = BriefingAgent(
        fetcher=FakeFetcher(build_articles()),
        llm_runner=runner,
    )

    briefing = agent.create_briefing(topic="AI")

    assert "AI summarization was unavailable" in briefing
    assert "AI reaches new milestone" in briefing
    assert "Teams adopt automation" in briefing

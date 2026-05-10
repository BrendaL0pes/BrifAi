from __future__ import annotations

from collections.abc import Callable
from typing import List

from src.core.models import NewsArticle
from src.interfaces.news_fetcher import INewsFetcher

try:
    from agno.agent import Agent
    from agno.models.groq import Groq
except ImportError:  # pragma: no cover
    Agent = None
    Groq = None


LlmRunner = Callable[[str], str]


class BriefingAgent:
    def __init__(
        self,
        fetcher: INewsFetcher,
        model_api_key: str | None = None,
        model_id: str = "llama-3.3-70b-versatile",
        llm_runner: LlmRunner | None = None,
    ):
        self.fetcher = fetcher
        self.model_api_key = model_api_key
        self.model_id = model_id
        self.llm_runner = llm_runner

    def create_briefing(
        self,
        topic: str = "general",
        keywords: list[str] | None = None,
        max_results: int = 5,
    ) -> str:
        articles = self._fetch_articles(topic, keywords, max_results)
        if not articles:
            return self._empty_briefing(topic)

        briefing = self._create_ai_briefing(topic, keywords or [], articles)
        if briefing:
            return briefing

        return self._create_fallback_briefing(topic, articles)

    def _fetch_articles(
        self,
        topic: str,
        keywords: list[str] | None,
        max_results: int,
    ) -> List[NewsArticle]:
        return self.fetcher.fetch_recent_news(
            topic=topic,
            keywords=keywords or [],
            max_results=max_results,
        )

    def _create_ai_briefing(
        self,
        topic: str,
        keywords: list[str],
        articles: List[NewsArticle],
    ) -> str | None:
        if not self._can_use_llm():
            return None

        try:
            return self._run_llm(self._build_prompt(topic, keywords, articles))
        except Exception:
            return None

    def _can_use_llm(self) -> bool:
        has_runner = self.llm_runner is not None
        has_agno = Agent is not None and Groq is not None
        return has_runner or bool(self.model_api_key and has_agno)

    def _run_llm(self, prompt: str) -> str:
        if self.llm_runner is not None:
            return self.llm_runner(prompt).strip()

        agent = Agent(
            name="BrifAI Briefing Agent",
            model=Groq(id=self.model_id, api_key=self.model_api_key),
            markdown=True,
            instructions=self._instructions(),
        )
        result = agent.run(prompt)
        return result.get_content_as_string().strip()

    def _instructions(self) -> list[str]:
        return [
            "You create concise daily news briefings in Markdown.",
            "Write in Brazilian Portuguese.",
            "Use this structure: title, executive summary, bullet highlights.",
            "Avoid repeating the same fact across highlights.",
            "Mention the source for each highlight.",
            "If the provided articles are weak, be transparent and cautious.",
        ]

    def _build_prompt(
        self,
        topic: str,
        keywords: list[str],
        articles: List[NewsArticle],
    ) -> str:
        keyword_text = ", ".join(keywords) if keywords else "none"
        articles_text = self._format_articles(articles)
        return (
            f"Topic: {topic}\n"
            f"Keywords: {keyword_text}\n"
            "Create a daily briefing with a short executive summary and up to "
            "5 highlights.\n"
            "Articles:\n"
            f"{articles_text}"
        )

    def _format_articles(self, articles: List[NewsArticle]) -> str:
        blocks = []
        for index, article in enumerate(articles, start=1):
            blocks.append(
                f"{index}. Title: {article.title}\n"
                f"Summary: {article.summary}\n"
                f"Source: {article.source}\n"
                f"URL: {article.url}"
            )
        return "\n\n".join(blocks)

    def _empty_briefing(self, topic: str) -> str:
        return (
            "# Daily Briefing\n\n"
            f"No recent articles were found for `{topic}` at this time."
        )

    def _create_fallback_briefing(
        self,
        topic: str,
        articles: List[NewsArticle],
    ) -> str:
        highlights = [self._format_highlight(i, a) for i, a in enumerate(articles, 1)]
        return (
            "# Daily Briefing\n\n"
            f"## Executive Summary\nRecent updates were collected for `{topic}`. "
            "AI summarization was unavailable, so this fallback briefing lists "
            "the most relevant articles directly.\n\n"
            "## Highlights\n"
            f"{''.join(highlights)}"
        )

    def _format_highlight(self, index: int, article: NewsArticle) -> str:
        return (
            f"- **{index}. {article.title}**\n"
            f"  {article.summary}\n"
            f"  Source: {article.source}\n"
            f"  Link: {article.url}\n"
        )

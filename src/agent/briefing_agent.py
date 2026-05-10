from typing import List

from src.interfaces.news_fetcher import INewsFetcher
from src.core.models import NewsArticle


class BriefingAgent:
    def __init__(self, fetcher: INewsFetcher):
        self.fetcher = fetcher

    def create_briefing(
        self,
        topic: str = "general",
        keywords: list[str] | None = None,
        max_results: int = 5,
    ) -> str:
        keywords = keywords or []
        articles: List[NewsArticle] = self.fetcher.fetch_recent_news(
            topic=topic, keywords=keywords, max_results=max_results
        )

        if not articles:
            return "No news articles available at this time."

        lines = []
        for index, article in enumerate(articles, start=1):
            lines.append(
                f"**{index}. {article.title}**\n{article.summary}\n{article.url}\nSource: {article.source}"
            )

        return "\n\n".join(lines)

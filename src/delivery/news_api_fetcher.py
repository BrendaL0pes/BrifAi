from typing import List

from src.interfaces.news_fetcher import INewsFetcher
from src.core.models import NewsArticle


class NewsApiFetcher(INewsFetcher):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_recent_news(
        self, topic: str, keywords: list[str], max_results: int = 5
    ) -> List[NewsArticle]:
        if not self.api_key:
            return []

        query = topic
        if keywords:
            query = " ".join([query, *keywords])

        return [
            NewsArticle(
                title=f"Sample news for {topic}",
                url="https://example.com/news",
                summary=f"This is a sample briefing item for '{query}'.",
                source="Example News",
            )
        ][:max_results]

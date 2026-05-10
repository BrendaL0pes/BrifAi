import httpx
from typing import List

from src.interfaces.news_fetcher import INewsFetcher
from src.core.models import NewsArticle

BASE_URL = "https://newsapi.org/v2/everything"


class NewsApiFetcher(INewsFetcher):
    """Fetches news articles from NewsAPI.org using async HTTP requests."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def fetch_recent_news(
        self, topic: str, keywords: list[str], max_results: int = 5
    ) -> List[NewsArticle]:
        """Fetches up to max_results articles for the given topic."""
        if not self._api_key:
            return []

        params = self._build_params(topic, keywords, max_results)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            return self._parse_articles(data)
        except (httpx.HTTPError, ValueError):
            return []

    def _build_params(
        self, topic: str, keywords: list[str], max_results: int
    ) -> dict[str, str | int]:
        query = " ".join([topic, *keywords]).strip() if keywords else topic
        return {
            "q": query,
            "pageSize": max_results,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": self._api_key,
        }

    def _parse_articles(self, data: dict) -> List[NewsArticle]:
        articles = []
        for item in data.get("articles", []):
            articles.append(
                NewsArticle(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    summary=item.get("description", ""),
                    source=item.get("source", {}).get("name", "Unknown"),
                )
            )
        return articles

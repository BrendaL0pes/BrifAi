"""NewsAPI fetcher implementation."""

import httpx

from src.core.models import NewsArticle
from src.interfaces.news_fetcher import INewsFetcher

BASE_URL = "https://newsapi.org/v2/everything"


class NewsApiFetcher(INewsFetcher):
    """Fetches news articles from NewsAPI.org."""

    def __init__(self, api_key: str) -> None:
        """Initializes the fetcher with the NewsAPI key."""
        self._api_key = api_key

    async def fetch_recent_news(
        self, topic: str, keywords: list[str], max_results: int
    ) -> list[NewsArticle]:
        """Fetches recent articles for the given topic and keywords."""
        params = self._build_params(topic, keywords, max_results)
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params)
        return self._parse_articles(response.json())

    def _build_params(self, topic: str, keywords: list[str], max_results: int) -> dict:
        """Builds the query parameters for the NewsAPI request."""
        query = " ".join([topic] + keywords)
        return {
            "q": query,
            "pageSize": max_results,
            "sortBy": "publishedAt",
            "language": "pt",
            "apiKey": self._api_key,
        }

    def _parse_articles(self, data: dict) -> list[NewsArticle]:
        """Parses the API response into a list of NewsArticle objects."""
        return [
            NewsArticle(
                title=a.get("title", ""),
                url=a.get("url", ""),
                summary=a.get("description") or "",
                source=a.get("source", {}).get("name", ""),
            )
            for a in data.get("articles", [])
        ]

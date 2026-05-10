"""NewsAPI implementation for fetching recent news articles."""
import logging
from typing import List

from newsapi import NewsApiClient

from src.core.models import NewsArticle
from src.interfaces.news_fetcher import INewsFetcher

logger = logging.getLogger(__name__)


class NewsAPIFetcher(INewsFetcher):
    """Fetches recent news articles from NewsAPI.org."""

    def __init__(self, api_key: str) -> None:
        """
        Initializes the NewsAPI client.

        Args:
            api_key: NewsAPI.org API key for authentication.
        """
        self.client = NewsApiClient(api_key=api_key)

    def fetch_recent_news(
        self, topic: str, keywords: List[str], max_results: int
    ) -> List[NewsArticle]:
        """
        Fetches recent news articles based on topic and keywords.

        Args:
            topic: The main subject of interest.
            keywords: Specific words to prioritize in the search.
            max_results: Maximum number of articles to return.

        Returns:
            A list of NewsArticle objects, or empty list on error.
        """
        try:
            query = self._build_query(topic, keywords)
            response = self.client.get_everything(
                q=query,
                language="en",
                sort_by="publishedAt",
                page_size=max_results,
            )
            return self._parse_articles(response)
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return []

    def _build_query(self, topic: str, keywords: List[str]) -> str:
        """Combines topic and keywords into a search query."""
        keyword_str = " ".join(keywords) if keywords else ""
        return f"{topic} {keyword_str}".strip()

    def _parse_articles(self, response: dict) -> List[NewsArticle]:
        """Converts API response into NewsArticle objects."""
        articles = []
        for item in response.get("articles", []):
            article = NewsArticle(
                title=item.get("title", ""),
                url=item.get("url", ""),
                summary=item.get("description", ""),
                source=item.get("source", {}).get("name", "Unknown"),
            )
            articles.append(article)
        return articles

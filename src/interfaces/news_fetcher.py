"""Interface for news fetching services."""
from abc import ABC, abstractmethod
from typing import List
from src.core.models import NewsArticle


class INewsFetcher(ABC):
    """Abstract base class for fetching news from external sources."""

    @abstractmethod
    def fetch_recent_news(
        self, topic: str, keywords: List[str], max_results: int
    ) -> List[NewsArticle]:
        """
        Fetches recent news articles based on topic and keywords.

        Args:
            topic: The main subject of interest.
            keywords: Specific words to look for.
            max_results: Maximum number of articles to return.

        Returns:
            A list of NewsArticle objects.
        """
        pass
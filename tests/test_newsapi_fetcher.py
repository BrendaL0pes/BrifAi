"""Unit tests for NewsAPI fetcher implementation."""
import unittest
from unittest.mock import MagicMock, patch

from src.core.models import NewsArticle
from src.services.newsapi_fetcher import NewsAPIFetcher


class TestNewsAPIFetcher(unittest.TestCase):
    """Tests for NewsAPIFetcher class."""

    def setUp(self) -> None:
        """Initialize test fixtures."""
        self.fetcher = NewsAPIFetcher(api_key="test_key")

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_fetch_recent_news_success(self, mock_client_class: MagicMock) -> None:
        """Test successful news fetching."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_everything.return_value = {
            "articles": [
                {
                    "title": "Test Article 1",
                    "url": "https://example.com/1",
                    "description": "Summary 1",
                    "source": {"name": "Test Source"},
                }
            ]
        }

        fetcher = NewsAPIFetcher(api_key="test_key")
        result = fetcher.fetch_recent_news("tech", ["ai"], 5)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], NewsArticle)
        self.assertEqual(result[0].title, "Test Article 1")

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_fetch_recent_news_api_error(self, mock_client_class: MagicMock) -> None:
        """Test graceful handling of API errors."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_everything.side_effect = Exception("API Error")

        fetcher = NewsAPIFetcher(api_key="test_key")
        result = fetcher.fetch_recent_news("tech", ["ai"], 5)

        self.assertEqual(result, [])

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_fetch_recent_news_empty_response(
        self, mock_client_class: MagicMock
    ) -> None:
        """Test handling of empty API response."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_everything.return_value = {"articles": []}

        fetcher = NewsAPIFetcher(api_key="test_key")
        result = fetcher.fetch_recent_news("nonexistent", ["topic"], 5)

        self.assertEqual(result, [])

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_build_query_with_keywords(self, mock_client_class: MagicMock) -> None:
        """Test query building with keywords."""
        fetcher = NewsAPIFetcher(api_key="test_key")
        query = fetcher._build_query("python", ["async", "frameworks"])

        self.assertEqual(query, "python async frameworks")

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_build_query_without_keywords(
        self, mock_client_class: MagicMock
    ) -> None:
        """Test query building without keywords."""
        fetcher = NewsAPIFetcher(api_key="test_key")
        query = fetcher._build_query("python", [])

        self.assertEqual(query, "python")

    @patch("src.services.newsapi_fetcher.NewsApiClient")
    def test_parse_articles_missing_fields(
        self, mock_client_class: MagicMock
    ) -> None:
        """Test parsing articles with missing optional fields."""
        fetcher = NewsAPIFetcher(api_key="test_key")
        response = {
            "articles": [
                {
                    "title": "Minimal Article",
                    "url": "https://example.com",
                    "source": {},
                }
            ]
        }

        result = fetcher._parse_articles(response)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Minimal Article")
        self.assertEqual(result[0].source, "Unknown")


if __name__ == "__main__":
    unittest.main()

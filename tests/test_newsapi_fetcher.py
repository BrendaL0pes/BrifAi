"""Unit tests for NewsApiFetcher."""
from unittest.mock import MagicMock

import httpx
import pytest
from src.core.models import NewsArticle
from src.delivery.news_api_fetcher import NewsApiFetcher


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self._data


class DummyAsyncClient:
    def __init__(self, response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        return self._response


class ErrorAsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, *args, **kwargs):
        raise httpx.HTTPError("Request failed")


class InvalidJsonResponse:
    def raise_for_status(self):
        return None

    def json(self):
        raise ValueError("Invalid JSON")


class TestNewsApiFetcher:
    @pytest.mark.asyncio
    async def test_fetch_recent_news_success(self, monkeypatch) -> None:
        response_data = {
            "articles": [
                {
                    "title": "Test Article",
                    "url": "https://example.com/test",
                    "description": "Summary",
                    "source": {"name": "Example Source"},
                }
            ]
        }
        monkeypatch.setattr(
            "src.delivery.news_api_fetcher.httpx.AsyncClient",
            lambda *args, **kwargs: DummyAsyncClient(DummyResponse(response_data)),
        )

        fetcher = NewsApiFetcher(api_key="test_key")
        result = await fetcher.fetch_recent_news("python", ["async"], 5)

        assert len(result) == 1
        assert isinstance(result[0], NewsArticle)
        assert result[0].title == "Test Article"
        assert result[0].source == "Example Source"

    @pytest.mark.asyncio
    async def test_fetch_recent_news_returns_empty_without_api_key(self) -> None:
        fetcher = NewsApiFetcher(api_key="")

        result = await fetcher.fetch_recent_news("python", ["async"], 5)

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_recent_news_handles_http_exceptions(self, monkeypatch) -> None:
        """Ensure HTTP client errors are caught and return an empty list."""
        monkeypatch.setattr(
            "src.delivery.news_api_fetcher.httpx.AsyncClient",
            lambda *args, **kwargs: ErrorAsyncClient(),
        )

        fetcher = NewsApiFetcher(api_key="test_key")
        result = await fetcher.fetch_recent_news("python", [], 5)

        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_recent_news_handles_invalid_json(self, monkeypatch) -> None:
        """Invalid JSON from the response should result in [] rather than raising."""
        monkeypatch.setattr(
            "src.delivery.news_api_fetcher.httpx.AsyncClient",
            lambda *args, **kwargs: DummyAsyncClient(InvalidJsonResponse()),
        )

        fetcher = NewsApiFetcher(api_key="test_key")
        result = await fetcher.fetch_recent_news("python", ["async"], 5)

        assert result == []

    def test_build_params(self) -> None:
        fetcher = NewsApiFetcher(api_key="test_key")

        params = fetcher._build_params("python", ["async", "pytest"], 3)

        assert params["q"] == "python async pytest"
        assert params["pageSize"] == 3
        assert params["apiKey"] == "test_key"
        assert params["language"] == "en"

    def test_build_params(self) -> None:
        """Build parameters correctly when keywords are provided."""
        fetcher = NewsApiFetcher(api_key="test_key")

        params = fetcher._build_params("python", ["async", "pytest"], 3)

        assert params["q"] == "python async pytest"
        assert params["pageSize"] == 3
        assert params["apiKey"] == "test_key"
        assert params["language"] == "en"

    def test_build_params_without_keywords(self) -> None:
        """Build parameters correctly when the keyword list is empty."""
        fetcher = NewsApiFetcher(api_key="test_key")

        params = fetcher._build_params("python", [], 3)

        assert params["q"] == "python"
        assert params["pageSize"] == 3
        assert params["apiKey"] == "test_key"
        assert params["language"] == "en"

    def test_parse_articles_handles_missing_source_name(self) -> None:
        """Parse articles gracefully when the API source object lacks a name."""
        fetcher = NewsApiFetcher(api_key="test_key")

        result = fetcher._parse_articles(
            {
                "articles": [
                    {
                        "title": "Minimal Article",
                        "url": "https://example.com",
                        "description": "Desc",
                        "source": {},
                    }
                ]
            }
        )

        assert len(result) == 1
        assert result[0].title == "Minimal Article"
        assert result[0].source == "Unknown"

    def test_parse_articles_returns_empty_for_missing_articles(self) -> None:
        """Return an empty list when the API response contains no articles field."""
        fetcher = NewsApiFetcher(api_key="test_key")

        result = fetcher._parse_articles({"status": "ok"})

        assert result == []

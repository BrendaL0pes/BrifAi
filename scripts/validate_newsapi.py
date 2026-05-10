"""Manual validation script for NewsAPI integration with real API calls."""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.newsapi_fetcher import NewsAPIFetcher


def main() -> None:
    """Validate NewsAPI fetcher with real API calls."""
    load_dotenv()
    api_key = os.getenv("NEWS_API_KEY")

    if not api_key:
        print("❌ ERROR: NEWS_API_KEY not found in .env file")
        print("Please add NEWS_API_KEY=<your_key> to .env")
        sys.exit(1)

    print("🔄 Initializing NewsAPIFetcher...")
    fetcher = NewsAPIFetcher(api_key=api_key)

    print("📡 Fetching news about 'technology' with keywords ['AI', 'machine learning']...")
    articles = fetcher.fetch_recent_news(
        topic="technology", keywords=["AI", "machine learning"], max_results=5
    )

    if not articles:
        print("⚠️  No articles returned (check API key or rate limits)")
        return

    print(f"\n✅ Successfully fetched {len(articles)} articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   URL: {article.url}")
        print(f"   Summary: {article.summary[:100]}...\n")


if __name__ == "__main__":
    main()

import asyncio

from agno.agent import Agent
from agno.models.groq import Groq

from src.core.models import Briefing, UserPreferences
from src.interfaces.news_fetcher import INewsFetcher

SYSTEM_PROMPT = """
You are a professional news briefing assistant.
For each topic provided, use the fetch_news tool to retrieve articles.
Summarize each article in 2-3 sentences.
Format the output in Markdown with one ## section per topic.
Respect the max_news_per_topic limit.
Output ONLY the Markdown briefing — no extra commentary.
"""


class BriefingAgent:
    """Generates briefing content using an AI agent and news tools."""

    def __init__(self, fetcher: INewsFetcher, model_id: str = "llama-3.1-8b-instant") -> None:
        self._fetcher = fetcher
        self._agent = Agent(
            name="BriefingAgent",
            model=Groq(id=model_id),
            instructions=SYSTEM_PROMPT,
            tools=[self._fetch_news],
        )
        self._use_arun = hasattr(self._agent, "arun")

    async def _fetch_news(
        self, topic: str, keywords: list[str], max_results: int
    ) -> str:
        articles = await self._fetcher.fetch_recent_news(topic, keywords, max_results)
        return "\n".join(
            f"- {article.title}: {article.summary}" for article in articles
        )

    async def generate_briefing(self, preferences: UserPreferences) -> Briefing:
        prompt = (
            f"Generate a briefing for topics: {preferences.topics}. "
            f"Max {preferences.max_news_per_topic} articles per topic."
        )
        if self._use_arun:
            response = await self._agent.arun(prompt)
        else:
            response = await asyncio.to_thread(self._agent.run, prompt)

        return Briefing(
            user_email=preferences.email_address,
            discord_channel_id=preferences.discord_channel_id,
            content_markdown=response.content,
        )

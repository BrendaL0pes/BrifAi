"""Briefing agent implementation using the Agno framework."""
import asyncio

from agno.agent import Agent
from agno.models.groq import Groq

from src.core.models import Briefing, UserPreferences
from src.interfaces.news_fetcher import INewsFetcher

SYSTEM_PROMPT = """
You are an Elite Intelligence Analyst. Your mission is to transform raw news into a high-impact executive briefing.

STRICT RULES:
- Call the fetch tool EXACTLY ONCE per topic using only the topic name.
- Output ONLY the final briefing in Markdown.
- Language: Portuguese (Brazil).
- Tone: Analytical, sharp, and insightful.

EXACT STRUCTURE TO FOLLOW:

# 🚀 BrifAI | Intelligence Report
---

## 📂 Tópico: [Topic Name]

### 🛰️ **[Título da Notícia]**
> 🖋️ **Fonte:** [Fonte] | 🔗 <[URL]>

**🔍 ANÁLISE EXECUTIVA**
[Análise profunda de 2 frases sobre o impacto dessa notícia.]

**📌 DESTAQUES:**
• **O Fato:** [Acontecimento principal em uma linha]
• **A Relevância:** [Por que o usuário deveria se importar com isso hoje?]

---

- Do not include extra summaries or introduction text.
- If no news is found, skip the topic.
- Keep the formatting clean for high-end readability.
"""


class BriefingAgent:
    """Generates briefing content using an AI agent and news tools."""

    def __init__(
        self, fetcher: INewsFetcher, model_id: str = "llama-3.1-8b-instant"
    ) -> None:
        """Initializes the agent with a news fetcher and Groq model."""
        self._fetcher = fetcher
        self._agent = Agent(
            name="BriefingAgent",
            model=Groq(id=model_id),
            instructions=SYSTEM_PROMPT,
            tools=[self._fetch_news],
        )
        self._use_arun = hasattr(self._agent, "arun")

    async def _fetch_news(self, topic: str) -> str:
        """Fetches recent news articles for a given topic.

        Args:
            topic: The news topic to search for (e.g. 'tecnologia', 'IA').

        Returns:
            Formatted string with title, source, description and url.
        """
        articles = await self._fetcher.fetch_recent_news(topic, [], 5)
        return "\n\n".join(
            f"Título: {a.title}\n"
            f"Autor: {a.source}\n"
            f"Descrição: {a.summary}\n"
            f"URL: <{a.url}>"
            for a in articles
        )

    async def generate_briefing(self, preferences: UserPreferences) -> Briefing:
        """Generates a briefing for all user topics."""
        prompt = f"Generate a briefing for these topics: {preferences.topics}."
        if self._use_arun:
            response = await self._agent.arun(prompt)
        else:
            response = await asyncio.to_thread(self._agent.run, prompt)
        return Briefing(
            user_email=preferences.email_address,
            discord_channel_id=preferences.discord_channel_id,
            content_markdown=response.content,
        )

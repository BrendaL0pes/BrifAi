"""Entry point for the Briefy application."""
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import discord
import nest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from src.agent.briefing_agent import BriefingAgent
from src.bot.discord_bot import DiscordBotManager
from src.delivery.discord_delivery import DiscordDeliveryService
from src.delivery.news_api_fetcher import NewsApiFetcher
from src.delivery.scheduler import BriefingScheduler
from src.delivery.smtp_email_service import SmtpEmailService
from src.storage.json_storage import JsonPreferencesStorage

def main() -> None:
    """Loads configuration, assembles dependencies, and starts the Discord client."""
    load_dotenv()
    nest_asyncio.apply()

    discord_token = os.getenv("DISCORD_BOT_TOKEN", "")
    if not discord_token:
        raise RuntimeError("DISCORD_BOT_TOKEN is required")

    storage = JsonPreferencesStorage("data/users.json")
    fetcher = NewsApiFetcher(api_key=os.getenv("NEWS_API_KEY", ""))
    agent = BriefingAgent(
        fetcher=fetcher,
        model_id=os.getenv("GROQ_MODEL_ID", "llama-3.1-8b-instant"),
    )
    email_service = SmtpEmailService()

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    discord_service = DiscordDeliveryService(client=client)
    scheduler = BriefingScheduler(
        storage=storage,
        agent=agent,
        email_senders=[email_service],
        discord_notifiers=[discord_service],
    )

    apscheduler = AsyncIOScheduler()
    apscheduler.add_job(scheduler.run_daily_job, "cron", hour=7, minute=0)

    bot_manager = DiscordBotManager(client=client, storage=storage)
    bot_manager.register_events()

    @client.event
    async def on_ready() -> None:
        if not apscheduler.running:
            apscheduler.start()
        print(f"Bot online: {client.user}")

    client.run(discord_token)


if __name__ == "__main__":
    main()
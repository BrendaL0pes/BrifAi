import os

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from src.agent.briefing_agent import BriefingAgent
from src.bot.discord_bot import DiscordBotManager
from src.delivery.discord_delivery import DiscordDeliveryService
from src.delivery.news_api_fetcher import NewsApiFetcher
from src.delivery.scheduler import BriefingScheduler
from src.delivery.smtp_email_service import SmtpEmailService
from src.storage.json_storage import JsonPreferencesStorage

load_dotenv()


def build_agent(fetcher: NewsApiFetcher) -> BriefingAgent:
    return BriefingAgent(
        fetcher=fetcher,
        model_api_key=os.getenv("GROQ_API_KEY"),
        model_id=os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile"),
    )


storage = JsonPreferencesStorage("data/users.json")
fetcher = NewsApiFetcher(api_key=os.getenv("NEWS_API_KEY"))
agent = build_agent(fetcher)
email_svc = SmtpEmailService()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

discord_svc = DiscordDeliveryService(client=client)
scheduler = BriefingScheduler(storage, agent, [email_svc], [discord_svc])
apscheduler = AsyncIOScheduler()
apscheduler.add_job(scheduler.run_daily_job, "cron", hour=7)

bot_manager = DiscordBotManager(client=client, storage=storage)
bot_manager.register_events()


@client.event
async def on_ready():
    apscheduler.start()
    print(f"Bot online: {client.user}")


client.run(os.getenv("DISCORD_BOT_TOKEN"))

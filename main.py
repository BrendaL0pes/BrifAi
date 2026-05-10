import os
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from src.storage.json_storage import JsonPreferencesStorage
from src.delivery.news_api_fetcher import NewsApiFetcher
from src.delivery.smtp_email_service import SmtpEmailService
from src.delivery.discord_delivery import DiscordDeliveryService
from src.delivery.scheduler import BriefingScheduler
from src.agent.briefing_agent import BriefingAgent
from src.bot.discord_bot import DiscordBotManager

load_dotenv()

storage = JsonPreferencesStorage("data/preferences.json")
fetcher = NewsApiFetcher(api_key=os.getenv("NEWS_API_KEY"))
agent = BriefingAgent(fetcher=fetcher)
email_svc = SmtpEmailService()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

discord_svc = DiscordDeliveryService(client=client)
scheduler = BriefingScheduler(storage, agent, [email_svc], [discord_svc])
apscheduler = AsyncIOScheduler()
apscheduler.add_job(scheduler.run_daily_job, "cron", hour=7)

bot_manager = DiscordBotManager(client=client, storage=storage, scheduler=scheduler)
bot_manager.register_events()


@client.event
async def on_ready():
    apscheduler.start()
    print(f"Bot online: {client.user}")


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_BOT_TOKEN"))

from typing import List

from src.agent.briefing_agent import BriefingAgent
from src.interfaces.discord_notifier import IDiscordNotifier
from src.interfaces.email_sender import IEmailSender
from src.interfaces.preferences_storage import IPreferencesStorage


class BriefingScheduler:
    def __init__(
        self,
        storage: IPreferencesStorage,
        agent: BriefingAgent,
        email_services: List[IEmailSender],
        discord_services: List[IDiscordNotifier],
    ):
        self.storage = storage
        self.agent = agent
        self.email_services = email_services
        self.discord_services = discord_services

    def run_daily_job(self) -> None:
        users = self.storage.get_all_users()
        for user in users:
            briefing = self.agent.create_briefing(
                topic=", ".join(user.topics or ["general"]),
                keywords=user.keywords,
                max_results=user.max_news_per_topic,
            )

            if user.email_address:
                for service in self.email_services:
                    service.send_briefing(user.email_address, briefing)

            if user.discord_channel_id:
                for service in self.discord_services:
                    service.send_message(user.discord_channel_id, briefing)

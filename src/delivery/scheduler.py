import logging
from typing import List

from src.agent.briefing_agent import BriefingAgent
from src.core.models import Briefing
from src.interfaces.discord_notifier import IDiscordNotifier
from src.interfaces.email_sender import IEmailSender
from src.interfaces.preferences_storage import IPreferencesStorage

logger = logging.getLogger(__name__)


class BriefingScheduler:
    """Orchestrates daily briefing generation and delivery."""

    def __init__(
        self,
        storage: IPreferencesStorage,
        agent: BriefingAgent,
        email_senders: List[IEmailSender],
        discord_notifiers: List[IDiscordNotifier],
    ) -> None:
        self._storage = storage
        self._agent = agent
        self._emails = email_senders
        self._discord = discord_notifiers

    async def run_daily_job(self) -> None:
        """Generates and delivers briefings for all registered users."""
        for user in self._storage.get_all_users():
            briefing = await self._agent.generate_briefing(user)
            await self._deliver(briefing)

    async def _deliver(self, briefing: Briefing) -> None:
        for sender in self._emails:
            try:
                sender.send_briefing(briefing.user_email, briefing.content_markdown)
            except Exception as exception:
                logger.error("Email failed for %s: %s", briefing.user_email, exception)

        for notifier in self._discord:
            try:
                await notifier.send_message(briefing.discord_channel_id, briefing.content_markdown)
            except Exception as exception:
                logger.error("Discord failed for %s: %s", briefing.discord_channel_id, exception)

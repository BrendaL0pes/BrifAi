from abc import ABC, abstractmethod
from typing import Optional
from src.core.models import UserPreferences
 
class IPreferencesStorage(ABC):
    @abstractmethod
    def save_user(self, preferences: UserPreferences) -> bool: pass
    @abstractmethod
    def get_user(self, discord_channel_id: str) -> Optional[UserPreferences]: pass
    @abstractmethod
    def get_all_users(self) -> list[UserPreferences]: pass
 
 
# news_fetcher.py
from src.core.models import NewsArticle
 
class INewsFetcher(ABC):
    @abstractmethod
    async def fetch_recent_news(
        self, topic: str, keywords: list[str], max_results: int
    ) -> list[NewsArticle]: pass
 
 
# email_sender.py
class IEmailSender(ABC):
    @abstractmethod
    def send_briefing(self, to_email: str, markdown_content: str) -> bool: pass
 
 
# discord_notifier.py
class IDiscordNotifier(ABC):
    @abstractmethod
    async def send_message(
        self, channel_id: str, markdown_content: str
    ) -> bool: pass


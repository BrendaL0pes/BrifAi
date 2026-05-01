from dataclasses import dataclass, field
 
@dataclass
class UserPreferences:
    discord_channel_id: str
    email_address: str
    topics: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    max_news_per_topic: int = 5
 
@dataclass
class NewsArticle:
    title: str
    url: str
    summary: str
    source: str
 
@dataclass
class Briefing:
    user_email: str
    discord_channel_id: str
    content_markdown: str


"""Interface for Discord notification services."""
from abc import ABC, abstractmethod


class IDiscordNotifier(ABC):
    """Abstract base class for sending messages to Discord channels."""

    @abstractmethod
    def send_message(self, channel_id: str, markdown_content: str) -> bool:
        """
        Sends a message to a specific Discord channel.

        Args:
            channel_id: The ID of the target Discord channel.
            markdown_content: The message content formatted in Markdown.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        pass
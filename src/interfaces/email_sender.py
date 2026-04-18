"""Interface for email sending services."""
from abc import ABC, abstractmethod


class IEmailSender(ABC):
    """Abstract base class for email notification services."""

    @abstractmethod
    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        """
        Sends the consolidated briefing to the user's email.

        Args:
            to_email: Destination email address.
            markdown_content: The briefing content formatted in Markdown.

        Returns:
            True if the email was sent successfully, False otherwise.
        """
        pass
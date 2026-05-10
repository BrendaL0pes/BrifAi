"""SMTP-based email sender implementation."""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import markdown2

from src.interfaces.email_sender import IEmailSender

logger = logging.getLogger(__name__)


class SMTPEmailSender(IEmailSender):
    """Sends briefings via SMTP email."""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        sender_email: str,
    ) -> None:
        """
        Initializes SMTP email sender.

        Args:
            smtp_server: SMTP server hostname (e.g., smtp.gmail.com).
            smtp_port: SMTP port (usually 587 for TLS).
            username: SMTP username.
            password: SMTP password (or app-specific password).
            sender_email: From address for emails.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email

    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        """
        Sends briefing via email.

        Args:
            to_email: Recipient email address.
            markdown_content: Briefing content in Markdown format.

        Returns:
            True if sent successfully, False otherwise.
        """
        try:
            html_content = self._convert_markdown_to_html(markdown_content)
            message = self._build_email(to_email, html_content)
            self._send_smtp(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def _convert_markdown_to_html(self, markdown_content: str) -> str:
        """Converts Markdown to HTML."""
        html = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])
        return f"<html><body>{html}</body></html>"

    def _build_email(self, to_email: str, html_content: str) -> MIMEMultipart:
        """Builds MIME email message."""
        message = MIMEMultipart("alternative")
        message["From"] = self.sender_email
        message["To"] = to_email
        message["Subject"] = "Your BrifAI Daily Briefing"
        message.attach(MIMEText(html_content, "html"))
        return message

    def _send_smtp(self, message: MIMEMultipart) -> None:
        """Sends message via SMTP."""
        with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(message)

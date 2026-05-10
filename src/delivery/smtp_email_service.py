"""SMTP email service implementation."""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.interfaces.email_sender import IEmailSender


class SmtpEmailService(IEmailSender):
    """Sends briefings via SMTP (Gmail-compatible)."""

    def __init__(self) -> None:
        """Reads SMTP credentials from environment variables."""
        self._host     = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self._port     = int(os.getenv("SMTP_PORT", "587"))
        self._user     = os.getenv("SMTP_USER", "")
        self._password = os.getenv("SMTP_PASSWORD", "")
        self._from_email = os.getenv("SMTP_FROM_EMAIL") or self._user

    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        """Sends the briefing as a plain text email."""
        if not self._user or not self._password:
            raise ValueError(
                "SMTP credentials are missing. Set SMTP_USER and SMTP_PASSWORD in the environment."
            )
        msg = self._build_mime(to_email, markdown_content)
        return self._send_via_smtp(msg)

    def _build_mime(self, to_email: str, content: str) -> MIMEMultipart:
        """Builds the MIME message object."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your Daily Briefing — BrifAI"
        msg["From"]    = self._from_email
        msg["To"]      = to_email
        msg.attach(MIMEText(content, "plain"))
        return msg

    def _send_via_smtp(self, msg: MIMEMultipart) -> bool:
        """Opens SMTP connection and sends the message."""
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(msg)
        return True

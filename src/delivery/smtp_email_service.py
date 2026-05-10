import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.interfaces.email_sender import IEmailSender


class SmtpEmailService(IEmailSender):
    """Sends briefings via SMTP (Gmail-compatible) using environment settings."""

    def __init__(self) -> None:
        self._host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self._port = int(os.getenv("SMTP_PORT", "587"))
        self._user = os.getenv("SMTP_USER", "")
        self._password = os.getenv("SMTP_PASSWORD", "")

    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        """Sends markdown briefing content via SMTP."""
        if not to_email or not markdown_content:
            return False

        if not self._user or not self._password:
            return False

        try:
            message = self._build_mime(to_email, markdown_content)
            self._send_via_smtp(message)
            return True
        except Exception:
            return False

    def _build_mime(self, to_email: str, content: str) -> MIMEMultipart:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Daily Briefing"
        message["From"] = self._user
        message["To"] = to_email
        message.attach(MIMEText(content, "plain"))
        return message

    def _send_via_smtp(self, message: MIMEMultipart) -> None:
        with smtplib.SMTP(self._host, self._port, timeout=10) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(message)

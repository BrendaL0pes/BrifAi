"""SMTP email service implementation."""

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.interfaces.email_sender import IEmailSender


class SmtpEmailService(IEmailSender):
    """Sends briefings via SMTP (Gmail-compatible)."""

    def __init__(self) -> None:
        """Reads SMTP credentials from environment variables."""
        self._host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self._port = int(os.getenv("SMTP_PORT", "587"))
        self._user = os.getenv("SMTP_USER", "")
        self._password = os.getenv("SMTP_PASSWORD", "")

    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        """Sends the briefing as plain text and HTML email."""
        msg = self._build_mime(to_email, markdown_content)
        return self._send_via_smtp(msg)

    def _build_mime(self, to_email: str, content: str) -> MIMEMultipart:
        """Builds the MIME message with plain text and HTML parts."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "📰 BrifAI — Seu Briefing Diário"
        msg["From"] = self._user
        msg["To"] = to_email
        msg.attach(MIMEText(content, "plain"))
        msg.attach(MIMEText(self._to_html(content), "html"))
        return msg

    def _to_html(self, markdown: str) -> str:
        """Converts basic Markdown to HTML for email rendering."""
        html = markdown
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = html.replace("\n\n", "</p><p>")
        html = html.replace("---", "<hr>")
        return f"<html><body style='font-family:Arial;max-width:600px;margin:auto;padding:20px'><p>{html}</p></body></html>"

    def _send_via_smtp(self, msg: MIMEMultipart) -> bool:
        """Opens SMTP connection and sends the message."""
        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(msg)
        return True

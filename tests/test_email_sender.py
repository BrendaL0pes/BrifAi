"""Unit tests for SmtpEmailService.

These tests verify the delivery-layer SMTP implementation used by the current application.
They exercise successful send, early validation failure, and SMTP error handling.
"""
from unittest.mock import MagicMock, patch

from src.delivery.smtp_email_service import SmtpEmailService


class TestSmtpEmailService:
    """Tests for SmtpEmailService."""

    @patch("src.delivery.smtp_email_service.smtplib.SMTP")
    def test_send_briefing_success(self, mock_smtp_class: MagicMock) -> None:
        """Ensure email delivery succeeds with valid credentials and content."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        service = SmtpEmailService()
        service._user = "test@gmail.com"
        service._password = "test_password"

        result = service.send_briefing("recipient@example.com", "Hello from BrifAI.")

        assert result is True
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "test_password")
        mock_smtp.send_message.assert_called_once()

    @patch("src.delivery.smtp_email_service.smtplib.SMTP")
    def test_send_briefing_fails_without_credentials(
        self, mock_smtp_class: MagicMock
    ) -> None:
        service = SmtpEmailService()
        service._user = ""
        service._password = ""

        result = service.send_briefing("recipient@example.com", "content")

        assert result is False
        mock_smtp_class.assert_not_called()

    @patch("src.delivery.smtp_email_service.smtplib.SMTP")
    def test_send_briefing_handles_smtp_exception(
        self, mock_smtp_class: MagicMock
    ) -> None:
        """If SMTP fails, send_briefing should return False."""
        mock_smtp_class.side_effect = Exception("SMTP failure")

        service = SmtpEmailService()
        service._user = "test@gmail.com"
        service._password = "test_password"

        result = service.send_briefing("recipient@example.com", "content")

        assert result is False

    def test_send_briefing_returns_false_for_missing_recipient_or_content(self) -> None:
        """Validate early-return checks for empty recipient or empty content."""
        service = SmtpEmailService()
        service._user = "sender@example.com"
        service._password = "password"

        assert service.send_briefing("", "Content") is False
        assert service.send_briefing("recipient@example.com", "") is False

    def test_build_mime_message(self) -> None:
        service = SmtpEmailService()
        service._user = "sender@example.com"
        service._password = "password"

        message = service._build_mime("recipient@example.com", "Hello")

        assert message["From"] == "sender@example.com"
        assert message["To"] == "recipient@example.com"
        assert message["Subject"] == "Your Daily Briefing"
        assert message.get_payload()[0].get_content_type() == "text/plain"

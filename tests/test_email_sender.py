"""Unit tests for email sender implementation."""
import unittest
from unittest.mock import MagicMock, patch

from src.services.email_sender import SMTPEmailSender


class TestSMTPEmailSender(unittest.TestCase):
    """Tests for SMTPEmailSender class."""

    def setUp(self) -> None:
        """Initialize test fixtures."""
        self.sender = SMTPEmailSender(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            username="test@gmail.com",
            password="test_password",
            sender_email="test@gmail.com",
        )

    @patch("src.services.email_sender.smtplib.SMTP")
    def test_send_briefing_success(self, mock_smtp_class: MagicMock) -> None:
        """Test successful email sending."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp

        result = self.sender.send_briefing(
            "recipient@example.com", "# Test Briefing\n\nThis is a test."
        )

        self.assertTrue(result)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("test@gmail.com", "test_password")

    @patch("src.services.email_sender.smtplib.SMTP")
    def test_send_briefing_connection_error(
        self, mock_smtp_class: MagicMock
    ) -> None:
        """Test handling of connection errors."""
        mock_smtp_class.side_effect = Exception("Connection refused")

        result = self.sender.send_briefing("recipient@example.com", "Content")

        self.assertFalse(result)

    @patch("src.services.email_sender.smtplib.SMTP")
    def test_send_briefing_auth_error(self, mock_smtp_class: MagicMock) -> None:
        """Test handling of authentication errors."""
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        mock_smtp.login.side_effect = Exception("535 Authentication failed")

        result = self.sender.send_briefing("recipient@example.com", "Content")

        self.assertFalse(result)

    def test_convert_markdown_to_html(self) -> None:
        """Test Markdown to HTML conversion."""
        markdown = "# Title\n\n**Bold text**\n\n- Item 1\n- Item 2"
        html = self.sender._convert_markdown_to_html(markdown)

        self.assertIn("<h1>", html)
        self.assertIn("<strong>", html)
        self.assertIn("<li>", html)
        self.assertIn("<html>", html)

    def test_build_email_structure(self) -> None:
        """Test email message structure."""
        message = self.sender._build_email(
            "recipient@example.com", "<p>Test content</p>"
        )

        self.assertEqual(message["From"], "test@gmail.com")
        self.assertEqual(message["To"], "recipient@example.com")
        self.assertEqual(message["Subject"], "Your BrifAI Daily Briefing")

    @patch("src.services.email_sender.smtplib.SMTP")
    def test_send_briefing_timeout(self, mock_smtp_class: MagicMock) -> None:
        """Test handling of SMTP timeout."""
        mock_smtp_class.side_effect = TimeoutError("Connection timeout")

        result = self.sender.send_briefing("recipient@example.com", "Content")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

from src.interfaces.email_sender import IEmailSender


class SmtpEmailService(IEmailSender):
    def send_briefing(self, to_email: str, markdown_content: str) -> bool:
        if not to_email or not markdown_content:
            return False
        return True

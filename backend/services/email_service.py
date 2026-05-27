import os
import smtplib
from email.message import EmailMessage
from urllib.parse import quote


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.from_email = os.getenv("EMAIL_FROM", self.smtp_user or "noreply@mindscape.ai")
        self.frontend_base_url = (os.getenv("FRONTEND_URL") or "https://hilary-frontend.onrender.com").rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_pass)

    def _send_email(self, to_email: str, subject: str, text_body: str, html_body: str):
        if not self.configured:
            raise RuntimeError("SMTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS.")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")

        try:
            # Explicitly ensure STARTTLS is called before logging in with timeout
            server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"SMTP Error: {e}")
            raise e

    def send_verification_email(self, to_email: str, token: str):
        verify_url = f"{self.frontend_base_url}/?verify_token={quote(token)}"
        subject = "Verify your MindScape account"
        text_body = (
            "Welcome to MindScape!\n\n"
            f"Please verify your email by opening this link:\n{verify_url}\n\n"
            "If you did not create this account, you can ignore this message."
        )
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.5;">
            <h2>Welcome to MindScape</h2>
            <p>Please verify your email address to activate your account.</p>
            <p><a href="{verify_url}" style="display:inline-block;padding:10px 16px;background:#2D5A4C;color:#fff;text-decoration:none;border-radius:6px;">Verify Email</a></p>
            <p>If the button does not work, copy and paste this URL into your browser:</p>
            <p>{verify_url}</p>
          </body>
        </html>
        """
        self._send_email(to_email, subject, text_body, html_body)


email_service = EmailService()

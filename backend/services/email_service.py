import os
import requests
from urllib.parse import quote

class EmailService:
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("EMAIL_FROM", "terhembafanushahemba@gmail.com")
        self.frontend_base_url = (os.getenv("FRONTEND_URL") or "https://hilary-frontend.onrender.com").rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _send_email(self, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
        if not self.configured:
            print("CRITICAL MAILER ERROR: BREVO_API_KEY environment variable is missing.")
            return False

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self.api_key
        }

        payload = {
            "sender": {
                "name": "Hilary Mindscape",
                "email": self.sender_email
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": subject,
            "textContent": text_body,
            "htmlContent": html_body
        }

        try:
            print(f"Routing HTTP post payload to Brevo API for recipient: {to_email}...")
            response = requests.post(url, json=payload, headers=headers, timeout=15)

            if response.status_code in [201, 202, 200]:
                print(f"HTTP mailing payload accepted by Brevo successfully (Code: {response.status_code}).")
                return True
            else:
                print(f"Brevo API rejected request with code {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"HTTP Mail pipeline failed to execute: {str(e)}")
            return False

    def send_verification_email(self, to_email: str, token: str) -> bool:
        # Note: The frontend uses /?verify_token=... according to previous App.jsx logic
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
        return self._send_email(to_email, subject, text_body, html_body)


email_service = EmailService()

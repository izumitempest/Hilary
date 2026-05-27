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
        # Note: The frontend handles verification at the root path via 'verify_token' query param
        verify_url = f"{self.frontend_base_url}/?verify_token={quote(token)}"
        subject = "Verify Your Account - MindScape"

        # Using concatenation to build the HTML body to avoid f-string escaping issues with CSS/HTML
        html_body = (
            "<html><body style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>"
            "<h2>Welcome to MindScape</h2>"
            "<p>Thank you for joining us! Please click the button below to verify your email address and activate your account:</p>"
            "<p style='margin: 25px 0;'>"
            "<a href='" + verify_url + "' style='background-color: #2D5A4C; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;'>"
            "Verify Email Address"
            "</a>"
            "</p>"
            "<p>If the button doesn't work, copy and paste this link into your browser:</p>"
            "<p style='word-break: break-all; color: #2D5A4C;'>" + verify_url + "</p>"
            "<br>"
            "<p style='font-size: 0.8em; color: #777;'>If you did not create this account, you can safely ignore this email.</p>"
            "</body></html>"
        )

        text_body = (
            "Welcome to MindScape!\n\n"
            f"Please verify your email by opening this link:\n{verify_url}\n\n"
            "If you did not create this account, you can ignore this message."
        )

        return self._send_email(to_email, subject, text_body, html_body)


email_service = EmailService()

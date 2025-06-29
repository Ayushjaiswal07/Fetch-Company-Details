import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from typing import Optional

class EmailSender:
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self):
        # Load environment variables
        load_dotenv()

        self.email_address: Optional[str] = os.getenv("EMAIL_ADDRESS")
        self.email_password: Optional[str] = os.getenv("EMAIL_PASSWORD")

        if not self.email_address or not self.email_password:
            raise EnvironmentError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in the .env file.")

    def send_email(self, to_email: str, body: str, subject: str = "Automated Email from Python") -> None:
        """
        Send an email using Gmail SMTP.

        Args:
            to_email (str): Recipient's email address.
            body (str): Plain text message body.
            subject (str): Subject of the email.
        """
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg.set_content(body)

            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(self.email_address, self.email_password)
                smtp.send_message(msg)

            print(f"✅ Email sent successfully to {to_email}")

        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

# # Sample usage
# if __name__ == "__main__":
#     sender = EmailSender()
#     sender.send_email(
#         to_email="jaiswalayush810@gmail.com",
#         body="Hello Ayush! This is a professional Python email class in action.",
#         subject="Test Email from Class"
#     )

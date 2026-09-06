import os
import smtplib # For email
from email.message import EmailMessage

def send_email(message):
    EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")
    EMAIL_RECIPIENTS = os.environ.get("EMAIL_RECIPIENTS")

    recipients = [email.strip() for email in EMAIL_RECIPIENTS.split(",") if email.strip()]

    print("RECIPIENTS:", recipients)

    msg = EmailMessage()
    msg["Subject"] = "AI Newsletter"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(recipients)

    msg.set_content(message)

    msg.add_alternative(message, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
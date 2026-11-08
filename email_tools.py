"""Email tools.

Sends an email (custom subject/body, or a constant template) through Gmail
SMTP (port 587, STARTTLS).
Settings come from environment variables (.env):
  EMAIL_SENDER        the Gmail address to send from
  EMAIL_APP_PASSWORD  its Gmail App Password (spaces are ignored)
"""

import os
import re
import smtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587  # STARTTLS

# Constant template. {recipient} is filled in by the tool.
EMAIL_SUBJECT = "Hello from Subroto's AI assistant"
EMAIL_BODY = """Hi {recipient},

This is an automated message sent by Subroto's tool-calling demo.

Regards,
Subroto
"""

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def send_email(to_email: str, subject: str = "", body: str = "") -> str:
    """Send an email. Uses the constant template when subject/body are empty."""
    to_email = to_email.strip()
    if not _EMAIL_RE.match(to_email):
        raise ValueError(f"Invalid email address: {to_email!r}")

    # Read at call time so values loaded from .env by main.py are picked up.
    sender = os.getenv("EMAIL_SENDER")
    password = (os.getenv("EMAIL_APP_PASSWORD") or "").replace(" ", "")
    if not sender or not password:
        raise RuntimeError("EMAIL_SENDER and EMAIL_APP_PASSWORD must be set in .env.")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject.strip() or EMAIL_SUBJECT
    msg.set_content(body or EMAIL_BODY.format(recipient=to_email))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    return f"Email sent from {sender} to {to_email}."


EMAIL_TOOL_SCHEMAS = [
    {
        "name": "send_email",
        "description": (
            "Send an email to one recipient. Provide a subject and body to send "
            "custom text (e.g. a summary you wrote). If both are omitted, a "
            "standard greeting template is sent. Use only when the user asks "
            "to send an email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {
                    "type": "string",
                    "description": "Recipient email address, e.g. name@example.com",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line. Optional.",
                },
                "body": {
                    "type": "string",
                    "description": "Plain-text email body. Optional.",
                },
            },
            "required": ["to_email"],
        },
    },
]

EMAIL_TOOL_FUNCTIONS = {
    "send_email": send_email,
}

# Tools that must be approved by the user in the terminal before running.
REQUIRES_CONFIRMATION = {"send_email"}

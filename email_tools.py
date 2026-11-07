"""Email tools.

Sends a constant-template email from SENDER_EMAIL through Gmail SMTP.
Needs a Gmail App Password in the EMAIL_APP_PASSWORD environment variable
(Google Account > Security > 2-Step Verification > App passwords).
"""

import os
import re
import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "subroto746@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL

# Constant template. {recipient} is filled in by the tool.
EMAIL_SUBJECT = "Hello from Subroto's AI assistant"
EMAIL_BODY = """Hi {recipient},

This is an automated message sent by Subroto's tool-calling demo.

Regards,
Subroto
"""

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def send_email(to_email: str) -> str:
    """Send the constant template email to `to_email`."""
    to_email = to_email.strip()
    if not _EMAIL_RE.match(to_email):
        raise ValueError(f"Invalid email address: {to_email!r}")

    password = os.getenv("EMAIL_APP_PASSWORD")
    if not password:
        raise RuntimeError("EMAIL_APP_PASSWORD is not set in the environment.")

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = EMAIL_SUBJECT
    msg.set_content(EMAIL_BODY.format(recipient=to_email))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SENDER_EMAIL, password)
        server.send_message(msg)

    return f"Email sent from {SENDER_EMAIL} to {to_email}."


EMAIL_TOOL_SCHEMAS = [
    {
        "name": "send_email",
        "description": (
            "Send the standard greeting email template to one recipient. "
            "Use only when the user asks to send an email."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {
                    "type": "string",
                    "description": "Recipient email address, e.g. name@example.com",
                }
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

from email.message import EmailMessage as MimeMessage

import aiosmtplib

from app.shared.mailer.email_message import EmailMessage
from app.shared.mailer.mailer import Mailer
from app.shared.mailer.smtp_security import SmtpSecurity


class SmtpMailer(Mailer):
    def __init__(
        self,
        host: str,
        port: int,
        sender: str,
        username: str | None = None,
        password: str | None = None,
        security: SmtpSecurity = SmtpSecurity.NONE,
    ) -> None:
        self._host = host
        self._port = port
        self._sender = sender
        self._username = username
        self._password = password
        self._security = security

    async def send(self, message: EmailMessage) -> None:
        mime_message = MimeMessage()
        mime_message["From"] = self._sender
        mime_message["To"] = message.recipient
        mime_message["Subject"] = message.subject
        mime_message.set_content(message.text)
        await aiosmtplib.send(
            mime_message,
            hostname=self._host,
            port=self._port,
            username=self._username,
            password=self._password,
            start_tls=self._security is SmtpSecurity.STARTTLS,
            use_tls=self._security is SmtpSecurity.TLS,
        )

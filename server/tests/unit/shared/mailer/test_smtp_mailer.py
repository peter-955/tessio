from email.message import EmailMessage as MimeMessage

import aiosmtplib
import pytest

from app.shared.mailer import EmailMessage, SmtpMailer, SmtpSecurity

MESSAGE = EmailMessage(recipient="olivia@tessio.test", subject="Welcome", text="Hello")


class RecordedSend:
    def __init__(self) -> None:
        self.messages: list[MimeMessage] = []
        self.options: list[dict[str, object]] = []

    async def __call__(self, message: MimeMessage, **options: object) -> None:
        self.messages.append(message)
        self.options.append(options)


@pytest.fixture
def recorded_send(monkeypatch: pytest.MonkeyPatch) -> RecordedSend:
    recorded = RecordedSend()
    monkeypatch.setattr(aiosmtplib, "send", recorded)
    return recorded


@pytest.mark.parametrize(
    ("security", "is_start_tls", "is_tls"),
    [(SmtpSecurity.NONE, False, False), (SmtpSecurity.STARTTLS, True, False), (SmtpSecurity.TLS, False, True)],
)
async def test_smtp_flags_follow_the_security_setting(
    recorded_send: RecordedSend, security: SmtpSecurity, is_start_tls: bool, is_tls: bool
) -> None:
    mailer = SmtpMailer("smtp.tessio.test", 587, "Tessio <no-reply@tessio.test>", "mailer", "p4ss", security)

    await mailer.send(MESSAGE)

    assert recorded_send.options == [
        {
            "hostname": "smtp.tessio.test",
            "port": 587,
            "username": "mailer",
            "password": "p4ss",
            "start_tls": is_start_tls,
            "use_tls": is_tls,
        }
    ]


async def test_mailpit_settings_send_without_credentials_or_tls(recorded_send: RecordedSend) -> None:
    mailer = SmtpMailer("localhost", 3206, "Tessio <no-reply@tessio.local>", None, None, SmtpSecurity.NONE)

    await mailer.send(MESSAGE)

    options = recorded_send.options[0]
    assert options["username"] is None
    assert options["password"] is None
    assert options["start_tls"] is False
    assert options["use_tls"] is False


async def test_the_message_has_the_sender_recipient_subject_and_text(recorded_send: RecordedSend) -> None:
    mailer = SmtpMailer("localhost", 3206, "Tessio <no-reply@tessio.local>", None, None, SmtpSecurity.NONE)

    await mailer.send(MESSAGE)

    sent_message = recorded_send.messages[0]
    assert sent_message["From"] == "Tessio <no-reply@tessio.local>"
    assert sent_message["To"] == "olivia@tessio.test"
    assert sent_message["Subject"] == "Welcome"
    assert sent_message.get_content().strip() == "Hello"

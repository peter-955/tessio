from app.modules.auth.typing.constants.auth_policy import INVITE_LIFETIME
from app.shared.mailer import EmailMessage


def build_invite_email(recipient: str, name: str, invite_url: str) -> EmailMessage:
    return EmailMessage(
        recipient=recipient,
        subject="You are invited to Tessio",
        text=(
            f"Hello {name},\n\n"
            "Set your password and two-factor authentication here:\n"
            f"{invite_url}\n\n"
            f"The link is valid for {INVITE_LIFETIME.days} days.\n"
        ),
    )

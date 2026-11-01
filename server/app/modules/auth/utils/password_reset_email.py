from app.modules.auth.typing.constants.auth_policy import PASSWORD_RESET_LIFETIME
from app.shared.mailer import EmailMessage


def build_password_reset_email(recipient: str, name: str, reset_url: str) -> EmailMessage:
    return EmailMessage(
        recipient=recipient,
        subject="Reset your Tessio password",
        text=(
            f"Hello {name},\n\n"
            "Choose a new password here:\n"
            f"{reset_url}\n\n"
            f"The link is valid for {int(PASSWORD_RESET_LIFETIME.total_seconds() // 60)} minutes. "
            "If you did not ask for it, ignore this email.\n"
        ),
    )

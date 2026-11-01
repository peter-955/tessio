from pydantic import JsonValue

from app.shared.mailer.email_message import EmailMessage
from app.shared.mailer.mailer import Mailer
from app.shared.queue import JobHandler


class SendEmailJobHandler(JobHandler):
    def __init__(self, mailer: Mailer) -> None:
        self._mailer = mailer

    async def handle(self, data: dict[str, JsonValue]) -> None:
        await self._mailer.send(EmailMessage.model_validate(data))

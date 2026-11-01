from app.shared.mailer.email_message import EmailMessage
from app.shared.mailer.mailer import Mailer
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName


class QueuedMailer(Mailer):
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    async def send(self, message: EmailMessage) -> None:
        await self._job_queue.add(QueueName.EMAIL, JobName.SEND_EMAIL, message.model_dump(mode="json"))

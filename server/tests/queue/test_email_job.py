import asyncio

from app.shared.mailer import EmailMessage, Mailer, QueuedMailer, SendEmailJobHandler
from app.shared.queue import BullmqJobQueue, BullmqJobWorker
from app.shared.typing.enums import JobName, QueueName

WORKER_TIMEOUT_SECONDS = 10


class SignallingMailer(Mailer):
    def __init__(self) -> None:
        self.messages: list[EmailMessage] = []
        self.received = asyncio.Event()

    async def send(self, message: EmailMessage) -> None:
        self.messages.append(message)
        self.received.set()


async def send_through_queue(redis_url: str, delivering_mailer: SignallingMailer, message: EmailMessage) -> None:
    job_queue = BullmqJobQueue(redis_url)
    job_worker = BullmqJobWorker(
        redis_url, QueueName.EMAIL, {JobName.SEND_EMAIL: SendEmailJobHandler(delivering_mailer)}
    )
    job_worker.start()
    try:
        await QueuedMailer(job_queue).send(message)
        await asyncio.wait_for(delivering_mailer.received.wait(), WORKER_TIMEOUT_SECONDS)
    finally:
        await job_worker.close()
        await job_queue.close()


async def test_queued_email_is_sent_by_the_worker(redis_url: str) -> None:
    message = EmailMessage(recipient="olivia@tessio.test", subject="You are invited to Tessio", text="Hello")
    delivering_mailer = SignallingMailer()

    await send_through_queue(redis_url, delivering_mailer, message)

    assert delivering_mailer.messages == [message]

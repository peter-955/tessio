from abc import ABC, abstractmethod

from app.shared.mailer.email_message import EmailMessage


class Mailer(ABC):
    @abstractmethod
    async def send(self, message: EmailMessage) -> None: ...

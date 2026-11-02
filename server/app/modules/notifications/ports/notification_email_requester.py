from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.modules.notifications.domains.notification_email_job.entity import NotificationEmailJob


class NotificationEmailRequester(ABC):
    @abstractmethod
    async def request(self, jobs: Sequence[NotificationEmailJob]) -> None: ...

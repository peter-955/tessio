from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob


class ChatDeliveryRequester(ABC):
    @abstractmethod
    async def request(self, jobs: Sequence[ChatDeliveryJob]) -> None: ...

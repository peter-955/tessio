from abc import ABC, abstractmethod
from uuid import UUID


class FlakyRecomputeRequester(ABC):
    @abstractmethod
    async def request(self, test_case_id: UUID) -> None: ...

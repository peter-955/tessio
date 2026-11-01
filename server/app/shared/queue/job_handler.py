from abc import ABC, abstractmethod

from pydantic import JsonValue


class JobHandler(ABC):
    @abstractmethod
    async def handle(self, data: dict[str, JsonValue]) -> None: ...

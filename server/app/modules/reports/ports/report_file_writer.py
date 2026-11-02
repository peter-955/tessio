from abc import ABC, abstractmethod


class ReportFileWriter(ABC):
    @abstractmethod
    async def write(self, key: str, content: bytes, content_type: str) -> None: ...

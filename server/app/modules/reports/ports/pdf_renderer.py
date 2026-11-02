from abc import ABC, abstractmethod


class PdfRenderer(ABC):
    @abstractmethod
    async def render(self, html: str) -> bytes: ...

from abc import ABC, abstractmethod


class JiraConnectionChecker(ABC):
    @abstractmethod
    async def is_configured(self) -> bool: ...

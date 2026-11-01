from abc import ABC, abstractmethod


class BreachedPasswordChecker(ABC):
    @abstractmethod
    async def is_breached(self, password: str) -> bool: ...

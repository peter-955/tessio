from abc import ABC, abstractmethod


class DependencyProbe(ABC):
    @abstractmethod
    async def is_reachable(self) -> bool: ...

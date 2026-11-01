from abc import ABC, abstractmethod

from app.modules.stories.domains.criteria_change.entity import CriteriaChange


class CriteriaChangedHandler(ABC):
    @abstractmethod
    async def handle(self, change: CriteriaChange) -> None: ...

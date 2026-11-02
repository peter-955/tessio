from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.stories.domains.acceptance_criterion.entity import AcceptanceCriterion


class AcceptanceCriterionRepository(ABC):
    @abstractmethod
    async def list_for_story(self, story_id: UUID) -> list[AcceptanceCriterion]: ...

    @abstractmethod
    async def save(self, criterion: AcceptanceCriterion) -> None: ...

    @abstractmethod
    async def delete_for_story(self, story_id: UUID) -> None: ...

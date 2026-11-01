from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion


class CriterionReader(ABC):
    @abstractmethod
    async def list_for_story(self, story_id: UUID) -> list[CaseCriterion]: ...

    @abstractmethod
    async def list_by_ids(self, criterion_ids: Collection[UUID]) -> list[CaseCriterion]: ...

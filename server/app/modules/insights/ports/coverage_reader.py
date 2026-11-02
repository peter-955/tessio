from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.runs import ResultStatus


class CoverageReader(ABC):
    @abstractmethod
    async def list_criteria(self, project_id: UUID, story_ids: Collection[UUID]) -> list[TracedCriterion]: ...

    @abstractmethod
    async def list_cases(
        self, project_id: UUID, story_ids: Collection[UUID] | None, is_including_deprecated: bool
    ) -> list[TracedCase]: ...

    @abstractmethod
    async def find_run_story_id(self, project_id: UUID, run_id: UUID) -> UUID | None: ...

    @abstractmethod
    async def list_run_case_story_keys(self, project_id: UUID, run_id: UUID) -> dict[UUID, str]: ...

    @abstractmethod
    async def list_run_outcomes(self, project_id: UUID, run_id: UUID) -> dict[UUID, ResultStatus | None]: ...

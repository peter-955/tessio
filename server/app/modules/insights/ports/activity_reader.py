from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.insights.domains.draft_case_list.entity import DraftCaseList
from app.modules.insights.domains.failure_to_fix_list.entity import FailureToFixList
from app.modules.insights.domains.gap_to_answer_list.entity import GapToAnswerList
from app.modules.insights.domains.run_reference.entity import RunReference
from app.shared.permissions import ProjectRole


class ActivityReader(ABC):
    @abstractmethod
    async def count_open_gaps(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, int]: ...

    @abstractmethod
    async def count_active_failures(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, int]: ...

    @abstractmethod
    async def find_last_runs(self, project_id: UUID, story_ids: Collection[UUID]) -> dict[UUID, RunReference]: ...

    @abstractmethod
    async def count_unassigned_failures(self, project_id: UUID) -> int: ...

    @abstractmethod
    async def list_failures_to_fix(self, project_id: UUID, user_id: UUID, limit: int) -> FailureToFixList: ...

    @abstractmethod
    async def list_gaps_to_answer(
        self, project_id: UUID, user_id: UUID, role: ProjectRole, limit: int
    ) -> GapToAnswerList: ...

    @abstractmethod
    async def list_draft_cases(self, project_id: UUID, user_id: UUID, limit: int) -> DraftCaseList: ...

from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.plans.domains.plan_case.entity import PlanCase
from app.modules.plans.domains.plan_failure_blocker.entity import PlanFailureBlocker
from app.modules.plans.domains.plan_gap_blocker.entity import PlanGapBlocker
from app.modules.plans.domains.plan_item_view.entity import PlanItemView
from app.modules.plans.domains.plan_latest_result.entity import PlanLatestResult
from app.modules.plans.domains.plan_progress_window.entity import PlanProgressWindow
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.typing.enums import PlanStatus


class PlanViewReader(ABC):
    @abstractmethod
    async def list_plans(self, project_id: UUID, status: PlanStatus | None) -> list[TestPlan]: ...

    @abstractmethod
    async def count_items(self, plan_ids: Collection[UUID]) -> dict[UUID, int]: ...

    @abstractmethod
    async def list_item_views(self, plan_id: UUID) -> list[PlanItemView]: ...

    @abstractmethod
    async def list_plan_cases(self, plan_id: UUID) -> list[PlanCase]: ...

    @abstractmethod
    async def list_plan_story_ids(self, plan_id: UUID) -> set[UUID]: ...

    @abstractmethod
    async def map_latest_results(
        self, test_case_ids: Collection[UUID], window: PlanProgressWindow
    ) -> dict[UUID, PlanLatestResult]: ...

    @abstractmethod
    async def list_failure_blockers(
        self, project_id: UUID, test_case_ids: Collection[UUID]
    ) -> list[PlanFailureBlocker]: ...

    @abstractmethod
    async def list_gap_blockers(self, project_id: UUID, story_ids: Collection[UUID]) -> list[PlanGapBlocker]: ...

    @abstractmethod
    async def map_environment_names(self, project_id: UUID, environment_ids: Collection[UUID]) -> dict[UUID, str]: ...

    @abstractmethod
    async def map_user_names(self, user_ids: Collection[UUID]) -> dict[UUID, str]: ...

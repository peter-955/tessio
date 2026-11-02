from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.suites.domains.suite_case_filter.entity import SuiteCaseFilter
from app.modules.suites.domains.suite_case_view.entity import SuiteCaseView
from app.modules.suites.domains.suite_run_reference.entity import SuiteRunReference
from app.modules.suites.domains.suite_summary.entity import SuiteSummary


class SuiteViewReader(ABC):
    @abstractmethod
    async def list_summaries(self, project_id: UUID, is_including_archived: bool) -> list[SuiteSummary]: ...

    @abstractmethod
    async def list_case_views(self, suite_id: UUID) -> list[SuiteCaseView]: ...

    @abstractmethod
    async def find_last_run(self, suite_id: UUID) -> SuiteRunReference | None: ...

    @abstractmethod
    async def find_running_run(self, suite_id: UUID) -> SuiteRunReference | None: ...

    @abstractmethod
    async def list_project_case_ids(self, project_id: UUID, test_case_ids: Collection[UUID]) -> set[UUID]: ...

    @abstractmethod
    async def list_matching_case_ids(self, project_id: UUID, case_filter: SuiteCaseFilter) -> list[UUID]: ...

    @abstractmethod
    async def find_story_id(self, project_id: UUID, story_key: str) -> UUID | None: ...

    @abstractmethod
    async def has_sprint(self, project_id: UUID, sprint_id: UUID) -> bool: ...

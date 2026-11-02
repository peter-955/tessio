from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure_filter.entity import FailureFilter
from app.modules.failures.domains.failure_view.entity import FailureView


class FailureRepository(ABC):
    @abstractmethod
    async def lock_test_case(self, test_case_id: UUID) -> None: ...

    @abstractmethod
    async def find_for_update(self, project_id: UUID, failure_id: UUID) -> Failure | None: ...

    @abstractmethod
    async def find_active_for_update(self, test_case_id: UUID) -> Failure | None: ...

    @abstractmethod
    async def add(self, failure: Failure) -> None: ...

    @abstractmethod
    async def save(self, failure: Failure) -> None: ...

    @abstractmethod
    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int: ...

    @abstractmethod
    async def find_view(self, project_id: UUID, failure_id: UUID) -> FailureView | None: ...

    @abstractmethod
    async def list_views(self, project_id: UUID, failure_filter: FailureFilter, limit: int) -> list[FailureView]: ...

    @abstractmethod
    async def list_active_with_jira_issue(self, project_id: UUID) -> list[Failure]: ...

import asyncio
from uuid import UUID

from app.modules.failures import FailureRepository
from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.failure_filter.entity import FailureFilter
from app.modules.failures.domains.failure_view.entity import FailureView

LOOKUP_DELAY_SECONDS = 0.3


class SlowFailureRepository(FailureRepository):
    def __init__(self, failure_repository: FailureRepository) -> None:
        self._failure_repository = failure_repository

    async def lock_test_case(self, test_case_id: UUID) -> None:
        await self._failure_repository.lock_test_case(test_case_id)

    async def find_for_update(self, project_id: UUID, failure_id: UUID) -> Failure | None:
        return await self._failure_repository.find_for_update(project_id, failure_id)

    async def find_active_for_update(self, test_case_id: UUID) -> Failure | None:
        failure = await self._failure_repository.find_active_for_update(test_case_id)
        await asyncio.sleep(LOOKUP_DELAY_SECONDS)
        return failure

    async def add(self, failure: Failure) -> None:
        await self._failure_repository.add(failure)

    async def save(self, failure: Failure) -> None:
        await self._failure_repository.save(failure)

    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int:
        return await self._failure_repository.count_active_for_story(project_id, story_id)

    async def find_view(self, project_id: UUID, failure_id: UUID) -> FailureView | None:
        return await self._failure_repository.find_view(project_id, failure_id)

    async def list_views(self, project_id: UUID, failure_filter: FailureFilter, limit: int) -> list[FailureView]:
        return await self._failure_repository.list_views(project_id, failure_filter, limit)

    async def list_active_with_jira_issue(self, project_id: UUID) -> list[Failure]:
        return await self._failure_repository.list_active_with_jira_issue(project_id)

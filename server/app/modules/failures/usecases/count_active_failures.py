from uuid import UUID

from app.modules.failures.domains.failure.repository import FailureRepository
from app.modules.stories import ActiveFailureCounter
from app.shared.common import Transaction


class CountActiveFailuresUseCase(ActiveFailureCounter):
    def __init__(self, transaction: Transaction, failure_repository: FailureRepository) -> None:
        self._transaction = transaction
        self._failure_repository = failure_repository

    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int:
        async with self._transaction.begin():
            count = await self._failure_repository.count_active_for_story(project_id, story_id)
        return count

from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.errors import OpenGapsBlockRunError
from app.shared.common import Transaction


class OpenGapChecker:
    def __init__(self, transaction: Transaction, gap_repository: GapRepository) -> None:
        self._transaction = transaction
        self._gap_repository = gap_repository

    async def count_open_gaps(self, story_id: UUID) -> int:
        async with self._transaction.begin():
            count = await self._gap_repository.count_open(story_id)
        return count

    async def ensure_no_open_gaps(self, story_id: UUID) -> None:
        count = await self.count_open_gaps(story_id)
        if count > 0:
            raise OpenGapsBlockRunError(count)

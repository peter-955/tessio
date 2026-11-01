from datetime import UTC, datetime

from app.modules.stories import CriteriaChange, CriteriaChangedHandler
from app.modules.test_cases.domains.test_case.repository import TestCaseRepository
from app.shared.common import Transaction


class FlagCasesForReviewUseCase(CriteriaChangedHandler):
    def __init__(self, transaction: Transaction, test_case_repository: TestCaseRepository) -> None:
        self._transaction = transaction
        self._test_case_repository = test_case_repository

    async def handle(self, change: CriteriaChange) -> None:
        criterion_ids = change.changed_criterion_ids | change.removed_criterion_ids
        if not criterion_ids:
            return
        now = datetime.now(UTC)
        async with self._transaction.begin():
            linked_cases = await self._test_case_repository.list_linked_to_criteria_for_update(
                change.project_id, criterion_ids
            )
            for linked_case in linked_cases:
                test_case = linked_case.test_case
                if test_case.is_deprecated:
                    continue
                await self._test_case_repository.save(
                    test_case.model_copy(
                        update={
                            "needs_review_at": now,
                            "needs_review_criterion_ids": sorted(
                                {*test_case.needs_review_criterion_ids, *linked_case.linked_criterion_ids}
                            ),
                        }
                    )
                )

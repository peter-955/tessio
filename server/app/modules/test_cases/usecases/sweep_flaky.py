from app.modules.test_cases.domains.test_case_quality.repository import TestCaseQualityRepository
from app.modules.test_cases.usecases.recompute_flaky import RecomputeFlakyUseCase
from app.shared.common import Transaction


class SweepFlakyUseCase:
    def __init__(
        self,
        transaction: Transaction,
        test_case_quality_repository: TestCaseQualityRepository,
        recompute_flaky: RecomputeFlakyUseCase,
    ) -> None:
        self._transaction = transaction
        self._test_case_quality_repository = test_case_quality_repository
        self._recompute_flaky = recompute_flaky

    async def execute(self) -> int:
        async with self._transaction.begin():
            test_case_ids = await self._test_case_quality_repository.list_case_ids()
        for test_case_id in test_case_ids:
            await self._recompute_flaky.execute(test_case_id)
        return len(test_case_ids)

from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.test_cases.domains.quarantine_event.entity import QuarantineEvent
from app.modules.test_cases.domains.quarantine_event.repository import QuarantineEventRepository
from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_quality.repository import TestCaseQualityRepository
from app.modules.test_cases.ports.case_result_history_reader import CaseResultHistoryReader
from app.modules.test_cases.typing.constants.flaky_case import FLAKY_RESULT_WINDOW, QUARANTINE_RELEASE_PASS_COUNT
from app.modules.test_cases.typing.enums import QuarantineEventKind
from app.modules.test_cases.utils.flaky_case import (
    count_result_flips,
    find_disagreed_at,
    is_quarantine_over,
    select_flaky_since,
)
from app.modules.test_cases.utils.test_case_event import build_test_case_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher


class RecomputeFlakyUseCase:
    def __init__(
        self,
        transaction: Transaction,
        test_case_quality_repository: TestCaseQualityRepository,
        case_result_history_reader: CaseResultHistoryReader,
        quarantine_event_repository: QuarantineEventRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._test_case_quality_repository = test_case_quality_repository
        self._case_result_history_reader = case_result_history_reader
        self._quarantine_event_repository = quarantine_event_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, test_case_id: UUID) -> None:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            test_case = await self._test_case_quality_repository.find_by_id_for_update(test_case_id)
            if test_case is None:
                return
            recomputed = await self._recompute(test_case, now)
            is_changing = recomputed != test_case
            if is_changing:
                await self._test_case_quality_repository.save(recomputed)
            if test_case.is_quarantined and not recomputed.is_quarantined:
                await self._quarantine_event_repository.add(
                    QuarantineEvent(
                        id=uuid7(),
                        test_case_id=test_case.id,
                        kind=QuarantineEventKind.AUTO_RELEASED,
                        actor_id=None,
                        reason=None,
                        created_at=now,
                    )
                )
        if is_changing:
            await self._live_event_publisher.publish(build_test_case_changed_event(recomputed))

    async def _recompute(self, test_case: TestCase, now: datetime) -> TestCase:
        version_results = await self._case_result_history_reader.list_version_results(
            test_case.id, test_case.current_version_id, FLAKY_RESULT_WINDOW
        )
        flaky_score = count_result_flips(version_results)
        latest_results = await self._case_result_history_reader.find_latest_per_executor_kind(
            test_case.id, test_case.current_version_id
        )
        updates: dict[str, object] = {
            "flaky_score": flaky_score,
            "flaky_since": select_flaky_since(flaky_score, test_case.flaky_since, now),
            "disagreed_at": find_disagreed_at(latest_results),
        }
        if test_case.quarantined_at is not None:
            results_since = await self._case_result_history_reader.list_results_since(
                test_case.id, test_case.quarantined_at, QUARANTINE_RELEASE_PASS_COUNT
            )
            if is_quarantine_over(results_since):
                updates |= {"quarantined_at": None, "quarantined_by": None, "quarantine_reason": None}
        return test_case.model_copy(update=updates)

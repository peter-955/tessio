from datetime import datetime
from uuid import UUID

from app.modules.notifications import SendNotificationUseCase
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_target.entity import RunTarget
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.runs.typing.constants.stale_run import STALE_RUN_BATCH_SIZE, STALE_RUN_INACTIVITY
from app.modules.runs.typing.enums import RunAbortReason, RunStatus
from app.modules.runs.usecases.screenshot_verifier import ScreenshotVerifier
from app.modules.runs.utils.run_event import build_run_finished_event
from app.modules.runs.utils.run_finished_payload import build_run_finished_payload
from app.modules.runs.utils.run_report import build_run_report
from app.modules.runs.utils.run_target import find_run_target
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import ProjectRole


class AbortStaleRunsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        screenshot_verifier: ScreenshotVerifier,
        criterion_impact_calculator: CriterionImpactCalculator,
        run_story_reader: RunStoryReader,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._screenshot_verifier = screenshot_verifier
        self._criterion_impact_calculator = criterion_impact_calculator
        self._run_story_reader = run_story_reader
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, now: datetime) -> int:
        cutoff = now - STALE_RUN_INACTIVITY
        aborted_count = 0
        while True:
            async with self._transaction.begin():
                stale_run_ids = await self._run_repository.list_stale_run_ids(cutoff, STALE_RUN_BATCH_SIZE)
            batch_aborted_count = 0
            for run_id in stale_run_ids:
                if await self._abort(run_id, cutoff, now):
                    batch_aborted_count += 1
            aborted_count += batch_aborted_count
            if len(stale_run_ids) < STALE_RUN_BATCH_SIZE or batch_aborted_count == 0:
                return aborted_count

    async def _abort(self, run_id: UUID, cutoff: datetime, now: datetime) -> bool:
        async with self._transaction.begin():
            run = await self._run_repository.find_stale_for_update(run_id, cutoff)
            if run is None:
                return False
            run_cases = await self._run_case_repository.list_views(run.id)
            missing_screenshots = await self._screenshot_verifier.verify(run.project_id, run.id, run_cases)
            report = build_run_report(
                run_cases,
                await self._case_result_repository.list_for_run(run.id),
                await self._case_result_repository.list_steps_for_run(run.id),
                await self._criterion_impact_calculator.calculate(run.project_id, run.id),
                missing_screenshots,
                None,
                now,
                run.skipped_cases,
            )
            aborted_run = run.model_copy(
                update={
                    "status": RunStatus.ABORTED,
                    "abort_reason": RunAbortReason.INACTIVE,
                    "summary": None,
                    "report": report,
                    "finished_at": now,
                }
            )
            await self._run_repository.save(aborted_run)
            target = await find_run_target(run, self._run_story_reader)
        await self._announce_finish(aborted_run, report, target)
        return True

    async def _announce_finish(self, run: Run, report: RunReport, target: RunTarget) -> None:
        await self._live_event_publisher.publish(build_run_finished_event(run))
        payload = build_run_finished_payload(run, report, target)
        if payload is None:
            return
        await self._send_notification.execute(
            run.project_id,
            payload,
            actor_id=None,
            recipient_ids={run.started_by},
            recipient_roles={ProjectRole.QC},
        )

from datetime import datetime
from uuid import UUID

from app.modules.notifications import RunFinishedPayload, RunOutcome, SendNotificationUseCase
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.runs.typing.constants.stale_run import STALE_RUN_BATCH_SIZE, STALE_RUN_INACTIVITY
from app.modules.runs.typing.enums import RunAbortReason, RunStatus
from app.modules.runs.usecases.screenshot_verifier import ScreenshotVerifier
from app.modules.runs.utils.run_report import build_run_report
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
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
            story_jira_key = await self._run_story_reader.find_jira_key(run.story_id)
        await self._announce_finish(aborted_run, report, story_jira_key)
        return True

    async def _announce_finish(self, run: Run, report: RunReport, story_jira_key: str) -> None:
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.RUN_FINISHED,
                project_id=run.project_id,
                ids={"runId": str(run.id), "storyId": str(run.story_id), "status": run.status.value},
            )
        )
        await self._send_notification.execute(
            run.project_id,
            RunFinishedPayload(
                run_id=run.id,
                story_id=run.story_id,
                story_jira_key=story_jira_key,
                outcome=RunOutcome(run.status.value),
                passed_count=report.counts.passed,
                failed_count=report.counts.failed,
                blocked_count=report.counts.blocked,
            ),
            actor_id=None,
            recipient_ids={run.started_by},
            recipient_roles={ProjectRole.QC},
        )

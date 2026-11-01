from datetime import UTC, datetime
from uuid import UUID

from app.modules.notifications import RunFinishedPayload, RunOutcome, SendNotificationUseCase
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.finished_run.entity import FinishedRun
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.errors import RunNotFoundError, RunNotOwnedError, RunNotRunningError
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.usecases.screenshot_verifier import ScreenshotVerifier
from app.modules.runs.utils.run_event import build_run_finished_event
from app.modules.runs.utils.run_report import build_run_report
from app.modules.runs.utils.run_status import resolve_finished_status
from app.modules.stories import StoryNotFoundError
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.masking import SecretMasker
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccessResolver,
    ProjectNotFoundError,
    ProjectRole,
    has_capability,
    require,
)


class FinishRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_target_reader: RunTargetReader,
        screenshot_verifier: ScreenshotVerifier,
        criterion_impact_calculator: CriterionImpactCalculator,
        secret_value_reader: SecretValueReader,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_target_reader = run_target_reader
        self._screenshot_verifier = screenshot_verifier
        self._criterion_impact_calculator = criterion_impact_calculator
        self._secret_value_reader = secret_value_reader
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, run_id: UUID, summary: str | None) -> FinishedRun:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_START)
            run = await self._run_repository.find_by_id_for_update(access.project_id, run_id)
            if run is None:
                raise RunNotFoundError
            if run.started_by != actor.user_id and not has_capability(access, Capability.RUN_FINISH_ANY):
                raise RunNotOwnedError
            if not run.is_running:
                raise RunNotRunningError
            story = await self._run_target_reader.find_story_by_id(run.project_id, run.story_id)
            if story is None:
                raise StoryNotFoundError
            run_cases = await self._run_case_repository.list_views(run.id)
            missing_screenshots = await self._screenshot_verifier.verify(run.project_id, run.id, run_cases)
            case_results = await self._case_result_repository.list_for_run(run.id)
            step_results = await self._case_result_repository.list_steps_for_run(run.id)
            status, abort_reason = resolve_finished_status(case_results)
            criterion_impacts = await self._criterion_impact_calculator.calculate(run.project_id, run.id)
            masker = SecretMasker(
                await self._secret_value_reader.list_secret_values(run.project_id, run.environment_id)
            )
            masked_summary = masker.mask_optional(summary)
            report = build_run_report(
                run_cases, case_results, step_results, criterion_impacts, missing_screenshots, masked_summary, now
            )
            finished_run = run.model_copy(
                update={
                    "status": status,
                    "abort_reason": abort_reason,
                    "summary": masked_summary,
                    "report": report,
                    "finished_at": now,
                    "last_activity_at": now,
                }
            )
            await self._run_repository.save(finished_run)
        await self._announce(finished_run, story.jira_key)
        return FinishedRun(run=finished_run, missing_screenshots=missing_screenshots)

    async def _announce(self, run: Run, story_jira_key: str) -> None:
        await self._live_event_publisher.publish(build_run_finished_event(run))
        if run.report is None:
            return
        await self._send_notification.execute(
            run.project_id,
            RunFinishedPayload(
                run_id=run.id,
                story_id=run.story_id,
                story_jira_key=story_jira_key,
                outcome=RunOutcome(run.status.value),
                passed_count=run.report.counts.passed,
                failed_count=run.report.counts.failed,
                blocked_count=run.report.counts.blocked,
            ),
            actor_id=run.started_by,
            recipient_ids={run.started_by},
            recipient_roles={ProjectRole.QC},
        )

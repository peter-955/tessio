from datetime import UTC, datetime
from uuid import UUID

from app.modules.jira import JiraResultCommentRequester
from app.modules.notifications import SendNotificationUseCase
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_target.entity import RunTarget
from app.modules.runs.errors import RunNotFoundError, RunNotManualError, RunNotOwnedError, RunNotRunningError
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.runs.typing.enums import RunAbortReason, RunExecutor, RunStatus
from app.modules.runs.usecases.screenshot_verifier import ScreenshotVerifier
from app.modules.runs.utils.run_event import build_run_finished_event
from app.modules.runs.utils.run_finished_payload import build_run_finished_payload
from app.modules.runs.utils.run_report import build_run_report
from app.modules.runs.utils.run_status import decide_run_status
from app.modules.runs.utils.run_story_ids import list_jira_comment_story_ids
from app.modules.runs.utils.run_target import find_run_target
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.masking import SecretMasker
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccess,
    ProjectAccessResolver,
    ProjectRole,
    has_capability,
    require,
)


class FinishManualRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        screenshot_verifier: ScreenshotVerifier,
        criterion_impact_calculator: CriterionImpactCalculator,
        secret_value_reader: SecretValueReader,
        run_story_reader: RunStoryReader,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
        jira_result_comment_requester: JiraResultCommentRequester,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._screenshot_verifier = screenshot_verifier
        self._criterion_impact_calculator = criterion_impact_calculator
        self._secret_value_reader = secret_value_reader
        self._run_story_reader = run_story_reader
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher
        self._jira_result_comment_requester = jira_result_comment_requester

    async def execute(self, actor: Actor, project_key: str, run_id: UUID, summary: str | None) -> Run:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_RECORD_MANUAL)
            run = await self._lock_manual_run(access, actor, run_id)
            masker = SecretMasker(
                await self._secret_value_reader.list_secret_values(run.project_id, run.environment_id)
            )
            masked_summary = masker.mask_optional(summary)
            run_cases = await self._run_case_repository.list_views(run.id)
            missing_screenshots = await self._screenshot_verifier.verify(run.project_id, run.id, run_cases)
            case_results = await self._case_result_repository.list_for_run(run.id)
            status = decide_run_status([case_result.status for case_result in case_results])
            report = build_run_report(
                run_cases,
                case_results,
                await self._case_result_repository.list_steps_for_run(run.id),
                await self._criterion_impact_calculator.calculate(run.project_id, run.id),
                missing_screenshots,
                masked_summary,
                now,
                run.skipped_cases,
            )
            finished_run = run.model_copy(
                update={
                    "status": status,
                    "abort_reason": RunAbortReason.NO_RESULTS if status is RunStatus.ABORTED else None,
                    "summary": masked_summary,
                    "report": report,
                    "finished_at": now,
                    "last_activity_at": now,
                }
            )
            await self._run_repository.save(finished_run)
            target = await find_run_target(run, self._run_story_reader)
        await self._announce_finish(finished_run, report, target, actor.user_id)
        return finished_run

    async def _lock_manual_run(self, access: ProjectAccess, actor: Actor, run_id: UUID) -> Run:
        run = await self._run_repository.find_by_id_for_update(access.project_id, run_id)
        if run is None:
            raise RunNotFoundError
        if run.executor is not RunExecutor.MANUAL:
            raise RunNotManualError
        if not run.is_running:
            raise RunNotRunningError
        if run.started_by != actor.user_id and not has_capability(access, Capability.RUN_FINISH_ANY):
            raise RunNotOwnedError
        return run

    async def _announce_finish(self, run: Run, report: RunReport, target: RunTarget, actor_id: UUID | None) -> None:
        await self._live_event_publisher.publish(build_run_finished_event(run))
        await self._jira_result_comment_requester.request_after_run(
            run.project_id, run.id, list_jira_comment_story_ids(run, report)
        )
        payload = build_run_finished_payload(run, report, target)
        if payload is None:
            return
        await self._send_notification.execute(
            run.project_id,
            payload,
            actor_id=actor_id,
            recipient_ids={run.started_by},
            recipient_roles={ProjectRole.QC},
        )

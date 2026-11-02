from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.files import (
    StoredFile,
    StoredFileKind,
    StoredFileRepository,
    StoredFileStatus,
    build_screenshot_key_prefix,
)
from app.modules.runs.domains.case_report.entity import CaseReport
from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.step_report.entity import StepReport
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.errors import (
    CaseResultExistsError,
    InvalidStepOrderError,
    IterationOutOfRangeError,
    RunNotFoundError,
    RunNotOwnedError,
    RunNotRunningError,
    UnknownCaseError,
)
from app.modules.runs.ports.case_result_recorded_handler import CaseResultRecordedHandler
from app.modules.runs.ports.flaky_recompute_requester import FlakyRecomputeRequester
from app.modules.runs.typing.constants.screenshot import PENDING_SCREENSHOT_CONTENT_TYPE, PENDING_SCREENSHOT_SUFFIX
from app.modules.runs.typing.enums import ResultStatus
from app.modules.runs.utils.case_story import resolve_case_story_id
from app.modules.runs.utils.run_event import build_run_case_recorded_event
from app.modules.runs.utils.step_diagnosis import build_step_diagnosis, select_suspected_cause
from app.modules.runs.utils.worst_iteration import is_new_case_outcome
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class RecordCaseResultUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        stored_file_repository: StoredFileRepository,
        secret_value_reader: SecretValueReader,
        case_result_recorded_handler: CaseResultRecordedHandler,
        flaky_recompute_requester: FlakyRecomputeRequester,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._stored_file_repository = stored_file_repository
        self._secret_value_reader = secret_value_reader
        self._case_result_recorded_handler = case_result_recorded_handler
        self._flaky_recompute_requester = flaky_recompute_requester
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, report: CaseReport) -> UUID:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_START)
            run = await self._run_repository.find_by_id_for_update(access.project_id, report.run_id)
            if run is None:
                raise RunNotFoundError
            if run.started_by != actor.user_id:
                raise RunNotOwnedError
            if not run.is_running:
                raise RunNotRunningError
            run_case = await self._find_run_case(run, report.case_id)
            if report.iteration >= run_case.version.iteration_count:
                raise IterationOutOfRangeError(report.iteration, run_case.version.iteration_count)
            earlier_results = await self._case_result_repository.list_for_case(run.id, run_case.test_case_id)
            if any(earlier.iteration == report.iteration for earlier in earlier_results):
                raise CaseResultExistsError
            self._check_step_orders(run_case, report.steps)
            masker = SecretMasker(
                await self._secret_value_reader.list_secret_values(run.project_id, run.environment_id)
            )
            suspected_cause, cause_reason = select_suspected_cause(
                report.status, report.suspected_cause, report.cause_reason, masker
            )
            case_result = CaseResult(
                id=uuid7(),
                run_id=run.id,
                test_case_id=run_case.test_case_id,
                test_case_version_id=run_case.version.id,
                status=report.status,
                duration_ms=report.duration_ms,
                suspected_cause=suspected_cause,
                cause_reason=cause_reason,
                recorded_by=actor.user_id,
                created_at=now,
                iteration=report.iteration,
            )
            step_results = await self._build_step_results(run, case_result, run_case, report.steps, masker, now)
            await self._case_result_repository.add(case_result, step_results)
            await self._run_repository.save(run.model_copy(update={"last_activity_at": now}))
            case_story_id = resolve_case_story_id(run, run_case)
            failure_events: list[LiveEvent] = []
            if is_new_case_outcome(case_result, earlier_results):
                failure_events = await self._case_result_recorded_handler.handle(
                    RecordedCaseResult(
                        project_id=run.project_id,
                        story_id=case_story_id,
                        run_id=run.id,
                        case_result_id=case_result.id,
                        test_case_id=case_result.test_case_id,
                        status=case_result.status,
                        suspected_cause=case_result.suspected_cause,
                        cause_reason=case_result.cause_reason,
                        recorded_by=actor.user_id,
                        recorded_at=now,
                    )
                )
        await self._live_event_publisher.publish(build_run_case_recorded_event(run, case_result, case_story_id))
        for failure_event in failure_events:
            await self._live_event_publisher.publish(failure_event)
        await self._flaky_recompute_requester.request(case_result.test_case_id)
        return case_result.id

    async def _find_run_case(self, run: Run, test_case_id: UUID) -> RunCaseView:
        for run_case in await self._run_case_repository.list_views(run.id):
            if run_case.test_case_id == test_case_id:
                return run_case
        raise UnknownCaseError

    @staticmethod
    def _check_step_orders(run_case: RunCaseView, step_reports: list[StepReport]) -> None:
        version_orders = {step.order for step in run_case.version.steps}
        reported_orders: set[int] = set()
        for step_report in step_reports:
            if step_report.order in reported_orders or step_report.order not in version_orders:
                raise InvalidStepOrderError(step_report.order, run_case.code)
            reported_orders.add(step_report.order)

    async def _build_step_results(
        self,
        run: Run,
        case_result: CaseResult,
        run_case: RunCaseView,
        step_reports: list[StepReport],
        masker: SecretMasker,
        now: datetime,
    ) -> list[StepResult]:
        reports_by_order = {step_report.order: step_report for step_report in step_reports}
        screenshot_key_prefix = build_screenshot_key_prefix(run.project_id, case_result.id)
        step_results: list[StepResult] = []
        for step in sorted(run_case.version.steps, key=lambda version_step: version_step.order):
            step_report = reports_by_order.get(step.order)
            screenshot_file_id = (
                None
                if step_report is None or not step_report.screenshot_path
                else await self._add_pending_screenshot(run, screenshot_key_prefix, step.order, now)
            )
            step_results.append(
                StepResult(
                    id=uuid7(),
                    case_result_id=case_result.id,
                    step_order=step.order,
                    status=ResultStatus.SKIPPED if step_report is None else step_report.status,
                    actual_result=None if step_report is None else masker.mask(step_report.actual_result),
                    error=None if step_report is None else masker.mask_optional(step_report.error),
                    screenshot_file_id=screenshot_file_id,
                    evidence_file_id=None,
                    diagnosis=None if step_report is None else build_step_diagnosis(step_report, masker),
                    created_at=now,
                )
            )
        return step_results

    async def _add_pending_screenshot(self, run: Run, key_prefix: str, step_order: int, now: datetime) -> UUID:
        stored_file = StoredFile(
            id=uuid7(),
            project_id=run.project_id,
            kind=StoredFileKind.SCREENSHOT,
            object_key=f"{key_prefix}{step_order}",
            file_name=f"{step_order}{PENDING_SCREENSHOT_SUFFIX}",
            content_type=PENDING_SCREENSHOT_CONTENT_TYPE,
            size=None,
            sha256=None,
            status=StoredFileStatus.PENDING,
            uploaded_by=run.started_by,
            created_at=now,
        )
        await self._stored_file_repository.save(stored_file)
        return stored_file.id

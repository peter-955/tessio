from collections.abc import Collection
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.files import StoredFileKind, StoredFileRepository
from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.manual_case_report.entity import ManualCaseReport
from app.modules.runs.domains.manual_step_report.entity import ManualStepReport
from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult
from app.modules.runs.domains.recorded_manual_case_result.entity import RecordedManualCaseResult
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.entity import RunCase
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.errors import (
    CaseResultExistsError,
    EvidenceFileNotFoundError,
    EvidenceNotUploadedError,
    InvalidStepReportError,
    RunCaseNotFoundError,
    RunNotFoundError,
    RunNotManualError,
    RunNotOwnedError,
    RunNotRunningError,
)
from app.modules.runs.ports.case_result_recorded_handler import CaseResultRecordedHandler
from app.modules.runs.typing.enums import ResultStatus, RunExecutor
from app.modules.test_cases import TestCaseVersion, TestCaseVersionRepository
from app.modules.test_data import SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor, Capability, ProjectAccess, ProjectAccessResolver, has_capability, require


class RecordManualCaseResultUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        test_case_version_repository: TestCaseVersionRepository,
        stored_file_repository: StoredFileRepository,
        secret_value_reader: SecretValueReader,
        case_result_recorded_handler: CaseResultRecordedHandler,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._test_case_version_repository = test_case_version_repository
        self._stored_file_repository = stored_file_repository
        self._secret_value_reader = secret_value_reader
        self._case_result_recorded_handler = case_result_recorded_handler
        self._live_event_publisher = live_event_publisher

    async def execute(
        self, actor: Actor, project_key: str, run_id: UUID, test_case_id: UUID, report: ManualCaseReport
    ) -> RecordedManualCaseResult:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_RECORD_MANUAL)
            run = await self._lock_manual_run(access, actor, run_id)
            run_case = await self._find_run_case(run.id, test_case_id)
            if await self._case_result_repository.find_for_case(run.id, test_case_id) is not None:
                raise CaseResultExistsError
            version = await self._test_case_version_repository.find_by_id(run_case.test_case_version_id)
            if version is None:
                raise RunCaseNotFoundError
            self._ensure_valid_step_orders(version, report.steps)
            await self._ensure_evidence_files(run, actor, report.steps)
            masker = SecretMasker(
                await self._secret_value_reader.list_secret_values(run.project_id, run.environment_id)
            )
            case_result_id = uuid7()
            step_results = self._build_step_results(case_result_id, version, report.steps, masker, now)
            suggested_status = self._suggest_status([step_result.status for step_result in step_results])
            case_result = CaseResult(
                id=case_result_id,
                run_id=run.id,
                test_case_id=test_case_id,
                test_case_version_id=run_case.test_case_version_id,
                status=report.status or suggested_status,
                duration_ms=report.duration_ms,
                recorded_by=actor.user_id,
                created_at=now,
            )
            await self._case_result_repository.add(case_result, step_results)
            await self._run_repository.save(run.model_copy(update={"last_activity_at": now}))
            await self._case_result_recorded_handler.handle(
                RecordedCaseResult(
                    project_id=run.project_id,
                    story_id=run.story_id,
                    run_id=run.id,
                    case_result_id=case_result.id,
                    test_case_id=test_case_id,
                    status=case_result.status,
                    recorded_by=actor.user_id,
                    recorded_at=now,
                )
            )
        await self._live_event_publisher.publish(
            LiveEvent(
                type=LiveEventType.RUN_CASE_RECORDED,
                project_id=run.project_id,
                ids={
                    "runId": str(run.id),
                    "storyId": str(run.story_id),
                    "caseResultId": str(case_result.id),
                    "testCaseId": str(test_case_id),
                    "status": case_result.status.value,
                },
            )
        )
        return RecordedManualCaseResult(
            case_result=case_result, step_results=step_results, suggested_status=suggested_status
        )

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

    async def _find_run_case(self, run_id: UUID, test_case_id: UUID) -> RunCase:
        run_cases = await self._run_case_repository.list_for_run(run_id)
        run_case = next((run_case for run_case in run_cases if run_case.test_case_id == test_case_id), None)
        if run_case is None:
            raise RunCaseNotFoundError
        return run_case

    @staticmethod
    def _ensure_valid_step_orders(version: TestCaseVersion, step_reports: list[ManualStepReport]) -> None:
        reported_orders = [step_report.order for step_report in step_reports]
        version_orders = {step.order for step in version.steps}
        if len(set(reported_orders)) != len(reported_orders) or not set(reported_orders) <= version_orders:
            raise InvalidStepReportError

    async def _ensure_evidence_files(self, run: Run, actor: Actor, step_reports: list[ManualStepReport]) -> None:
        for step_report in step_reports:
            if step_report.evidence_file_id is None:
                continue
            stored_file = await self._stored_file_repository.find_by_id(step_report.evidence_file_id)
            if (
                stored_file is None
                or stored_file.project_id != run.project_id
                or stored_file.kind is not StoredFileKind.EVIDENCE
                or stored_file.uploaded_by != actor.user_id
            ):
                raise EvidenceFileNotFoundError
            if stored_file.is_pending:
                raise EvidenceNotUploadedError
            if not stored_file.is_uploaded:
                raise EvidenceFileNotFoundError

    @staticmethod
    def _build_step_results(
        case_result_id: UUID,
        version: TestCaseVersion,
        step_reports: list[ManualStepReport],
        masker: SecretMasker,
        now: datetime,
    ) -> list[StepResult]:
        reports_by_order = {step_report.order: step_report for step_report in step_reports}
        step_results: list[StepResult] = []
        for step in sorted(version.steps, key=lambda version_step: version_step.order):
            step_report = reports_by_order.get(step.order)
            step_results.append(
                StepResult(
                    id=uuid7(),
                    case_result_id=case_result_id,
                    step_order=step.order,
                    status=ResultStatus.SKIPPED if step_report is None else step_report.status,
                    actual_result="" if step_report is None else masker.mask(step_report.actual_result),
                    error=None if step_report is None else masker.mask_optional(step_report.error),
                    screenshot_file_id=None,
                    evidence_file_id=None if step_report is None else step_report.evidence_file_id,
                    created_at=now,
                )
            )
        return step_results

    @staticmethod
    def _suggest_status(step_statuses: Collection[ResultStatus]) -> ResultStatus:
        for status in (ResultStatus.FAILED, ResultStatus.BLOCKED, ResultStatus.PASSED):
            if status in step_statuses:
                return status
        return ResultStatus.SKIPPED

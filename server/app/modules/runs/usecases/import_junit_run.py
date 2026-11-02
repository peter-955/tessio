from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.jira import JiraResultCommentRequester
from app.modules.notifications import SendNotificationUseCase
from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.imported_case_outcome.entity import ImportedCaseOutcome
from app.modules.runs.domains.junit_import.entity import JunitImport
from app.modules.runs.domains.recorded_case_result.entity import RecordedCaseResult
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_suite.entity import RunSuite
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.domains.unmapped_test.entity import UnmappedTest
from app.modules.runs.errors import (
    JunitNoMappedTestsError,
    SuiteArchivedError,
    SuiteNotFoundError,
    UnknownImportEnvironmentError,
    UnknownImportSuiteError,
)
from app.modules.runs.ports.case_result_recorded_handler import CaseResultRecordedHandler
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator
from app.modules.runs.ports.flaky_recompute_requester import FlakyRecomputeRequester
from app.modules.runs.ports.import_case_reader import ImportCaseReader
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.typing.constants.junit import MAX_LISTED_UNMAPPED_TESTS
from app.modules.runs.typing.enums import ResultStatus, RunExecutor
from app.modules.runs.usecases.run_start_gate import RunStartGate
from app.modules.runs.utils.junit_mapping import map_junit_tests
from app.modules.runs.utils.junit_parser import parse_junit
from app.modules.runs.utils.run_event import (
    build_run_case_recorded_event,
    build_run_finished_event,
    build_run_started_event,
)
from app.modules.runs.utils.run_finished_payload import build_run_finished_payload
from app.modules.runs.utils.run_report import build_run_report
from app.modules.runs.utils.run_status import decide_run_status
from app.modules.runs.utils.run_story_ids import list_jira_comment_story_ids
from app.modules.runs.utils.run_target import find_run_target
from app.modules.test_cases import TestCaseVersion
from app.modules.test_data import Environment, SecretValueReader
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher
from app.shared.masking import SecretMasker
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectRole, require


class ImportJunitRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_target_reader: RunTargetReader,
        run_start_gate: RunStartGate,
        import_case_reader: ImportCaseReader,
        criterion_impact_calculator: CriterionImpactCalculator,
        secret_value_reader: SecretValueReader,
        run_story_reader: RunStoryReader,
        case_result_recorded_handler: CaseResultRecordedHandler,
        flaky_recompute_requester: FlakyRecomputeRequester,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
        jira_result_comment_requester: JiraResultCommentRequester,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_target_reader = run_target_reader
        self._run_start_gate = run_start_gate
        self._import_case_reader = import_case_reader
        self._criterion_impact_calculator = criterion_impact_calculator
        self._secret_value_reader = secret_value_reader
        self._run_story_reader = run_story_reader
        self._case_result_recorded_handler = case_result_recorded_handler
        self._flaky_recompute_requester = flaky_recompute_requester
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher
        self._jira_result_comment_requester = jira_result_comment_requester

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        content: bytes,
        environment_reference: str,
        suite_reference: str | None,
    ) -> JunitImport:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_START)
            tests = parse_junit(content)
            environment = await self._find_environment(access.project_id, environment_reference)
            suite = None if suite_reference is None else await self._find_suite(access.project_id, suite_reference)
            case_numbers = {number for test in tests for number in test.case_numbers}
            cases = await self._import_case_reader.list_by_numbers(access.project_id, case_numbers)
            outcomes, unmapped_tests = map_junit_tests(tests, {case.number: case for case in cases})
            if not outcomes:
                raise JunitNoMappedTestsError
            masker = SecretMasker(await self._secret_value_reader.list_secret_values(access.project_id, environment.id))
            run = self._build_run(access.project_id, actor, environment, suite, outcomes, now)
            await self._run_repository.add(run)
            versions = await self._run_start_gate.add_run_cases(
                access.project_id, run, [outcome.case.version for outcome in outcomes], now
            )
            case_results = await self._record_results(run, outcomes, versions, masker, actor, now)
            failure_events = await self._apply_failures(run, outcomes, case_results, actor, now)
            report = await self._build_report(run, case_results, self._mask_unmapped(unmapped_tests, masker), now)
            finished_run = run.model_copy(update={"report": report})
            await self._run_repository.save(finished_run)
            target = await find_run_target(finished_run, self._run_story_reader)
        await self._announce(finished_run, outcomes, case_results, failure_events)
        payload = build_run_finished_payload(finished_run, report, target)
        if payload is not None:
            await self._send_notification.execute(
                finished_run.project_id,
                payload,
                actor_id=actor.user_id,
                recipient_ids={finished_run.started_by},
                recipient_roles={ProjectRole.QC},
            )
        return JunitImport(
            run=finished_run,
            counts=report.counts,
            mapped_test_count=len(tests) - len(unmapped_tests),
            unmapped_test_count=report.unmapped_test_count,
            unmapped_tests=report.unmapped_tests,
        )

    async def _find_environment(self, project_id: UUID, reference: str) -> Environment:
        wanted = reference.strip().casefold()
        for environment in await self._run_target_reader.list_active_environments(project_id):
            if str(environment.id) == wanted or environment.name.strip().casefold() == wanted:
                return environment
        raise UnknownImportEnvironmentError(reference)

    async def _find_suite(self, project_id: UUID, reference: str) -> RunSuite:
        try:
            suite = await self._run_start_gate.require_suite(project_id, reference)
        except SuiteNotFoundError as error:
            raise UnknownImportSuiteError(reference) from error
        if suite.is_archived:
            raise SuiteArchivedError
        return suite

    @staticmethod
    def _build_run(
        project_id: UUID,
        actor: Actor,
        environment: Environment,
        suite: RunSuite | None,
        outcomes: list[ImportedCaseOutcome],
        now: datetime,
    ) -> Run:
        status = decide_run_status([outcome.status for outcome in outcomes])
        return Run(
            id=uuid7(),
            project_id=project_id,
            story_id=None,
            environment_id=environment.id,
            executor=RunExecutor.CI,
            status=status,
            abort_reason=None,
            parent_run_id=None,
            started_by=actor.user_id,
            started_via_token_id=actor.api_token_id,
            summary=None,
            report=None,
            started_at=now,
            last_activity_at=now,
            finished_at=now,
            created_at=now,
            test_suite_id=None if suite is None else suite.id,
        )

    async def _record_results(
        self,
        run: Run,
        outcomes: list[ImportedCaseOutcome],
        versions: list[TestCaseVersion],
        masker: SecretMasker,
        actor: Actor,
        now: datetime,
    ) -> list[CaseResult]:
        versions_by_case_id = {version.test_case_id: version for version in versions}
        case_results: list[CaseResult] = []
        for outcome in outcomes:
            case_result = CaseResult(
                id=uuid7(),
                run_id=run.id,
                test_case_id=outcome.case.test_case_id,
                test_case_version_id=outcome.case.version.id,
                status=outcome.status,
                duration_ms=outcome.duration_ms,
                suspected_cause=None,
                cause_reason=None,
                recorded_by=actor.user_id,
                created_at=now,
            )
            step_results = self._build_step_results(
                case_result, versions_by_case_id[outcome.case.test_case_id], outcome, masker, now
            )
            await self._case_result_repository.add(case_result, step_results)
            case_results.append(case_result)
        return case_results

    @staticmethod
    def _build_step_results(
        case_result: CaseResult,
        version: TestCaseVersion,
        outcome: ImportedCaseOutcome,
        masker: SecretMasker,
        now: datetime,
    ) -> list[StepResult]:
        if outcome.status is not ResultStatus.FAILED:
            return []
        first_step_order = min((step.order for step in version.steps), default=1)
        return [
            StepResult(
                id=uuid7(),
                case_result_id=case_result.id,
                step_order=first_step_order,
                status=ResultStatus.FAILED,
                actual_result=None,
                error=masker.mask_optional(outcome.error),
                screenshot_file_id=None,
                evidence_file_id=None,
                diagnosis=None,
                created_at=now,
            )
        ]

    async def _apply_failures(
        self,
        run: Run,
        outcomes: list[ImportedCaseOutcome],
        case_results: list[CaseResult],
        actor: Actor,
        now: datetime,
    ) -> list[LiveEvent]:
        failure_events: list[LiveEvent] = []
        for outcome, case_result in zip(outcomes, case_results, strict=True):
            failure_events.extend(
                await self._case_result_recorded_handler.handle(
                    RecordedCaseResult(
                        project_id=run.project_id,
                        story_id=outcome.case.story_id,
                        run_id=run.id,
                        case_result_id=case_result.id,
                        test_case_id=case_result.test_case_id,
                        status=case_result.status,
                        suspected_cause=None,
                        cause_reason=None,
                        recorded_by=actor.user_id,
                        recorded_at=now,
                    )
                )
            )
        return failure_events

    async def _build_report(
        self, run: Run, case_results: list[CaseResult], unmapped_tests: list[UnmappedTest], now: datetime
    ) -> RunReport:
        report = build_run_report(
            await self._run_case_repository.list_views(run.id),
            case_results,
            await self._case_result_repository.list_steps_for_run(run.id),
            await self._criterion_impact_calculator.calculate(run.project_id, run.id),
            [],
            None,
            now,
        )
        return report.model_copy(
            update={
                "unmapped_tests": unmapped_tests[:MAX_LISTED_UNMAPPED_TESTS],
                "unmapped_test_count": len(unmapped_tests),
            }
        )

    @staticmethod
    def _mask_unmapped(unmapped_tests: list[UnmappedTest], masker: SecretMasker) -> list[UnmappedTest]:
        return [
            unmapped_test.model_copy(
                update={
                    "name": masker.mask(unmapped_test.name),
                    "classname": masker.mask_optional(unmapped_test.classname),
                }
            )
            for unmapped_test in unmapped_tests
        ]

    async def _announce(
        self,
        run: Run,
        outcomes: list[ImportedCaseOutcome],
        case_results: list[CaseResult],
        failure_events: list[LiveEvent],
    ) -> None:
        await self._live_event_publisher.publish(build_run_started_event(run))
        for outcome, case_result in zip(outcomes, case_results, strict=True):
            await self._live_event_publisher.publish(
                build_run_case_recorded_event(run, case_result, outcome.case.story_id)
            )
        for failure_event in failure_events:
            await self._live_event_publisher.publish(failure_event)
        await self._live_event_publisher.publish(build_run_finished_event(run))
        for case_result in case_results:
            await self._flaky_recompute_requester.request(case_result.test_case_id)
        await self._jira_result_comment_requester.request_after_run(
            run.project_id, run.id, list_jira_comment_story_ids(run, run.report)
        )

from datetime import UTC, datetime
from uuid import UUID

from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_opening.entity import RunOpening
from app.modules.runs.domains.run_sheet.entity import RunSheet
from app.modules.runs.domains.suite_run_opening.entity import SuiteRunOpening
from app.modules.runs.errors import NoFailedCasesToRerunError, RunNotFinishedError, RunNotFoundError
from app.modules.runs.typing.enums import ResultStatus, RunExecutor
from app.modules.runs.usecases.run_start_gate import RunStartGate
from app.modules.runs.utils.run_event import build_run_started_event, build_story_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccess, ProjectAccessResolver, require


class RerunFailedCasesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_start_gate: RunStartGate,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_start_gate = run_start_gate
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        parent_run_id: UUID,
        executor: RunExecutor,
        environment_id: UUID | None,
    ) -> RunSheet:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_START)
            if executor is RunExecutor.MANUAL:
                require(access, Capability.RUN_RECORD_MANUAL)
            parent_run = await self._run_repository.find_by_id(access.project_id, parent_run_id)
            if parent_run is None:
                raise RunNotFoundError
            if parent_run.is_running:
                raise RunNotFinishedError
            candidate_case_ids = await self._list_rerun_candidate_ids(parent_run)
            kept_case_ids = await self._keep_ready_case_ids(access.project_id, parent_run, candidate_case_ids)
            if not kept_case_ids:
                raise NoFailedCasesToRerunError
            sheet = await self._open_rerun(access, actor, parent_run, executor, environment_id, kept_case_ids, now)
        await self._announce(sheet, parent_run.id)
        return sheet

    async def _keep_ready_case_ids(
        self, project_id: UUID, parent_run: Run, candidate_case_ids: list[UUID]
    ) -> list[UUID]:
        if not candidate_case_ids:
            return []
        if parent_run.test_suite_id is not None:
            return await self._run_start_gate.list_ready_suite_case_ids(
                project_id, parent_run.test_suite_id, candidate_case_ids
            )
        if parent_run.story_id is None:
            return []
        return await self._run_start_gate.list_ready_case_ids(project_id, parent_run.story_id, candidate_case_ids)

    async def _open_rerun(
        self,
        access: ProjectAccess,
        actor: Actor,
        parent_run: Run,
        executor: RunExecutor,
        environment_id: UUID | None,
        test_case_ids: list[UUID],
        now: datetime,
    ) -> RunSheet:
        if parent_run.test_suite_id is not None:
            return await self._run_start_gate.open_suite_run(
                access,
                actor,
                SuiteRunOpening(
                    suite_id=parent_run.test_suite_id,
                    environment_id=environment_id,
                    executor=executor,
                    parent_run_id=parent_run.id,
                    test_case_ids=test_case_ids,
                ),
                now,
            )
        if parent_run.story_id is None:
            raise NoFailedCasesToRerunError
        return await self._run_start_gate.open_run(
            access,
            actor,
            RunOpening(
                story_id=parent_run.story_id,
                environment_id=environment_id,
                executor=executor,
                parent_run_id=parent_run.id,
                test_case_ids=test_case_ids,
            ),
            now,
        )

    async def _list_rerun_candidate_ids(self, parent_run: Run) -> list[UUID]:
        case_results = await self._case_result_repository.list_for_run(parent_run.id)
        failing_case_ids = {
            case_result.test_case_id
            for case_result in case_results
            if case_result.status in {ResultStatus.FAILED, ResultStatus.BLOCKED}
        }
        run_cases = await self._run_case_repository.list_for_run(parent_run.id)
        return [
            run_case.test_case_id
            for run_case in sorted(run_cases, key=lambda parent_case: parent_case.position)
            if run_case.test_case_id in failing_case_ids
        ]

    async def _announce(self, sheet: RunSheet, parent_run_id: UUID) -> None:
        run = sheet.run
        await self._live_event_publisher.publish(build_run_started_event(run, {"parentRunId": str(parent_run_id)}))
        if sheet.story_jira_key is not None:
            await self._live_event_publisher.publish(build_story_changed_event(run, sheet.story_jira_key))

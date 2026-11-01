from datetime import UTC, datetime
from uuid import UUID

from app.modules.runs.domains.case_result.repository import CaseResultRepository
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_opening.entity import RunOpening
from app.modules.runs.domains.run_story.entity import RunStory
from app.modules.runs.domains.started_run.entity import StartedRun
from app.modules.runs.errors import (
    EnvironmentNotFoundError,
    InvalidRequestError,
    NoFailedCasesToRerunError,
    ParentRunMismatchError,
    RunNotFinishedError,
    RunNotFoundError,
)
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.typing.constants.run_report import FAILING_RESULT_STATUSES
from app.modules.runs.typing.enums import RunExecutor
from app.modules.runs.usecases.run_start_gate import RunStartGate
from app.modules.runs.utils.run_event import build_run_started_event, build_story_changed_event
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class StartRunUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        case_result_repository: CaseResultRepository,
        run_target_reader: RunTargetReader,
        run_start_gate: RunStartGate,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._case_result_repository = case_result_repository
        self._run_target_reader = run_target_reader
        self._run_start_gate = run_start_gate
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        story_key: str,
        environment_name: str | None,
        case_ids: list[UUID] | None,
        parent_run_id: UUID | None,
    ) -> StartedRun:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_START)
            story = await self._run_target_reader.find_story(access.project_id, story_key)
            if story is None:
                raise StoryNotFoundError
            environment_id = (
                None
                if environment_name is None
                else await self._find_environment_id(access.project_id, environment_name)
            )
            test_case_ids = (
                case_ids
                if parent_run_id is None
                else await self._list_rerun_case_ids(access.project_id, story, case_ids, parent_run_id)
            )
            sheet = await self._run_start_gate.open_run(
                access,
                actor,
                RunOpening(
                    story_id=story.id,
                    environment_id=environment_id,
                    executor=RunExecutor.CLAUDE,
                    parent_run_id=parent_run_id,
                    test_case_ids=test_case_ids,
                ),
                now,
            )
            environment = await self._run_target_reader.find_environment_by_id(
                access.project_id, sheet.run.environment_id
            )
            if environment is None:
                raise EnvironmentNotFoundError(str(sheet.run.environment_id))
            run_cases = await self._run_case_repository.list_views(sheet.run.id)
        await self._live_event_publisher.publish(build_run_started_event(sheet.run))
        await self._live_event_publisher.publish(build_story_changed_event(sheet.run, sheet.story_jira_key))
        return StartedRun(run=sheet.run, environment=environment, cases=run_cases)

    async def _find_environment_id(self, project_id: UUID, environment_name: str) -> UUID:
        wanted_name = environment_name.strip().casefold()
        for environment in await self._run_target_reader.list_active_environments(project_id):
            if environment.name.strip().casefold() == wanted_name:
                return environment.id
        raise EnvironmentNotFoundError(environment_name)

    async def _list_rerun_case_ids(
        self, project_id: UUID, story: RunStory, case_ids: list[UUID] | None, parent_run_id: UUID
    ) -> list[UUID]:
        if case_ids is not None:
            raise InvalidRequestError("Pass either case_ids or parent_run_id, not both.")
        parent_run = await self._run_repository.find_by_id(project_id, parent_run_id)
        if parent_run is None:
            raise RunNotFoundError
        if parent_run.story_id != story.id:
            raise ParentRunMismatchError
        if parent_run.is_running:
            raise RunNotFinishedError
        failing_case_ids = {
            case_result.test_case_id
            for case_result in await self._case_result_repository.list_for_run(parent_run.id)
            if case_result.status in FAILING_RESULT_STATUSES
        }
        candidate_ids = [
            run_case.test_case_id
            for run_case in await self._run_case_repository.list_for_run(parent_run.id)
            if run_case.test_case_id in failing_case_ids
        ]
        rerun_case_ids = await self._run_start_gate.list_ready_case_ids(project_id, story.id, candidate_ids)
        if not rerun_case_ids:
            raise NoFailedCasesToRerunError
        return rerun_case_ids

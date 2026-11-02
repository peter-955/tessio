from collections.abc import Collection
from datetime import datetime
from uuid import UUID, uuid7

from app.modules.gaps import OpenGapChecker
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run.repository import RunRepository
from app.modules.runs.domains.run_case.entity import RunCase
from app.modules.runs.domains.run_case.repository import RunCaseRepository
from app.modules.runs.domains.run_opening.entity import RunOpening
from app.modules.runs.domains.run_sheet.entity import RunSheet
from app.modules.runs.domains.run_suite.entity import RunSuite
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.runs.domains.story_case.entity import StoryCase
from app.modules.runs.domains.suite_run_case.entity import SuiteRunCase
from app.modules.runs.domains.suite_run_opening.entity import SuiteRunOpening
from app.modules.runs.errors import (
    CaseNotReadyError,
    EnvironmentNotFoundError,
    EnvironmentRequiredError,
    NoReadyCasesError,
    RunAlreadyRunningError,
    SuiteAlreadyRunningError,
    SuiteArchivedError,
    SuiteEmptyError,
    SuiteNotFoundError,
    SuiteOpenGapsBlockRunError,
    UnknownCaseError,
    UnknownSuiteCaseError,
)
from app.modules.runs.ports.run_gap_reader import RunGapReader
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.ports.suite_run_scope_reader import SuiteRunScopeReader
from app.modules.runs.typing.enums import RunStatus
from app.modules.runs.utils.skip_reason import find_skip_reason
from app.modules.stories import MarkStoryInTestUseCase, StoryNotFoundError
from app.modules.test_cases import CaseStepExpander, TestCaseStatus, TestCaseVersion
from app.modules.test_data import Environment
from app.shared.permissions import Actor, ProjectAccess


class RunStartGate:
    def __init__(
        self,
        open_gap_checker: OpenGapChecker,
        run_repository: RunRepository,
        run_case_repository: RunCaseRepository,
        run_target_reader: RunTargetReader,
        mark_story_in_test: MarkStoryInTestUseCase,
        suite_run_scope_reader: SuiteRunScopeReader,
        run_gap_reader: RunGapReader,
        case_step_expander: CaseStepExpander,
    ) -> None:
        self._open_gap_checker = open_gap_checker
        self._run_repository = run_repository
        self._run_case_repository = run_case_repository
        self._run_target_reader = run_target_reader
        self._mark_story_in_test = mark_story_in_test
        self._suite_run_scope_reader = suite_run_scope_reader
        self._run_gap_reader = run_gap_reader
        self._case_step_expander = case_step_expander

    async def select_cases(
        self, project_id: UUID, story_id: UUID, case_ids: Collection[UUID] | None
    ) -> list[StoryCase]:
        await self._open_gap_checker.ensure_no_open_gaps(story_id)
        if await self._run_repository.has_running_for_story(project_id, story_id):
            raise RunAlreadyRunningError
        story_cases = await self._run_target_reader.list_story_cases(project_id, story_id)
        if case_ids is None:
            selected_cases = [story_case for story_case in story_cases if story_case.status is TestCaseStatus.READY]
        else:
            selected_cases = self._pick_cases(story_cases, case_ids)
        if not selected_cases:
            raise NoReadyCasesError
        return selected_cases

    async def require_story_id(self, project_id: UUID, jira_key: str) -> UUID:
        story = await self._run_target_reader.find_story(project_id, jira_key)
        if story is None:
            raise StoryNotFoundError
        return story.id

    async def list_ready_case_ids(self, project_id: UUID, story_id: UUID, test_case_ids: list[UUID]) -> list[UUID]:
        story_cases = await self._run_target_reader.list_story_cases(project_id, story_id)
        ready_case_ids = {
            story_case.test_case_id for story_case in story_cases if story_case.status is TestCaseStatus.READY
        }
        return [test_case_id for test_case_id in dict.fromkeys(test_case_ids) if test_case_id in ready_case_ids]

    async def open_run(self, access: ProjectAccess, actor: Actor, opening: RunOpening, now: datetime) -> RunSheet:
        story = await self._mark_story_in_test.execute(access.project_id, opening.story_id, actor.user_id, now)
        environment = await self._resolve_environment(access.project_id, opening.environment_id, opening.parent_run_id)
        story_cases = await self.select_cases(access.project_id, opening.story_id, opening.test_case_ids)
        run = Run(
            id=uuid7(),
            project_id=access.project_id,
            story_id=opening.story_id,
            environment_id=environment.id,
            executor=opening.executor,
            status=RunStatus.RUNNING,
            abort_reason=None,
            parent_run_id=opening.parent_run_id,
            started_by=actor.user_id,
            started_via_token_id=actor.api_token_id,
            summary=None,
            report=None,
            started_at=now,
            last_activity_at=now,
            finished_at=None,
            created_at=now,
        )
        await self._run_repository.add(run)
        case_versions = await self.add_run_cases(
            access.project_id, run, [story_case.version for story_case in story_cases], now
        )
        return RunSheet(run=run, story_jira_key=story.jira_key, case_versions=case_versions, case_results=[])

    async def require_suite(self, project_id: UUID, reference: str) -> RunSuite:
        suite = await self._suite_run_scope_reader.find_suite(project_id, reference)
        if suite is None:
            raise SuiteNotFoundError
        return suite

    async def require_suite_by_id(self, project_id: UUID, suite_id: UUID) -> RunSuite:
        suite = await self._suite_run_scope_reader.find_suite_by_id(project_id, suite_id)
        if suite is None:
            raise SuiteNotFoundError
        return suite

    async def list_ready_suite_case_ids(
        self, project_id: UUID, suite_id: UUID, test_case_ids: list[UUID]
    ) -> list[UUID]:
        suite_cases = await self._suite_run_scope_reader.list_suite_cases(project_id, suite_id)
        runnable_case_ids = {
            suite_case.test_case_id for suite_case in suite_cases if find_skip_reason(suite_case) is None
        }
        return [test_case_id for test_case_id in dict.fromkeys(test_case_ids) if test_case_id in runnable_case_ids]

    async def open_suite_run(
        self, access: ProjectAccess, actor: Actor, opening: SuiteRunOpening, now: datetime
    ) -> RunSheet:
        suite = await self.require_suite_by_id(access.project_id, opening.suite_id)
        if suite.is_archived:
            raise SuiteArchivedError
        environment = await self._resolve_environment(access.project_id, opening.environment_id, opening.parent_run_id)
        suite_cases = await self._suite_run_scope_reader.list_suite_cases(access.project_id, suite.id)
        await self._ensure_no_open_gaps(access.project_id, suite_cases)
        if await self._run_repository.has_running_for_suite(access.project_id, suite.id):
            raise SuiteAlreadyRunningError
        selected_cases, skipped_cases = self._select_suite_cases(suite_cases, opening.test_case_ids)
        if not selected_cases:
            raise SuiteEmptyError
        run = Run(
            id=uuid7(),
            project_id=access.project_id,
            story_id=None,
            environment_id=environment.id,
            executor=opening.executor,
            status=RunStatus.RUNNING,
            abort_reason=None,
            parent_run_id=opening.parent_run_id,
            started_by=actor.user_id,
            started_via_token_id=actor.api_token_id,
            summary=None,
            report=None,
            started_at=now,
            last_activity_at=now,
            finished_at=None,
            created_at=now,
            test_suite_id=suite.id,
            skipped_cases=skipped_cases,
        )
        await self._run_repository.add(run)
        case_versions = await self.add_run_cases(
            access.project_id, run, [suite_case.version for suite_case in selected_cases], now
        )
        return RunSheet(
            run=run,
            story_jira_key=None,
            case_versions=case_versions,
            case_results=[],
            suite_name=suite.name,
            skipped_cases=skipped_cases,
        )

    async def add_run_cases(
        self, project_id: UUID, run: Run, versions: list[TestCaseVersion], now: datetime
    ) -> list[TestCaseVersion]:
        expanded_versions = await self._case_step_expander.expand(project_id, versions)
        await self._run_case_repository.add_all(
            [
                RunCase(
                    id=uuid7(),
                    run_id=run.id,
                    test_case_id=version.test_case_id,
                    test_case_version_id=version.id,
                    position=position,
                    created_at=now,
                    steps=version.steps,
                )
                for position, version in enumerate(expanded_versions, start=1)
            ]
        )
        return expanded_versions

    async def _ensure_no_open_gaps(self, project_id: UUID, suite_cases: list[SuiteRunCase]) -> None:
        story_ids = {suite_case.story_id for suite_case in suite_cases}
        open_gaps = await self._run_gap_reader.list_open_gaps(project_id, story_ids)
        if open_gaps:
            raise SuiteOpenGapsBlockRunError(open_gaps)

    def _select_suite_cases(
        self, suite_cases: list[SuiteRunCase], case_ids: Collection[UUID] | None
    ) -> tuple[list[SuiteRunCase], list[SkippedRunCase]]:
        if case_ids is not None:
            return self._pick_suite_cases(suite_cases, case_ids), []
        selected_cases: list[SuiteRunCase] = []
        skipped_cases: list[SkippedRunCase] = []
        for suite_case in suite_cases:
            skip_reason = find_skip_reason(suite_case)
            if skip_reason is None:
                selected_cases.append(suite_case)
            else:
                skipped_cases.append(
                    SkippedRunCase(
                        test_case_id=suite_case.test_case_id,
                        code=suite_case.code,
                        title=suite_case.version.title,
                        story_jira_key=suite_case.story_jira_key,
                        reason=skip_reason,
                    )
                )
        return selected_cases, skipped_cases

    def _pick_suite_cases(self, suite_cases: list[SuiteRunCase], case_ids: Collection[UUID]) -> list[SuiteRunCase]:
        cases_by_id = {suite_case.test_case_id: suite_case for suite_case in suite_cases}
        picked_cases: list[SuiteRunCase] = []
        for case_id in dict.fromkeys(case_ids):
            suite_case = cases_by_id.get(case_id)
            if suite_case is None:
                raise UnknownSuiteCaseError
            if find_skip_reason(suite_case) is not None:
                raise CaseNotReadyError(suite_case.code)
            picked_cases.append(suite_case)
        return picked_cases

    async def _resolve_environment(
        self, project_id: UUID, environment_id: UUID | None, parent_run_id: UUID | None
    ) -> Environment:
        if environment_id is not None:
            environment = await self._run_target_reader.find_environment_by_id(project_id, environment_id)
            if environment is None or environment.is_archived:
                raise EnvironmentNotFoundError(str(environment_id))
            return environment
        active_environments = await self._run_target_reader.list_active_environments(project_id)
        active_by_id = {environment.id: environment for environment in active_environments}
        if parent_run_id is not None:
            parent_run = await self._run_repository.find_by_id(project_id, parent_run_id)
            if parent_run is not None and parent_run.environment_id in active_by_id:
                return active_by_id[parent_run.environment_id]
        default_environment_id = await self._run_target_reader.find_default_environment_id(project_id)
        if default_environment_id is not None and default_environment_id in active_by_id:
            return active_by_id[default_environment_id]
        if len(active_environments) == 1:
            return active_environments[0]
        raise EnvironmentRequiredError([environment.name for environment in active_environments])

    @staticmethod
    def _pick_cases(story_cases: list[StoryCase], case_ids: Collection[UUID]) -> list[StoryCase]:
        cases_by_id = {story_case.test_case_id: story_case for story_case in story_cases}
        picked_cases: list[StoryCase] = []
        for case_id in dict.fromkeys(case_ids):
            story_case = cases_by_id.get(case_id)
            if story_case is None:
                raise UnknownCaseError
            if story_case.status is not TestCaseStatus.READY:
                raise CaseNotReadyError(story_case.code)
            picked_cases.append(story_case)
        return picked_cases

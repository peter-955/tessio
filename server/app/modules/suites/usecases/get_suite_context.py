from uuid import UUID

from app.modules.runs import (
    RunSuite,
    SkippedRunCase,
    SuiteArchivedError,
    SuiteNotFoundError,
    SuiteRunCase,
    SuiteRunScopeReader,
    find_skip_reason,
)
from app.modules.story_context import StoryContextReader
from app.modules.suites.domains.suite_context.entity import SuiteContext
from app.modules.suites.domains.suite_context_story.entity import SuiteContextStory
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetSuiteContextUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        suite_run_scope_reader: SuiteRunScopeReader,
        test_suite_repository: TestSuiteRepository,
        story_context_reader: StoryContextReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._suite_run_scope_reader = suite_run_scope_reader
        self._test_suite_repository = test_suite_repository
        self._story_context_reader = story_context_reader

    async def execute_in_token_project(self, actor: Actor, suite_reference: str) -> SuiteContext:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.RUN_VIEW)
            require(access, Capability.STORY_VIEW)
            require(access, Capability.TEST_CASE_VIEW)
            require(access, Capability.TEST_DATA_VIEW)
            run_suite = await self._require_active_suite(access.project_id, suite_reference)
            suite = await self._test_suite_repository.find_by_id(access.project_id, run_suite.id)
            if suite is None:
                raise SuiteNotFoundError
            suite_cases = await self._suite_run_scope_reader.list_suite_cases(access.project_id, suite.id)
            runnable_cases = [suite_case for suite_case in suite_cases if find_skip_reason(suite_case) is None]
            stories = await self._list_stories(access.project_id, runnable_cases)
            used_keys = {key for story in stories for case in story.cases for key in case.data_keys}
            data_entries = [
                entry
                for entry in await self._story_context_reader.list_data_entries(access.project_id)
                if entry.key in used_keys
            ]
            environments = await self._story_context_reader.list_environments(access.project_id)
        return SuiteContext(
            suite=suite,
            stories=stories,
            skipped_cases=[
                SkippedRunCase(
                    test_case_id=suite_case.test_case_id,
                    code=suite_case.code,
                    title=suite_case.version.title,
                    story_jira_key=suite_case.story_jira_key,
                    reason=skip_reason,
                )
                for suite_case in suite_cases
                if (skip_reason := find_skip_reason(suite_case)) is not None
            ],
            data_entries=data_entries,
            environments=environments,
        )

    async def _require_active_suite(self, project_id: UUID, suite_reference: str) -> RunSuite:
        run_suite = await self._suite_run_scope_reader.find_suite(project_id, suite_reference)
        if run_suite is None:
            raise SuiteNotFoundError
        if run_suite.is_archived:
            raise SuiteArchivedError
        return run_suite

    async def _list_stories(self, project_id: UUID, runnable_cases: list[SuiteRunCase]) -> list[SuiteContextStory]:
        case_ids_by_story_key: dict[str, list[UUID]] = {}
        for suite_case in runnable_cases:
            case_ids_by_story_key.setdefault(suite_case.story_jira_key, []).append(suite_case.test_case_id)
        stories: list[SuiteContextStory] = []
        for story_key, case_ids in case_ids_by_story_key.items():
            story = await self._story_context_reader.find_story(project_id, story_key)
            if story is None:
                continue
            cases_by_id = {case.id: case for case in await self._story_context_reader.list_ready_cases(story.id)}
            stories.append(
                SuiteContextStory(
                    story=story,
                    criteria=await self._story_context_reader.list_criteria(story.id),
                    cases=[cases_by_id[case_id] for case_id in case_ids if case_id in cases_by_id],
                )
            )
        return stories

from collections.abc import Collection
from uuid import UUID

from sqlalchemy import and_, case, exists, func, select
from sqlalchemy.dialects.postgresql import distinct_on

from app.modules.labels.infrastructure import LabelTable, TestCaseLabelTable
from app.modules.runs import RunStatus
from app.modules.runs.infrastructure import RunTable
from app.modules.stories.infrastructure import SprintTable, StoryTable
from app.modules.suites.domains.suite_case_filter.entity import SuiteCaseFilter
from app.modules.suites.domains.suite_case_view.entity import SuiteCaseView
from app.modules.suites.domains.suite_run_reference.entity import SuiteRunReference
from app.modules.suites.domains.suite_summary.entity import SuiteSummary
from app.modules.suites.domains.test_suite.entity import TestSuite
from app.modules.suites.infrastructure.test_suite_case_table import TestSuiteCaseTable
from app.modules.suites.infrastructure.test_suite_table import TestSuiteTable
from app.modules.suites.ports.suite_view_reader import SuiteViewReader
from app.modules.test_cases import TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseTable
from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.shared.postgres import Database


class PostgresSuiteViewReader(SuiteViewReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_summaries(self, project_id: UUID, is_including_archived: bool) -> list[SuiteSummary]:
        is_runnable = and_(TestCaseTable.status == TestCaseStatus.READY, TestCaseTable.needs_review_at.is_(None))
        counts = (
            select(
                TestSuiteCaseTable.test_suite_id.label("test_suite_id"),
                func.count().label("case_count"),
                func.count(case((is_runnable, 1))).label("ready_case_count"),
            )
            .join(TestCaseTable, TestCaseTable.id == TestSuiteCaseTable.test_case_id)
            .group_by(TestSuiteCaseTable.test_suite_id)
            .subquery("suite_case_counts")
        )
        statement = (
            select(TestSuiteTable, counts.c.case_count, counts.c.ready_case_count)
            .outerjoin(counts, counts.c.test_suite_id == TestSuiteTable.id)
            .where(TestSuiteTable.project_id == project_id)
            .order_by(func.lower(TestSuiteTable.name), TestSuiteTable.id)
        )
        if not is_including_archived:
            statement = statement.where(TestSuiteTable.archived_at.is_(None))
        rows = (await self._database.get_current_session().execute(statement)).all()
        last_runs = await self._map_last_runs([row[0].id for row in rows])
        return [
            SuiteSummary(
                suite=TestSuite.model_validate(suite_row),
                case_count=case_count or 0,
                ready_case_count=ready_case_count or 0,
                last_run=last_runs.get(suite_row.id),
            )
            for suite_row, case_count, ready_case_count in rows
        ]

    async def list_case_views(self, suite_id: UUID) -> list[SuiteCaseView]:
        result = await self._database.get_current_session().execute(
            select(TestSuiteCaseTable.position, TestCaseTable, StoryTable.jira_key, StoryTable.title)
            .join(TestCaseTable, TestCaseTable.id == TestSuiteCaseTable.test_case_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(TestSuiteCaseTable.test_suite_id == suite_id)
            .order_by(TestSuiteCaseTable.position)
        )
        return [
            SuiteCaseView(
                test_case_id=test_case.id,
                code=f"{CASE_CODE_PREFIX}{test_case.number}",
                title=test_case.title,
                status=test_case.status,
                priority=test_case.priority,
                is_needing_review=test_case.needs_review_at is not None,
                story_id=test_case.story_id,
                story_jira_key=jira_key,
                story_title=story_title,
                position=position,
            )
            for position, test_case, jira_key, story_title in result
        ]

    async def find_last_run(self, suite_id: UUID) -> SuiteRunReference | None:
        return (await self._map_last_runs([suite_id])).get(suite_id)

    async def find_running_run(self, suite_id: UUID) -> SuiteRunReference | None:
        row = (
            await self._database.get_current_session().execute(
                select(RunTable.id, RunTable.status, RunTable.started_at, RunTable.finished_at).where(
                    RunTable.test_suite_id == suite_id, RunTable.status == RunStatus.RUNNING
                )
            )
        ).first()
        if row is None:
            return None
        run_id, status, started_at, finished_at = row
        return SuiteRunReference(id=run_id, status=status, started_at=started_at, finished_at=finished_at)

    async def list_project_case_ids(self, project_id: UUID, test_case_ids: Collection[UUID]) -> set[UUID]:
        if not test_case_ids:
            return set()
        found_ids = await self._database.get_current_session().scalars(
            select(TestCaseTable.id).where(TestCaseTable.project_id == project_id, TestCaseTable.id.in_(test_case_ids))
        )
        return set(found_ids)

    async def list_matching_case_ids(self, project_id: UUID, case_filter: SuiteCaseFilter) -> list[UUID]:
        statement = (
            select(TestCaseTable.id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(TestCaseTable.project_id == project_id, TestCaseTable.status != TestCaseStatus.DEPRECATED)
            .order_by(TestCaseTable.number)
        )
        if case_filter.priorities:
            statement = statement.where(TestCaseTable.priority.in_(case_filter.priorities))
        if case_filter.story_id is not None:
            statement = statement.where(TestCaseTable.story_id == case_filter.story_id)
        if case_filter.sprint_id is not None:
            statement = statement.where(StoryTable.sprint_id == case_filter.sprint_id)
        for label_name in case_filter.label_names:
            statement = statement.where(
                exists().where(
                    TestCaseLabelTable.test_case_id == TestCaseTable.id,
                    TestCaseLabelTable.label_id == LabelTable.id,
                    LabelTable.project_id == project_id,
                    func.lower(LabelTable.name) == label_name.strip().lower(),
                )
            )
        case_ids = await self._database.get_current_session().scalars(statement)
        return list(case_ids)

    async def find_story_id(self, project_id: UUID, story_key: str) -> UUID | None:
        story_id: UUID | None = await self._database.get_current_session().scalar(
            select(StoryTable.id).where(
                StoryTable.project_id == project_id, StoryTable.jira_key == story_key.strip().upper()
            )
        )
        return story_id

    async def has_sprint(self, project_id: UUID, sprint_id: UUID) -> bool:
        found = await self._database.get_current_session().scalar(
            select(exists().where(SprintTable.project_id == project_id, SprintTable.id == sprint_id))
        )
        return bool(found)

    async def _map_last_runs(self, suite_ids: Collection[UUID]) -> dict[UUID, SuiteRunReference]:
        if not suite_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(RunTable.test_suite_id, RunTable.id, RunTable.status, RunTable.started_at, RunTable.finished_at)
            .ext(distinct_on(RunTable.test_suite_id))
            .where(RunTable.test_suite_id.in_(suite_ids))
            .order_by(RunTable.test_suite_id, RunTable.started_at.desc(), RunTable.id.desc())
        )
        return {
            suite_id: SuiteRunReference(id=run_id, status=status, started_at=started_at, finished_at=finished_at)
            for suite_id, run_id, status, started_at, finished_at in result
            if suite_id is not None
        }

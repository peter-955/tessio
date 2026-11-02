from uuid import UUID

from sqlalchemy import func, select

from app.modules.runs import RunSuite, SuiteRunCase, SuiteRunScopeReader
from app.modules.stories.infrastructure import StoryTable
from app.modules.suites.infrastructure.test_suite_case_table import TestSuiteCaseTable
from app.modules.suites.infrastructure.test_suite_table import TestSuiteTable
from app.modules.suites.utils.suite_reference import parse_suite_id
from app.modules.test_cases import TestCaseVersion
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.shared.postgres import Database


class PostgresSuiteRunScopeReader(SuiteRunScopeReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_suite(self, project_id: UUID, reference: str) -> RunSuite | None:
        suite_id = parse_suite_id(reference)
        if suite_id is not None:
            return await self.find_suite_by_id(project_id, suite_id)
        row = await self._database.get_current_session().scalar(
            select(TestSuiteTable)
            .where(
                TestSuiteTable.project_id == project_id,
                func.lower(TestSuiteTable.name) == reference.strip().lower(),
            )
            .order_by(TestSuiteTable.archived_at.is_not(None), TestSuiteTable.archived_at.desc())
            .limit(1)
        )
        return None if row is None else self._build_suite(row)

    async def find_suite_by_id(self, project_id: UUID, suite_id: UUID) -> RunSuite | None:
        row = await self._database.get_current_session().scalar(
            select(TestSuiteTable).where(TestSuiteTable.project_id == project_id, TestSuiteTable.id == suite_id)
        )
        return None if row is None else self._build_suite(row)

    async def list_suite_cases(self, project_id: UUID, suite_id: UUID) -> list[SuiteRunCase]:
        result = await self._database.get_current_session().execute(
            select(TestCaseTable, TestCaseVersionTable, StoryTable.jira_key)
            .select_from(TestSuiteCaseTable)
            .join(TestCaseTable, TestCaseTable.id == TestSuiteCaseTable.test_case_id)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .join(StoryTable, StoryTable.id == TestCaseTable.story_id)
            .where(TestSuiteCaseTable.test_suite_id == suite_id, TestCaseTable.project_id == project_id)
            .order_by(TestSuiteCaseTable.position)
            .execution_options(populate_existing=True)
        )
        return [
            SuiteRunCase(
                test_case_id=test_case.id,
                code=f"{CASE_CODE_PREFIX}{test_case.number}",
                status=test_case.status,
                is_needing_review=test_case.needs_review_at is not None,
                story_id=test_case.story_id,
                story_jira_key=jira_key,
                version=TestCaseVersion.model_validate(version_row),
            )
            for test_case, version_row, jira_key in result
        ]

    @staticmethod
    def _build_suite(row: TestSuiteTable) -> RunSuite:
        return RunSuite(id=row.id, name=row.name, is_archived=row.archived_at is not None)

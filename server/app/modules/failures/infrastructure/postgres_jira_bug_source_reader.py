from uuid import UUID

from pydantic import JsonValue, TypeAdapter
from sqlalchemy import and_, select

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.domains.jira_bug_source.entity import JiraBugSource
from app.modules.failures.ports.jira_bug_source_reader import JiraBugSourceReader
from app.modules.failures.typing.constants import TEST_CASE_CODE_PREFIX
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.infrastructure import CaseResultTable, RunCaseTable, RunTable
from app.modules.stories import StorySource
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases import TestStep
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.postgres import Database

STEPS_ADAPTER = TypeAdapter(list[TestStep])
DATA_ROWS_ADAPTER = TypeAdapter(list[dict[str, str]])


class PostgresJiraBugSourceReader(JiraBugSourceReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, failure: Failure) -> JiraBugSource | None:
        result = await self._database.get_current_session().execute(
            select(
                ProjectTable.key,
                ProjectTable.jira_project_key,
                ProjectTable.jira_bug_issue_type,
                StoryTable.jira_key,
                StoryTable.title,
                StoryTable.source,
                TestCaseTable.number,
                TestCaseVersionTable.title,
                TestCaseVersionTable.preconditions,
                TestCaseVersionTable.steps,
                TestCaseVersionTable.data_rows,
                RunCaseTable.steps,
                CaseResultTable.iteration,
                EnvironmentTable.id,
                EnvironmentTable.name,
                EnvironmentTable.base_url,
            )
            .select_from(CaseResultTable)
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .join(EnvironmentTable, EnvironmentTable.id == RunTable.environment_id)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == CaseResultTable.test_case_version_id)
            .join(TestCaseTable, TestCaseTable.id == CaseResultTable.test_case_id)
            .join(ProjectTable, ProjectTable.id == RunTable.project_id)
            .join(StoryTable, StoryTable.id == failure.story_id)
            .outerjoin(
                RunCaseTable,
                and_(
                    RunCaseTable.run_id == CaseResultTable.run_id,
                    RunCaseTable.test_case_id == CaseResultTable.test_case_id,
                ),
            )
            .where(CaseResultTable.id == failure.latest_case_result_id, RunTable.project_id == failure.project_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        (
            project_key,
            jira_project_key,
            jira_bug_issue_type,
            story_jira_key,
            story_title,
            story_source,
            test_case_number,
            test_case_title,
            preconditions,
            version_steps,
            data_rows,
            snapshot_steps,
            iteration,
            environment_id,
            environment_name,
            environment_base_url,
        ) = row
        return JiraBugSource(
            failure_id=failure.id,
            project_key=project_key,
            jira_project_key=jira_project_key,
            jira_bug_issue_type=jira_bug_issue_type,
            story_jira_key=story_jira_key,
            story_title=story_title,
            is_story_from_jira=story_source is StorySource.JIRA,
            test_case_code=f"{TEST_CASE_CODE_PREFIX}{test_case_number}",
            test_case_title=test_case_title,
            preconditions=preconditions,
            steps=self._parse_steps(snapshot_steps if snapshot_steps is not None else version_steps),
            iteration=iteration,
            data_row=self._find_data_row(data_rows, iteration),
            repro_steps=None,
            environment_id=environment_id,
            environment_name=environment_name,
            environment_base_url=environment_base_url,
            cause=failure.cause,
            cause_reason=failure.cause_reason,
        )

    async def find_jira_project_key(self, project_id: UUID) -> str | None:
        jira_project_key: str | None = await self._database.get_current_session().scalar(
            select(ProjectTable.jira_project_key).where(ProjectTable.id == project_id)
        )
        return jira_project_key

    @staticmethod
    def _parse_steps(steps: JsonValue) -> list[TestStep]:
        return STEPS_ADAPTER.validate_python(steps or [])

    @staticmethod
    def _find_data_row(data_rows: JsonValue, iteration: int) -> dict[str, str] | None:
        rows = DATA_ROWS_ADAPTER.validate_python(data_rows or [])
        return rows[iteration] if 0 <= iteration < len(rows) else None

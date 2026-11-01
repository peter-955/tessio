from uuid import UUID

from sqlalchemy import select

from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.domains.run_story.entity import RunStory
from app.modules.runs.domains.story_case.entity import StoryCase
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases import TestCaseStatus, TestCaseVersion
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_cases.typing.constants import CASE_CODE_PREFIX
from app.modules.test_data import Environment
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.postgres import Database


class PostgresRunTargetReader(RunTargetReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_story(self, project_id: UUID, story_key: str) -> RunStory | None:
        result = await self._database.get_current_session().execute(
            select(StoryTable.id, StoryTable.jira_key, StoryTable.title).where(
                StoryTable.project_id == project_id, StoryTable.jira_key == story_key.strip().upper()
            )
        )
        row = result.one_or_none()
        if row is None:
            return None
        story_id, jira_key, title = row
        return RunStory(id=story_id, jira_key=jira_key, title=title)

    async def find_story_by_id(self, project_id: UUID, story_id: UUID) -> RunStory | None:
        result = await self._database.get_current_session().execute(
            select(StoryTable.id, StoryTable.jira_key, StoryTable.title).where(
                StoryTable.project_id == project_id, StoryTable.id == story_id
            )
        )
        row = result.one_or_none()
        if row is None:
            return None
        found_story_id, jira_key, title = row
        return RunStory(id=found_story_id, jira_key=jira_key, title=title)

    async def list_story_cases(self, project_id: UUID, story_id: UUID) -> list[StoryCase]:
        result = await self._database.get_current_session().execute(
            select(TestCaseTable.id, TestCaseTable.number, TestCaseTable.status, TestCaseVersionTable)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .where(
                TestCaseTable.project_id == project_id,
                TestCaseTable.story_id == story_id,
                TestCaseTable.status != TestCaseStatus.DEPRECATED,
            )
            .order_by(TestCaseTable.number)
            .execution_options(populate_existing=True)
        )
        return [
            StoryCase(
                test_case_id=test_case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                status=status,
                version=TestCaseVersion.model_validate(version_row),
            )
            for test_case_id, number, status, version_row in result
        ]

    async def find_environment_by_id(self, project_id: UUID, environment_id: UUID) -> Environment | None:
        row = await self._database.get_current_session().scalar(
            select(EnvironmentTable).where(
                EnvironmentTable.project_id == project_id, EnvironmentTable.id == environment_id
            )
        )
        return None if row is None else Environment.model_validate(row)

    async def list_active_environments(self, project_id: UUID) -> list[Environment]:
        rows = await self._database.get_current_session().scalars(
            select(EnvironmentTable)
            .where(EnvironmentTable.project_id == project_id, EnvironmentTable.archived_at.is_(None))
            .order_by(EnvironmentTable.name, EnvironmentTable.id)
        )
        return [Environment.model_validate(row) for row in rows]

    async def find_default_environment_id(self, project_id: UUID) -> UUID | None:
        default_environment_id: UUID | None = await self._database.get_current_session().scalar(
            select(ProjectTable.default_environment_id).where(ProjectTable.id == project_id)
        )
        return default_environment_id

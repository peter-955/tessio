from collections.abc import Collection
from uuid import UUID

from sqlalchemy import func, select

from app.modules.files.infrastructure import StoredFileTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.story_context.domains.context_case.entity import ContextCase
from app.modules.story_context.domains.context_criterion.entity import ContextCriterion
from app.modules.story_context.domains.context_environment.entity import ContextEnvironment
from app.modules.story_context.domains.context_file.entity import ContextFile
from app.modules.story_context.domains.context_story.entity import ContextStory
from app.modules.story_context.domains.data_entry.entity import DataEntry
from app.modules.story_context.ports.story_context_reader import StoryContextReader
from app.modules.story_context.typing.constants import CASE_CODE_PREFIX
from app.modules.test_cases import TestCaseStatus, TestCaseVersion
from app.modules.test_cases.infrastructure import (
    TestCaseTable,
    TestCaseVersionTable,
    TestFileTable,
    TestFileVersionTable,
)
from app.modules.test_data import DataItemKind
from app.modules.test_data.infrastructure import DataItemTable, EnvironmentTable
from app.shared.postgres import Database

OTHER_CASE_STATUSES = (TestCaseStatus.DRAFT, TestCaseStatus.IN_REVIEW)


class PostgresStoryContextReader(StoryContextReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_story(self, project_id: UUID, jira_key: str) -> ContextStory | None:
        result = await self._database.get_current_session().execute(
            select(
                StoryTable.id, StoryTable.jira_key, StoryTable.title, StoryTable.jira_status, StoryTable.test_status
            ).where(StoryTable.project_id == project_id, StoryTable.jira_key == jira_key.strip().upper())
        )
        row = result.one_or_none()
        if row is None:
            return None
        story_id, story_jira_key, title, jira_status, test_status = row
        return ContextStory(
            id=story_id, jira_key=story_jira_key, title=title, jira_status=jira_status, test_status=test_status
        )

    async def list_criteria(self, story_id: UUID) -> list[ContextCriterion]:
        result = await self._database.get_current_session().execute(
            select(
                AcceptanceCriterionTable.id,
                AcceptanceCriterionTable.code,
                AcceptanceCriterionTable.text,
                AcceptanceCriterionTable.removed_at,
            )
            .where(AcceptanceCriterionTable.story_id == story_id)
            .order_by(AcceptanceCriterionTable.position)
        )
        return [
            ContextCriterion(id=criterion_id, code=code, text=text, is_removed=removed_at is not None)
            for criterion_id, code, text, removed_at in result
        ]

    async def list_ready_cases(self, story_id: UUID) -> list[ContextCase]:
        result = await self._database.get_current_session().execute(
            select(TestCaseTable.number, TestCaseVersionTable)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .where(TestCaseTable.story_id == story_id, TestCaseTable.status == TestCaseStatus.READY)
            .order_by(TestCaseTable.number)
            .execution_options(populate_existing=True)
        )
        numbered_versions = [(number, TestCaseVersion.model_validate(row)) for number, row in result]
        files_by_version_id = await self._map_files(
            {file_version_id for _, version in numbered_versions for file_version_id in version.file_version_ids}
        )
        return [
            ContextCase(
                id=version.test_case_id,
                code=f"{CASE_CODE_PREFIX}{number}",
                title=version.title,
                priority=version.priority,
                version_number=version.number,
                business_value=version.business_value,
                preconditions=version.preconditions,
                steps=version.steps,
                criterion_ids=version.criterion_ids,
                data_keys=version.data_keys,
                files=sorted(
                    (
                        files_by_version_id[file_version_id]
                        for file_version_id in version.file_version_ids
                        if file_version_id in files_by_version_id
                    ),
                    key=lambda file: file.key,
                ),
            )
            for number, version in numbered_versions
        ]

    async def count_other_cases(self, story_id: UUID) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(TestCaseTable)
            .where(TestCaseTable.story_id == story_id, TestCaseTable.status.in_(OTHER_CASE_STATUSES))
        )
        return int(count or 0)

    async def list_data_entries(self, project_id: UUID) -> list[DataEntry]:
        result = await self._database.get_current_session().execute(
            select(
                DataItemTable.id,
                DataItemTable.key,
                DataItemTable.kind,
                DataItemTable.value,
                DataItemTable.environment_id,
            )
            .where(DataItemTable.project_id == project_id)
            .order_by(DataItemTable.key, DataItemTable.environment_id.nulls_first())
        )
        return [
            DataEntry(
                id=item_id,
                key=key,
                kind=kind,
                value=None if kind == DataItemKind.SECRET else value,
                environment_id=environment_id,
            )
            for item_id, key, kind, value, environment_id in result
        ]

    async def list_environments(self, project_id: UUID) -> list[ContextEnvironment]:
        result = await self._database.get_current_session().execute(
            select(
                EnvironmentTable.id,
                EnvironmentTable.name,
                EnvironmentTable.base_url,
                EnvironmentTable.health_check_url,
                ProjectTable.default_environment_id,
            )
            .join(ProjectTable, ProjectTable.id == EnvironmentTable.project_id)
            .where(EnvironmentTable.project_id == project_id, EnvironmentTable.archived_at.is_(None))
            .order_by(EnvironmentTable.name)
        )
        return [
            ContextEnvironment(
                id=environment_id,
                name=name,
                base_url=base_url,
                health_check_url=health_check_url,
                is_default=environment_id == default_environment_id,
            )
            for environment_id, name, base_url, health_check_url, default_environment_id in result
        ]

    async def _map_files(self, file_version_ids: Collection[UUID]) -> dict[UUID, ContextFile]:
        if not file_version_ids:
            return {}
        result = await self._database.get_current_session().execute(
            select(TestFileVersionTable.id, TestFileTable.key, StoredFileTable.file_name)
            .join(TestFileTable, TestFileTable.id == TestFileVersionTable.test_file_id)
            .join(StoredFileTable, StoredFileTable.id == TestFileVersionTable.stored_file_id)
            .where(TestFileVersionTable.id.in_(file_version_ids))
        )
        return {
            file_version_id: ContextFile(key=key, file_name=file_name) for file_version_id, key, file_name in result
        }

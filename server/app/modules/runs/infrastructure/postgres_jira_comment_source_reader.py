from uuid import UUID

from sqlalchemy import select

from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.domains.jira_comment_source.entity import JiraCommentSource
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.ports.jira_comment_source_reader import JiraCommentSourceReader
from app.modules.runs.typing.enums import RunStatus
from app.modules.stories import StorySource
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_data.infrastructure import EnvironmentTable
from app.shared.postgres import Database


class PostgresJiraCommentSourceReader(JiraCommentSourceReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID, story_id: UUID, run_id: UUID | None) -> JiraCommentSource | None:
        session = self._database.get_current_session()
        story_row = (
            await session.execute(
                select(
                    StoryTable.jira_key,
                    StoryTable.title,
                    StoryTable.source,
                    ProjectTable.key,
                    ProjectTable.jira_project_key,
                )
                .join(ProjectTable, ProjectTable.id == StoryTable.project_id)
                .where(StoryTable.id == story_id, StoryTable.project_id == project_id)
            )
        ).one_or_none()
        if story_row is None:
            return None
        run_statement = (
            select(RunTable, EnvironmentTable.name)
            .join(EnvironmentTable, EnvironmentTable.id == RunTable.environment_id)
            .where(RunTable.project_id == project_id)
        )
        if run_id is None:
            run_statement = (
                run_statement.where(
                    RunTable.story_id == story_id,
                    RunTable.status.in_((RunStatus.PASSED, RunStatus.FAILED)),
                    RunTable.finished_at.is_not(None),
                )
                .order_by(RunTable.finished_at.desc(), RunTable.id.desc())
                .limit(1)
            )
        else:
            run_statement = run_statement.where(RunTable.id == run_id)
        run_row = (await session.execute(run_statement)).one_or_none()
        jira_key, title, source, project_key, jira_project_key = story_row
        run = None if run_row is None else run_row[0]
        return JiraCommentSource(
            project_key=project_key,
            is_project_linked=jira_project_key is not None,
            story_jira_key=jira_key,
            story_title=title,
            is_story_from_jira=source is StorySource.JIRA,
            run_id=None if run is None else run.id,
            run_status=None if run is None else run.status,
            environment_name=None if run_row is None else run_row[1],
            counts=None if run is None else self._find_counts(run, story_id),
        )

    @staticmethod
    def _find_counts(run: RunTable, story_id: UUID) -> RunCounts | None:
        if run.report is None:
            return None
        report = RunReport.model_validate(run.report)
        if run.story_id == story_id:
            return report.counts
        return next((story.counts for story in report.stories if story.story_id == story_id), None)

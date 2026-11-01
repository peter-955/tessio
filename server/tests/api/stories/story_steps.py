from datetime import UTC, datetime, timedelta
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import delete, insert, select, update

from app.container import Container
from app.modules.jira import JiraIssue, JiraSprint, JiraSprintState
from app.modules.jira.infrastructure import JiraConnectionTable
from app.modules.projects.infrastructure import ProjectTable
from app.modules.stories import SyncJiraProjectJobHandler
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import (
    AcceptanceCriterionTable,
    ProjectSyncStateTable,
    SprintTable,
    StoryTable,
)
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.modules.stories.utils.sprint_issues_jql import build_sprint_issues_jql
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.test_data.project_steps import SeededProject
from tests.fakes.fake_jira_client import FakeJiraClient

JIRA_SITE_URL = "https://team.atlassian.net"
JIRA_API_TOKEN = b"jira-api-token"
BOARD_ID = 1


async def seed_jira_connection(container: Container, configured_by: UUID) -> None:
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(delete(JiraConnectionTable))
        await session.execute(
            insert(JiraConnectionTable).values(
                id=1,
                site_url=JIRA_SITE_URL,
                account_email="jira-bot@example.com",
                api_token_encrypted=container.secret_cipher.encrypt(JIRA_API_TOKEN),
                account_id="acc-1",
                account_display_name="Jira Bot",
                configured_by=configured_by,
                configured_at=datetime.now(UTC),
            )
        )


async def clear_jira_connection(container: Container) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(delete(JiraConnectionTable))


def build_sprint(
    sprint_id: int,
    state: JiraSprintState = JiraSprintState.ACTIVE,
    name: str | None = None,
    start_at: datetime | None = None,
    complete_at: datetime | None = None,
) -> JiraSprint:
    return JiraSprint(
        id=sprint_id,
        name=name or f"Sprint {sprint_id}",
        state=state,
        start_at=start_at,
        end_at=None,
        complete_at=complete_at,
    )


def build_closed_sprint(sprint_id: int, closed_days_ago: int, name: str | None = None) -> JiraSprint:
    return build_sprint(
        sprint_id,
        JiraSprintState.CLOSED,
        name=name,
        complete_at=datetime.now(UTC) - timedelta(days=closed_days_ago),
    )


def build_list_item(text: str) -> JsonValue:
    return {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]}


def build_description(criteria: list[str]) -> JsonValue:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Story context."}]},
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "Acceptance criteria"}]},
            {"type": "bulletList", "content": [build_list_item(text) for text in criteria]},
        ],
    }


def build_issue(
    jira_project_key: str,
    number: int,
    criteria: list[str] | None = None,
    summary: str | None = None,
    issue_type_name: str = "Story",
    is_subtask: bool = False,
) -> JiraIssue:
    return JiraIssue(
        id=str(10000 + number),
        key=f"{jira_project_key}-{number}",
        summary=summary or f"Story {number}",
        description=build_description(criteria or []),
        status_name="In Progress",
        issue_type_name=issue_type_name,
        is_subtask=is_subtask,
        updated_at=datetime(2026, 10, 30, 9, tzinfo=UTC),
    )


def set_board(
    fake_jira_client: FakeJiraClient,
    project: SeededProject,
    issues_by_sprint: dict[JiraSprint, list[JiraIssue]],
    board_id: int = BOARD_ID,
) -> None:
    fake_jira_client.sprints_by_board_id[board_id] = list(issues_by_sprint)
    for jira_sprint, issues in issues_by_sprint.items():
        fake_jira_client.issues_by_jql[build_sprint_issues_jql(project.key, jira_sprint.id)] = issues


async def set_project_board_id(container: Container, project: SeededProject, board_id: int) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(jira_board_id=board_id)
        )


async def detach_story_from_sprint(container: Container, project: SeededProject, jira_key: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable)
            .where(StoryTable.project_id == project.id, StoryTable.jira_key == jira_key)
            .values(sprint_id=None)
        )


async def run_sync(container: StoriesTestContainer, project_id: UUID) -> None:
    await SyncJiraProjectJobHandler(container.sync_jira_project).handle({"projectId": str(project_id)})


async def set_test_status(
    container: Container, project: SeededProject, jira_key: str, test_status: StoryTestStatus
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable)
            .where(StoryTable.project_id == project.id, StoryTable.jira_key == jira_key)
            .values(test_status=test_status)
        )


async def set_sync_state(
    container: Container, project: SeededProject, status: ProjectSyncStatus, queued_at: datetime
) -> None:
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(delete(ProjectSyncStateTable).where(ProjectSyncStateTable.project_id == project.id))
        await session.execute(
            insert(ProjectSyncStateTable).values(
                project_id=project.id, status=status, queued_at=queued_at, created_at=queued_at
            )
        )


async def find_story_row(container: Container, project: SeededProject, jira_key: str) -> StoryTable | None:
    async with container.database.begin():
        row: StoryTable | None = await container.database.get_current_session().scalar(
            select(StoryTable).where(StoryTable.project_id == project.id, StoryTable.jira_key == jira_key)
        )
        return row


async def list_criterion_rows(container: Container, story_id: UUID) -> list[AcceptanceCriterionTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.story_id == story_id)
            .order_by(AcceptanceCriterionTable.position)
        )
        return list(rows)


async def list_sprint_rows(container: Container, project: SeededProject) -> list[SprintTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(SprintTable).where(SprintTable.project_id == project.id).order_by(SprintTable.jira_sprint_id)
        )
        return list(rows)

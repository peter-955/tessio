from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import count
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import Integer, Text, Uuid, column, insert, select, table, update
from sqlalchemy.dialects.postgresql import ARRAY

from app.container import Container
from app.modules.gaps.infrastructure import GapTable
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.users import UserStatus, WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import SignedUpAccount, create_invited_user, sign_up_as
from tests.api.test_data.project_steps import SeededProject, add_member
from tests.conftest import RecordingMailer

DEFAULT_QUESTION = "Which currencies does checkout accept?"
STORY_NUMBERS = count(1)
TEST_CASE_ROWS = table(
    "test_cases",
    column("id", Uuid()),
    column("project_id", Uuid()),
    column("story_id", Uuid()),
    column("number", Integer()),
    column("title", Text()),
    column("priority", Text()),
    column("status", Text()),
    column("needs_review_criterion_ids", ARRAY(Uuid())),
    column("created_by", Uuid()),
    column("created_at"),
)


@dataclass(frozen=True)
class SeededStory:
    id: UUID
    jira_key: str
    criterion_ids: dict[str, UUID]


async def seed_story(
    container: Container, project: SeededProject, jira_key: str | None = None, criterion_codes: tuple[str, ...] = ()
) -> SeededStory:
    story_id = uuid7()
    story_jira_key = jira_key or f"{project.key}-{next(STORY_NUMBERS)}"
    now = datetime.now(UTC)
    criterion_ids = {code: uuid7() for code in criterion_codes}
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(StoryTable).values(
                id=story_id,
                project_id=project.id,
                sprint_id=None,
                jira_id=str(uuid4()),
                jira_key=story_jira_key,
                jira_url=f"https://team.atlassian.net/browse/{story_jira_key}",
                title=f"Story {story_jira_key}",
                description=None,
                jira_status="In Progress",
                jira_issue_type="Story",
                test_status=StoryTestStatus.NOT_STARTED,
                jira_updated_at=now,
                synced_at=now,
                created_at=now,
            )
        )
        for position, (code, criterion_id) in enumerate(criterion_ids.items(), start=1):
            await session.execute(
                insert(AcceptanceCriterionTable).values(
                    id=criterion_id,
                    story_id=story_id,
                    position=position,
                    code=code,
                    text=f"Criterion {code}",
                    removed_at=None,
                    created_at=now,
                )
            )
    return SeededStory(id=story_id, jira_key=story_jira_key, criterion_ids=criterion_ids)


async def remove_criterion(container: Container, criterion_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.id == criterion_id)
            .values(removed_at=datetime.now(UTC))
        )


async def seed_test_case(
    container: Container, project: SeededProject, story_id: UUID, number: int, created_by: UUID
) -> UUID:
    test_case_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(TEST_CASE_ROWS).values(
                id=test_case_id,
                project_id=project.id,
                story_id=story_id,
                number=number,
                title=f"Case {number}",
                priority="medium",
                status="draft",
                needs_review_criterion_ids=[],
                created_by=created_by,
                created_at=datetime.now(UTC),
            )
        )
    return test_case_id


async def add_active_member(
    container: Container, recording_mailer: RecordingMailer, project: SeededProject, role: ProjectRole, name: str
) -> UUID:
    user_id = await create_invited_user(container, recording_mailer, name)
    async with container.database.begin():
        user = await container.user_repository.find_by_id(user_id)
        assert user is not None
        await container.user_repository.update(user, user.model_copy(update={"status": UserStatus.ACTIVE}))
    await add_member(container, project, user_id, role)
    return user_id


async def add_invited_member(
    container: Container, recording_mailer: RecordingMailer, project: SeededProject, role: ProjectRole
) -> UUID:
    user_id = await create_invited_user(container, recording_mailer)
    await add_member(container, project, user_id, role)
    return user_id


async def raise_gap(client: AsyncClient, project_key: str, story: SeededStory, **body: object) -> Response:
    return await client.post(
        f"/api/projects/{project_key}/stories/{story.jira_key}/gaps",
        json={"type": "missing_ac", "question": DEFAULT_QUESTION, **body},
    )


async def raise_gap_id(client: AsyncClient, project_key: str, story: SeededStory, **body: object) -> str:
    response = await raise_gap(client, project_key, story, **body)
    assert response.status_code == 201, response.text
    gap_id: str = response.json()["id"]
    return gap_id


async def answer_gap(client: AsyncClient, project_key: str, gap_id: str, answer: str = "EUR and USD.") -> Response:
    return await client.put(f"/api/projects/{project_key}/gaps/{gap_id}/answer", json={"answer": answer})


async def reopen_gap(client: AsyncClient, project_key: str, gap_id: str) -> Response:
    return await client.post(f"/api/projects/{project_key}/gaps/{gap_id}/reopen")


async def reassign_gap(client: AsyncClient, project_key: str, gap_id: str, **body: object) -> Response:
    return await client.put(f"/api/projects/{project_key}/gaps/{gap_id}/assignee", json=body)


async def find_gap_row(container: Container, gap_id: str) -> GapTable:
    async with container.database.begin():
        row = await container.database.get_current_session().scalar(select(GapTable).where(GapTable.id == UUID(gap_id)))
    assert row is not None
    return row


async def list_notified_user_ids(container: Container, project: SeededProject, gap_id: str) -> list[UUID]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.project_id == project.id).order_by(NotificationTable.id)
        )
        return [row.user_id for row in rows if row.payload.get("gap_id") == gap_id]


def read_tool_error(response: Response) -> str:
    result = response.json()["result"]
    assert result["isError"] is True
    text: str = result["content"][0]["text"]
    return text


async def sign_up_account(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole,
    name: str = "Test User",
) -> SignedUpAccount:
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, name)
    await add_member(container, project, account.user_id, role)
    return account

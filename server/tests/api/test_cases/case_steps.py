from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from uuid import UUID, uuid7

from httpx import AsyncClient, Response
from openpyxl import Workbook
from pydantic import JsonValue
from sqlalchemy import insert, update

from app.container import Container
from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import AcceptanceCriterionTable, StoryTable
from app.modules.test_data import DataItemKind
from app.modules.test_data.infrastructure import DataItemTable
from app.shared.permissions import ProjectRole
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer


@dataclass(frozen=True)
class SeededStory:
    id: UUID
    jira_key: str
    criterion_ids: list[UUID]


@dataclass(frozen=True)
class CaseProject:
    project: SeededProject
    story: SeededStory
    user_id: UUID

    @property
    def key(self) -> str:
        return self.project.key


async def seed_story(
    container: Container, project: SeededProject, jira_key: str, criteria_texts: list[str] | None = None
) -> SeededStory:
    story_id = uuid7()
    now = datetime.now(UTC)
    criterion_ids = [uuid7() for _ in criteria_texts or []]
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(StoryTable).values(
                id=story_id,
                project_id=project.id,
                sprint_id=None,
                jira_id=f"id-{jira_key}",
                jira_key=jira_key,
                jira_url=f"https://team.atlassian.net/browse/{jira_key}",
                title=f"Story {jira_key}",
                description=None,
                jira_status="In Progress",
                jira_issue_type="Story",
                test_status=StoryTestStatus.NOT_STARTED,
                jira_updated_at=now,
                synced_at=now,
                created_at=now,
            )
        )
        for position, (criterion_id, text) in enumerate(zip(criterion_ids, criteria_texts or [], strict=True), 1):
            await session.execute(
                insert(AcceptanceCriterionTable).values(
                    id=criterion_id,
                    story_id=story_id,
                    position=position,
                    code=f"AC{position}",
                    text=text,
                    created_at=now,
                )
            )
    return SeededStory(id=story_id, jira_key=jira_key, criterion_ids=criterion_ids)


async def remove_criterion(container: Container, criterion_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.id == criterion_id)
            .values(removed_at=datetime.now(UTC))
        )


async def seed_data_item(
    container: Container, project: SeededProject, key: str, environment_id: UUID | None = None
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(DataItemTable).values(
                id=uuid7(),
                project_id=project.id,
                environment_id=environment_id,
                key=key,
                kind=DataItemKind.VARIABLE,
                value="value",
                value_encrypted=None,
                created_at=datetime.now(UTC),
            )
        )


async def seed_test_file_upload(
    container: Container,
    project: SeededProject,
    user_id: UUID,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    kind: StoredFileKind = StoredFileKind.TEST_FILE,
    file_name: str = "invoice.pdf",
) -> UUID:
    file_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(StoredFileTable).values(
                id=file_id,
                project_id=project.id,
                kind=kind,
                object_key=f"projects/{project.id}/{kind.value}/{file_id}/{file_name}",
                file_name=file_name,
                content_type="application/pdf",
                size=1024 if status is StoredFileStatus.UPLOADED else None,
                sha256=None,
                status=status,
                uploaded_by=user_id,
                created_at=datetime.now(UTC),
            )
        )
    return file_id


def build_xlsx(sheets: dict[str, list[list[str | None]]]) -> bytes:
    workbook = Workbook()
    default_sheet = workbook.active
    if default_sheet is not None:
        workbook.remove(default_sheet)
    for title, rows in sheets.items():
        worksheet = workbook.create_sheet(title)
        for row in rows:
            worksheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def build_step(action: str, expected: str | None = None) -> JsonValue:
    return {"action": action, "expected": expected}


async def create_case(client: AsyncClient, project_key: str, story_key: str, **fields: JsonValue) -> Response:
    return await client.post(
        f"/api/projects/{project_key}/test-cases", json={"storyKey": story_key, "title": "Pay by card", **fields}
    )


async def create_case_code(client: AsyncClient, project_key: str, story_key: str, **fields: JsonValue) -> str:
    response = await create_case(client, project_key, story_key, **fields)
    assert response.status_code == 201, response.text
    code: str = response.json()["code"]
    return code


async def update_case(
    client: AsyncClient, project_key: str, case_code: str, base_version_number: int, **fields: JsonValue
) -> Response:
    return await client.patch(
        f"/api/projects/{project_key}/test-cases/{case_code}",
        json={"baseVersionNumber": base_version_number, **fields},
    )


async def change_status(client: AsyncClient, project_key: str, case_code: str, status: str) -> Response:
    return await client.put(f"/api/projects/{project_key}/test-cases/{case_code}/status", json={"status": status})


async def get_case(client: AsyncClient, project_key: str, case_code: str) -> Response:
    response = await client.get(f"/api/projects/{project_key}/test-cases/{case_code}")
    assert response.status_code == 200, response.text
    return response


async def set_up_case_project(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    criteria_texts: list[str] | None = None,
    role: ProjectRole = ProjectRole.QC,
) -> CaseProject:
    project = await seed_project(container)
    user_id = await sign_up_member(client, container, recording_mailer, project, role)
    story = await seed_story(container, project, f"{project.key}-1", criteria_texts or ["Pay by card", "Get receipt"])
    return CaseProject(project=project, story=story, user_id=user_id)

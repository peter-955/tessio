from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import count
from uuid import UUID, uuid4, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import func, insert, select, update

from app.container import Container
from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.runs import RunExecutor, RunStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases import TestCasePriority, TestCaseStatus
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_data import DataItemKind
from app.modules.test_data.infrastructure import DataItemTable, EnvironmentTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as, use_session
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer

SECRET_KEY = "ADMIN_PASSWORD"
SECRET_VALUE = "s3cr3t-Passw0rd"
STEP_COUNT = 3
STORY_NUMBERS = count(1)


@dataclass(frozen=True)
class SeededCase:
    id: UUID
    version_id: UUID
    number: int


@dataclass(frozen=True)
class ManualRunProject:
    project: SeededProject
    story_id: UUID
    story_key: str
    environment_id: UUID
    cases: list[SeededCase]
    qc: SignedUpAccount

    @property
    def key(self) -> str:
        return self.project.key


async def seed_manual_run_project(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    case_statuses: tuple[TestCaseStatus, ...] = (TestCaseStatus.READY, TestCaseStatus.READY, TestCaseStatus.READY),
) -> ManualRunProject:
    project = await seed_project(container)
    qc = await sign_up_account(client, container, recording_mailer, project, ProjectRole.QC, "Quinn QC")
    story_id, story_key = await seed_story(container, project)
    cases = [
        await seed_case(container, project, story_id, number, qc.user_id, status)
        for number, status in enumerate(case_statuses, start=1)
    ]
    environment_id = await seed_environment(container, project)
    await seed_secret(container, project, environment_id, SECRET_KEY, SECRET_VALUE)
    use_session(client, qc.session_token)
    return ManualRunProject(
        project=project,
        story_id=story_id,
        story_key=story_key,
        environment_id=environment_id,
        cases=cases,
        qc=qc,
    )


async def sign_up_account(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole | None,
    name: str = "Test User",
) -> SignedUpAccount:
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, name)
    if role is not None:
        await add_member(container, project, account.user_id, role)
    return account


async def seed_story(container: Container, project: SeededProject) -> tuple[UUID, str]:
    story_id = uuid7()
    jira_key = f"{project.key}-{next(STORY_NUMBERS)}"
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(StoryTable).values(
                id=story_id,
                project_id=project.id,
                sprint_id=None,
                jira_id=str(uuid4()),
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
    return story_id, jira_key


async def seed_case(
    container: Container,
    project: SeededProject,
    story_id: UUID,
    number: int,
    created_by: UUID,
    status: TestCaseStatus,
) -> SeededCase:
    case_id = uuid7()
    version_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(TestCaseTable).values(
                id=case_id,
                project_id=project.id,
                story_id=story_id,
                number=number,
                title=f"Case {number}",
                priority=TestCasePriority.MEDIUM,
                status=status,
                current_version_id=None,
                needs_review_criterion_ids=[],
                created_by=created_by,
                created_at=now,
            )
        )
        await session.execute(
            insert(TestCaseVersionTable).values(
                id=version_id,
                test_case_id=case_id,
                number=1,
                title=f"Case {number}",
                priority=TestCasePriority.MEDIUM,
                business_value=None,
                preconditions="Signed in",
                steps=[
                    {"order": order, "action": f"Action {order}", "expected": f"Expected {order}"}
                    for order in range(1, STEP_COUNT + 1)
                ],
                criterion_ids=[],
                data_keys=[],
                file_version_ids=[],
                created_by=created_by,
                created_at=now,
            )
        )
        await session.execute(
            update(TestCaseTable).where(TestCaseTable.id == case_id).values(current_version_id=version_id)
        )
    return SeededCase(id=case_id, version_id=version_id, number=number)


async def change_case_status(container: Container, case_id: UUID, status: TestCaseStatus) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable).where(TestCaseTable.id == case_id).values(status=status)
        )


async def seed_environment(container: Container, project: SeededProject, name: str = "staging") -> UUID:
    environment_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(EnvironmentTable).values(
                id=environment_id,
                project_id=project.id,
                name=name,
                base_url=f"https://{name}.tessio.test",
                health_check_url=None,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
        )
    return environment_id


async def seed_secret(
    container: Container, project: SeededProject, environment_id: UUID | None, key: str, value: str
) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(DataItemTable).values(
                id=uuid7(),
                project_id=project.id,
                environment_id=environment_id,
                key=key,
                kind=DataItemKind.SECRET,
                value=None,
                value_encrypted=container.secret_cipher.encrypt(value.encode()),
                created_at=datetime.now(UTC),
            )
        )


async def seed_evidence_file(
    container: Container,
    project_id: UUID,
    uploaded_by: UUID,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    kind: StoredFileKind = StoredFileKind.EVIDENCE,
) -> UUID:
    file_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(StoredFileTable).values(
                id=file_id,
                project_id=project_id,
                kind=kind,
                object_key=f"projects/{project_id}/{kind.value}/{file_id}/evidence.png",
                file_name="evidence.png",
                content_type="image/png",
                size=2048 if status is StoredFileStatus.UPLOADED else None,
                sha256=None,
                status=status,
                uploaded_by=uploaded_by,
                created_at=datetime.now(UTC),
            )
        )
    return file_id


async def seed_claude_run(container: Container, seeded: ManualRunProject) -> UUID:
    run_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(RunTable).values(
                id=run_id,
                project_id=seeded.project.id,
                story_id=seeded.story_id,
                environment_id=seeded.environment_id,
                executor=RunExecutor.CLAUDE,
                status=RunStatus.RUNNING,
                abort_reason=None,
                parent_run_id=None,
                started_by=seeded.qc.user_id,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=now,
                last_activity_at=now,
                finished_at=None,
                created_at=now,
            )
        )
    return run_id


async def find_run_row(container: Container, run_id: str | UUID) -> RunTable:
    async with container.database.begin():
        row = await container.database.get_current_session().scalar(
            select(RunTable).where(RunTable.id == UUID(str(run_id)))
        )
    assert row is not None
    return row


async def count_case_results(container: Container, run_id: str | UUID) -> int:
    async with container.database.begin():
        count = await container.database.get_current_session().scalar(
            select(func.count()).select_from(CaseResultTable).where(CaseResultTable.run_id == UUID(str(run_id)))
        )
    return int(count or 0)


async def count_child_runs(container: Container, run_id: str | UUID) -> int:
    async with container.database.begin():
        count = await container.database.get_current_session().scalar(
            select(func.count()).select_from(RunTable).where(RunTable.parent_run_id == UUID(str(run_id)))
        )
    return int(count or 0)


async def move_last_activity_back(container: Container, run_id: str | UUID, idle_time: timedelta) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunTable)
            .where(RunTable.id == UUID(str(run_id)))
            .values(last_activity_at=datetime.now(UTC) - idle_time)
        )


async def find_story_test_status(container: Container, story_id: UUID) -> StoryTestStatus:
    async with container.database.begin():
        test_status = await container.database.get_current_session().scalar(
            select(StoryTable.test_status).where(StoryTable.id == story_id)
        )
    assert test_status is not None
    return test_status


async def list_run_notifications(container: Container, project: SeededProject, run_id: str) -> list[NotificationTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.project_id == project.id).order_by(NotificationTable.id)
        )
        return [row for row in rows if row.payload.get("run_id") == run_id]


def build_step(order: int, status: str, **fields: object) -> dict[str, object]:
    return {"order": order, "status": status, **fields}


async def start_manual_run(client: AsyncClient, seeded: ManualRunProject, **body: object) -> Response:
    return await client.post(f"/api/projects/{seeded.key}/runs", json={"storyKey": seeded.story_key, **body})


async def start_manual_run_id(client: AsyncClient, seeded: ManualRunProject, **body: object) -> str:
    response = await start_manual_run(client, seeded, **body)
    assert response.status_code == 201, response.text
    run_id: str = response.json()["id"]
    return run_id


async def record_case(client: AsyncClient, project_key: str, run_id: str, case_id: UUID, **body: object) -> Response:
    return await client.put(f"/api/projects/{project_key}/runs/{run_id}/cases/{case_id}", json=body)


async def record_case_status(
    client: AsyncClient, project_key: str, run_id: str, case_id: UUID, status: str
) -> Response:
    response = await record_case(
        client, project_key, run_id, case_id, steps=[build_step(order, status) for order in range(1, STEP_COUNT + 1)]
    )
    assert response.status_code == 200, response.text
    return response


async def finish_manual_run(client: AsyncClient, project_key: str, run_id: str, **body: object) -> Response:
    return await client.post(f"/api/projects/{project_key}/runs/{run_id}/finish", json=body)


async def rerun_failed_cases(client: AsyncClient, project_key: str, run_id: str, **body: object) -> Response:
    return await client.post(f"/api/projects/{project_key}/runs/{run_id}/rerun-failed", json=body or None)

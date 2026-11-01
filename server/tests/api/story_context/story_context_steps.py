from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from httpx import AsyncClient
from pydantic import JsonValue
from sqlalchemy import delete, func, insert, select, update

from app.container import Container
from app.modules.audit.infrastructure import AuditEventTable
from app.modules.files import StoredFileKind
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs.infrastructure import RunCaseTable, RunFileTable, RunTable
from app.modules.runs.typing.enums import RunExecutor, RunStatus
from app.modules.test_data.infrastructure import DataItemTable, EnvironmentTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as, use_session
from tests.api.test_cases.case_steps import (
    SeededStory,
    build_step,
    change_status,
    create_case,
    get_case,
    seed_story,
    seed_test_file_upload,
)
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer

PROJECT_EMAIL = "a@shop.test"
STAGING_EMAIL = "s@shop.test"
ARCHIVED_EMAIL = "old@shop.test"
PROJECT_PASSWORD = "project-password-plaintext"
STAGING_PASSWORD = "staging-password-plaintext"
API_KEY = "api-key-plaintext"


@dataclass(frozen=True)
class TokenHolder:
    account: SignedUpAccount
    token: str

    @property
    def user_id(self) -> UUID:
        return self.account.user_id


@dataclass(frozen=True)
class ContextProject:
    project: SeededProject
    story: SeededStory
    author: SignedUpAccount
    staging_id: UUID
    production_id: UUID
    archived_environment_id: UUID
    data_item_ids: dict[str, UUID]

    @property
    def key(self) -> str:
        return self.project.key


@dataclass(frozen=True)
class CreatedCase:
    code: str
    file_ids: dict[str, UUID]


@dataclass(frozen=True)
class ReadyCase:
    id: UUID
    code: str
    version_id: UUID
    version_number: int


async def sign_up_author(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> SignedUpAccount:
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Quinn Author")
    await add_member(container, project, account.user_id, ProjectRole.QC)
    return account


async def set_up_context_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> ContextProject:
    project = await seed_project(container)
    author = await sign_up_author(client, container, recording_mailer, project)
    story = await seed_story(container, project, f"{project.key}-12", ["Pay by card", "Get a receipt", "Old rule"])
    staging_id = UUID(await create_environment(client, project, "Staging", "https://staging.shop.test"))
    production_id = UUID(
        await create_environment(client, project, "Production", "https://shop.test", "https://shop.test/health")
    )
    archived_environment_id = UUID(await create_environment(client, project, "Legacy", "https://legacy.shop.test"))
    data_item_ids = {
        "user_email": UUID(await create_data_item(client, project, "user_email", PROJECT_EMAIL)),
        "user_email@staging": UUID(
            await create_data_item(client, project, "user_email", STAGING_EMAIL, environment_id=str(staging_id))
        ),
        "user_email@legacy": UUID(
            await create_data_item(
                client, project, "user_email", ARCHIVED_EMAIL, environment_id=str(archived_environment_id)
            )
        ),
        "user_password": UUID(await create_data_item(client, project, "user_password", PROJECT_PASSWORD, "secret")),
        "user_password@staging": UUID(
            await create_data_item(
                client, project, "user_password", STAGING_PASSWORD, "secret", environment_id=str(staging_id)
            )
        ),
        "api_key": UUID(await create_data_item(client, project, "api_key", API_KEY, "secret")),
        "coupon": UUID(await create_data_item(client, project, "coupon", "SAVE10")),
    }
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(default_environment_id=staging_id)
        )
        await session.execute(
            update(EnvironmentTable)
            .where(EnvironmentTable.id == archived_environment_id)
            .values(archived_at=datetime.now(UTC))
        )
    return ContextProject(
        project=project,
        story=story,
        author=author,
        staging_id=staging_id,
        production_id=production_id,
        archived_environment_id=archived_environment_id,
        data_item_ids=data_item_ids,
    )


async def attach_file(
    client: AsyncClient,
    container: Container,
    context_project: ContextProject,
    case_code: str,
    key: str,
    file_name: str,
) -> UUID:
    use_session(client, context_project.author.session_token)
    file_id = await seed_test_file_upload(
        container, context_project.project, context_project.author.user_id, file_name=file_name
    )
    case = await get_case(client, context_project.key, case_code)
    response = await client.post(
        f"/api/projects/{context_project.key}/test-cases/{case_code}/files",
        json={"key": key, "fileId": str(file_id), "baseVersionNumber": case.json()["currentVersion"]["number"]},
    )
    assert response.status_code == 201, response.text
    return file_id


async def create_ready_case(
    client: AsyncClient,
    container: Container,
    context_project: ContextProject,
    steps: list[JsonValue],
    file_keys: tuple[str, ...] = (),
    **fields: JsonValue,
) -> CreatedCase:
    use_session(client, context_project.author.session_token)
    response = await create_case(client, context_project.key, context_project.story.jira_key, steps=steps, **fields)
    assert response.status_code == 201, response.text
    code: str = response.json()["code"]
    file_ids = {
        key: await attach_file(client, container, context_project, code, key, f"{key}.pdf") for key in file_keys
    }
    for status in ("in_review", "ready"):
        changed = await change_status(client, context_project.key, code, status)
        assert changed.status_code == 200, changed.text
    return CreatedCase(code=code, file_ids=file_ids)


async def find_ready_case(client: AsyncClient, context_project: ContextProject, code: str) -> ReadyCase:
    use_session(client, context_project.author.session_token)
    body = (await get_case(client, context_project.key, code)).json()
    return ReadyCase(
        id=UUID(body["id"]),
        code=code,
        version_id=UUID(body["currentVersion"]["id"]),
        version_number=body["currentVersion"]["number"],
    )


def build_file_url(project: SeededProject, file_id: UUID, file_name: str) -> str:
    return f"https://storage.test/tessio/projects/{project.id}/{StoredFileKind.TEST_FILE.value}/{file_id}/{file_name}"


def build_login_steps() -> list[JsonValue]:
    return [
        build_step("Sign in as {{data.user_email}} with {{data.user_password}}", "The account page opens"),
        build_step("Upload {{file.invoice}}"),
    ]


async def add_token_holder(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole,
    name: str = "Claude Owner",
) -> TokenHolder:
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, name)
    await add_member(container, project, account.user_id, role)
    token = await create_token(client, project.key)
    return TokenHolder(account=account, token=token)


async def seed_run(
    container: Container,
    project: SeededProject,
    story_id: UUID,
    environment_id: UUID,
    started_by: UUID,
    cases: list[tuple[UUID, UUID]],
    status: RunStatus = RunStatus.RUNNING,
) -> UUID:
    run_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(RunTable).values(
                id=run_id,
                project_id=project.id,
                story_id=story_id,
                environment_id=environment_id,
                executor=RunExecutor.CLAUDE,
                status=status,
                abort_reason=None,
                parent_run_id=None,
                started_by=started_by,
                started_via_token_id=None,
                summary=None,
                report=None,
                started_at=now,
                last_activity_at=now,
                finished_at=None if status is RunStatus.RUNNING else now,
                created_at=now,
            )
        )
        for position, (test_case_id, test_case_version_id) in enumerate(cases, start=1):
            await session.execute(
                insert(RunCaseTable).values(
                    id=uuid7(),
                    run_id=run_id,
                    test_case_id=test_case_id,
                    test_case_version_id=test_case_version_id,
                    position=position,
                    created_at=now,
                )
            )
    return run_id


async def seed_environment(container: Container, project: SeededProject, name: str = "Staging") -> UUID:
    environment_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(EnvironmentTable).values(
                id=environment_id,
                project_id=project.id,
                name=name,
                base_url="https://other.shop.test",
                health_check_url=None,
                archived_at=None,
                created_at=datetime.now(UTC),
            )
        )
    return environment_id


async def seed_story_run(
    container: Container,
    context_project: ContextProject,
    started_by: UUID,
    cases: list[ReadyCase],
    status: RunStatus = RunStatus.RUNNING,
) -> UUID:
    return await seed_run(
        container,
        context_project.project,
        context_project.story.id,
        context_project.staging_id,
        started_by,
        [(case.id, case.version_id) for case in cases],
        status,
    )


async def delete_data_item(container: Container, item_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(delete(DataItemTable).where(DataItemTable.id == item_id))


async def find_audit_rows(container: Container, run_id: UUID) -> list[AuditEventTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(AuditEventTable).where(AuditEventTable.run_id == run_id).order_by(AuditEventTable.id)
        )
        return list(rows)


async def count_run_files(container: Container, run_id: UUID) -> int:
    async with container.database.begin():
        count = await container.database.get_current_session().scalar(
            select(func.count()).select_from(RunFileTable).where(RunFileTable.run_id == run_id)
        )
    return int(count or 0)


async def find_run_files(container: Container, run_id: UUID) -> list[RunFileTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(RunFileTable).where(RunFileTable.run_id == run_id)
        )
        return list(rows)

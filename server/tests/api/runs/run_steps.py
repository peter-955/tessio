import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

from httpx import AsyncClient, Response
from sqlalchemy import func, insert, select, update

from app.container import Container
from app.modules.projects.infrastructure import ProjectTable
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.modules.test_data import DataItemKind
from app.modules.test_data.infrastructure import DataItemTable, EnvironmentTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import seed_story
from tests.api.projects.user_steps import SignedUpAccount, sign_up_as
from tests.api.test_data.project_steps import SeededProject, add_member
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

TOOL_ERROR_PREFIX = re.compile(r"^Error executing tool \w+: ")
DEFAULT_ENVIRONMENT_NAME = "Staging"


@dataclass(frozen=True)
class SeededRunnableStory:
    project: SeededProject
    story_id: UUID
    jira_key: str
    case_ids: list[UUID]
    environment_id: UUID


@dataclass(frozen=True)
class Runner:
    account: SignedUpAccount
    token: str


async def sign_up_runner(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole = ProjectRole.QC,
    name: str = "Quinn Runner",
    workspace_role: WorkspaceRole = WorkspaceRole.MEMBER,
) -> Runner:
    account = await sign_up_as(client, container, recording_mailer, workspace_role, name)
    await add_member(container, project, account.user_id, role)
    token = await create_token(client, project.key)
    client.cookies.clear()
    return Runner(account=account, token=token)


async def seed_environment(
    container: Container,
    project: SeededProject,
    name: str = DEFAULT_ENVIRONMENT_NAME,
    is_archived: bool = False,
    is_default: bool = False,
) -> UUID:
    async with container.database.begin():
        session = container.database.get_current_session()
        environment_id = await session.scalar(
            select(EnvironmentTable.id).where(EnvironmentTable.project_id == project.id, EnvironmentTable.name == name)
        )
        if environment_id is None:
            environment_id = uuid7()
            now = datetime.now(UTC)
            await session.execute(
                insert(EnvironmentTable).values(
                    id=environment_id,
                    project_id=project.id,
                    name=name,
                    base_url=f"https://{name.lower()}.shop.test",
                    health_check_url=f"https://{name.lower()}.shop.test/health",
                    archived_at=now if is_archived else None,
                    created_at=now,
                )
            )
        if is_default:
            await session.execute(
                update(ProjectTable).where(ProjectTable.id == project.id).values(default_environment_id=environment_id)
            )
    return environment_id


async def seed_case(
    container: Container,
    project: SeededProject,
    story_id: UUID,
    created_by: UUID,
    step_count: int,
    status: str = "ready",
) -> UUID:
    test_case_id = uuid7()
    version_id = uuid7()
    now = datetime.now(UTC)
    async with container.database.begin():
        session = container.database.get_current_session()
        highest_number = await session.scalar(
            select(func.max(TestCaseTable.number)).where(TestCaseTable.project_id == project.id)
        )
        number = (highest_number or 0) + 1
        await session.execute(
            insert(TestCaseTable).values(
                id=test_case_id,
                project_id=project.id,
                story_id=story_id,
                number=number,
                title=f"Case {number}",
                priority="medium",
                status=status,
                current_version_id=None,
                needs_review_criterion_ids=[],
                created_by=created_by,
                created_at=now,
            )
        )
        await session.execute(
            insert(TestCaseVersionTable).values(
                build_version_values(version_id, test_case_id, 1, f"Case {number}", step_count, created_by, now)
            )
        )
        await session.execute(
            update(TestCaseTable).where(TestCaseTable.id == test_case_id).values(current_version_id=version_id)
        )
    return test_case_id


def build_version_values(
    version_id: UUID,
    test_case_id: UUID,
    version_number: int,
    title: str,
    step_count: int,
    created_by: UUID,
    now: datetime,
) -> dict[str, object]:
    return {
        "id": version_id,
        "test_case_id": test_case_id,
        "number": version_number,
        "title": title,
        "priority": "medium",
        "business_value": None,
        "preconditions": "Signed out",
        "steps": [
            {"order": order, "action": f"Action {order}", "expected": f"Expected {order}"}
            for order in range(1, step_count + 1)
        ],
        "criterion_ids": [],
        "data_keys": [],
        "file_version_ids": [],
        "created_by": created_by,
        "created_at": now,
    }


async def seed_runnable_story(
    container: Container,
    project: SeededProject,
    created_by: UUID,
    case_count: int = 2,
    step_count: int = 2,
    status: str = "ready",
    environment_name: str | None = DEFAULT_ENVIRONMENT_NAME,
) -> SeededRunnableStory:
    story = await seed_story(container, project)
    case_ids = [
        await seed_case(container, project, story.id, created_by, step_count, status) for _ in range(case_count)
    ]
    environment_id = (
        uuid7() if environment_name is None else await seed_environment(container, project, environment_name)
    )
    return SeededRunnableStory(
        project=project, story_id=story.id, jira_key=story.jira_key, case_ids=case_ids, environment_id=environment_id
    )


async def edit_case(container: Container, test_case_id: UUID, title: str, step_count: int, created_by: UUID) -> UUID:
    version_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        highest_number = await session.scalar(
            select(func.max(TestCaseVersionTable.number)).where(TestCaseVersionTable.test_case_id == test_case_id)
        )
        await session.execute(
            insert(TestCaseVersionTable).values(
                build_version_values(
                    version_id,
                    test_case_id,
                    (highest_number or 0) + 1,
                    title,
                    step_count,
                    created_by,
                    datetime.now(UTC),
                )
            )
        )
        await session.execute(
            update(TestCaseTable)
            .where(TestCaseTable.id == test_case_id)
            .values(current_version_id=version_id, title=title)
        )
    return version_id


async def change_case_status(container: Container, test_case_id: UUID, status: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseTable).where(TestCaseTable.id == test_case_id).values(status=status)
        )


async def seed_secret(
    container: Container, project: SeededProject, key: str, value: str, environment_id: UUID | None = None
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


def read_tool_error(response: Response) -> str:
    result = response.json()["result"]
    assert result["isError"] is True, result
    text: str = result["content"][0]["text"]
    return TOOL_ERROR_PREFIX.sub("", text)


def read_tool_error_code(response: Response) -> str:
    return read_tool_error(response).split(":", 1)[0]


async def start_run_for(client: AsyncClient, token: str, story_key: str, **arguments: object) -> Response:
    return await call_tool(client, token, "start_run", {"story_key": story_key, **arguments})


async def start_run_id(client: AsyncClient, token: str, story_key: str, **arguments: object) -> str:
    content = read_tool_json(await start_run_for(client, token, story_key, **arguments))
    run_id = content["run_id"]
    assert isinstance(run_id, str)
    return run_id


def build_steps(statuses: list[str], **step_fields: object) -> list[dict[str, object]]:
    return [
        {"order": order, "status": status, "actual_result": f"Saw step {order}", **step_fields}
        for order, status in enumerate(statuses, start=1)
    ]


async def record_case(
    client: AsyncClient,
    token: str,
    run_id: str,
    case_id: UUID,
    status: str = "passed",
    steps: list[dict[str, object]] | None = None,
    duration_ms: int = 900,
) -> Response:
    return await call_tool(
        client,
        token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(case_id),
            "status": status,
            "duration_ms": duration_ms,
            "steps": build_steps([status]) if steps is None else steps,
        },
    )


async def record_case_id(
    client: AsyncClient,
    token: str,
    run_id: str,
    case_id: UUID,
    status: str = "passed",
    steps: list[dict[str, object]] | None = None,
) -> str:
    content = read_tool_json(await record_case(client, token, run_id, case_id, status, steps))
    case_result_id = content["case_result_id"]
    assert isinstance(case_result_id, str)
    return case_result_id


async def finish(client: AsyncClient, token: str, run_id: str, summary: str | None = None) -> Response:
    arguments: dict[str, object] = {"run_id": run_id}
    if summary is not None:
        arguments["summary"] = summary
    return await call_tool(client, token, "finish_run", arguments)

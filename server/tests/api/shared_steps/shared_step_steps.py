from dataclasses import dataclass
from uuid import UUID

from httpx import AsyncClient, Response
from pydantic import JsonValue
from sqlalchemy import null, update

from app.container import Container
from app.modules.runs.infrastructure import RunCaseTable
from app.modules.test_cases.infrastructure import TestCaseVersionTable
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import Runner, seed_environment, sign_up_runner
from tests.api.test_cases.case_steps import SeededStory, change_status, create_case, seed_story
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer

LOG_IN_STEPS: list[JsonValue] = [
    {"action": "Open {{data.base_url}}/sign-in", "expected": "The sign-in form is shown"},
    {"action": "Sign in as {{param.role}}", "expected": "The dashboard is shown"},
]


@dataclass(frozen=True)
class SharedStepProject:
    project: SeededProject
    story: SeededStory
    runner: Runner

    @property
    def key(self) -> str:
        return self.project.key


async def set_up_shared_step_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole = ProjectRole.QC
) -> SharedStepProject:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, role)
    story = await seed_story(container, project, f"{project.key}-1", ["Sign in works"])
    await seed_environment(container, project, is_default=True)
    use_session(client, runner.account.session_token)
    return SharedStepProject(project=project, story=story, runner=runner)


def shared_step_path(project_key: str, key: str | None = None) -> str:
    base = f"/api/projects/{project_key}/shared-steps"
    return base if key is None else f"{base}/{key}"


async def create_shared_step(
    client: AsyncClient,
    project_key: str,
    key: str = "log_in",
    title: str = "Log in",
    steps: list[JsonValue] | None = None,
) -> Response:
    body = {"key": key, "title": title, "steps": LOG_IN_STEPS if steps is None else steps}
    return await client.post(shared_step_path(project_key), json=body)


async def create_shared_step_json(
    client: AsyncClient,
    project_key: str,
    key: str = "log_in",
    title: str = "Log in",
    steps: list[JsonValue] | None = None,
) -> dict[str, JsonValue]:
    response = await create_shared_step(client, project_key, key, title, steps)
    assert response.status_code == 201, response.text
    content: dict[str, JsonValue] = response.json()
    return content


async def update_shared_step(
    client: AsyncClient, project_key: str, key: str, base_version_number: int, **fields: JsonValue
) -> Response:
    return await client.patch(
        shared_step_path(project_key, key), json={"baseVersionNumber": base_version_number, **fields}
    )


async def create_case_with(client: AsyncClient, project_key: str, story_key: str, **fields: JsonValue) -> str:
    response = await create_case(client, project_key, story_key, **fields)
    assert response.status_code == 201, response.text
    code: str = response.json()["code"]
    return code


async def make_ready(client: AsyncClient, project_key: str, case_code: str) -> None:
    for status in ("in_review", "ready"):
        response = await change_status(client, project_key, case_code, status)
        assert response.status_code == 200, response.text


async def find_case_id(client: AsyncClient, project_key: str, case_code: str) -> UUID:
    response = await client.get(f"/api/projects/{project_key}/test-cases/{case_code}")
    assert response.status_code == 200, response.text
    return UUID(response.json()["id"])


async def get_run_detail(client: AsyncClient, project_key: str, run_id: str) -> Response:
    response = await client.get(f"/api/projects/{project_key}/runs/{run_id}")
    assert response.status_code == 200, response.text
    return response


async def drop_run_snapshots(container: Container, run_id: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunCaseTable).where(RunCaseTable.run_id == UUID(run_id)).values(steps=null())
        )


async def clear_saved_data_rows(container: Container, test_case_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(TestCaseVersionTable).where(TestCaseVersionTable.test_case_id == test_case_id).values(data_rows=[])
        )

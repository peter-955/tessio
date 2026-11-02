from uuid import UUID

from httpx import AsyncClient, Response
from sqlalchemy import update

from app.container import Container
from app.modules.failures.infrastructure import FailureTable
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import SeededRunnableStory, finish, start_run_id
from tests.api.suites.suite_steps import SuiteWorld, record_suite_case
from tests.support.mcp_steps import read_tool_json

DEFAULT_PLAN_NAME = "Release 2.4"
DEFAULT_ENVIRONMENT = "Staging"


def plans_path(project_key: str) -> str:
    return f"/api/projects/{project_key}/plans"


def plan_path(project_key: str, plan_id: str) -> str:
    return f"{plans_path(project_key)}/{plan_id}"


def suite_item(suite_id: str) -> dict[str, str]:
    return {"suiteId": suite_id}


def story_item(story: SeededRunnableStory) -> dict[str, str]:
    return {"storyId": str(story.story_id)}


async def create_plan(
    client: AsyncClient, project_key: str, name: str = DEFAULT_PLAN_NAME, **fields: object
) -> Response:
    return await client.post(plans_path(project_key), json={"name": name, **fields})


async def create_plan_id(client: AsyncClient, project_key: str, name: str = DEFAULT_PLAN_NAME, **fields: object) -> str:
    response = await create_plan(client, project_key, name, **fields)
    assert response.status_code == 201, response.text
    plan_id: str = response.json()["id"]
    return plan_id


async def set_plan_items(client: AsyncClient, project_key: str, plan_id: str, items: list[dict[str, str]]) -> Response:
    return await client.put(f"{plan_path(project_key, plan_id)}/items", json={"items": items})


async def seed_plan(
    client: AsyncClient,
    world: SuiteWorld,
    items: list[dict[str, str]],
    name: str = DEFAULT_PLAN_NAME,
    **fields: object,
) -> str:
    use_session(client, world.runner.account.session_token)
    plan_id = await create_plan_id(client, world.key, name, **fields)
    response = await set_plan_items(client, world.key, plan_id, items)
    assert response.status_code == 200, response.text
    return plan_id


async def get_plan(client: AsyncClient, project_key: str, plan_id: str) -> Response:
    return await client.get(plan_path(project_key, plan_id))


async def read_plan(client: AsyncClient, project_key: str, plan_id: str) -> dict[str, object]:
    response = await get_plan(client, project_key, plan_id)
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


async def read_progress(client: AsyncClient, project_key: str, plan_id: str) -> dict[str, object]:
    progress = (await read_plan(client, project_key, plan_id))["progress"]
    assert isinstance(progress, dict)
    return progress


async def sign_off_plan(client: AsyncClient, project_key: str, plan_id: str) -> Response:
    return await client.post(f"{plan_path(project_key, plan_id)}/sign-off")


async def close_plan(client: AsyncClient, project_key: str, plan_id: str) -> Response:
    return await client.post(f"{plan_path(project_key, plan_id)}/close")


async def run_story(
    client: AsyncClient,
    world: SuiteWorld,
    story: SeededRunnableStory,
    statuses: list[str],
    environment: str = DEFAULT_ENVIRONMENT,
) -> str:
    run_id = await start_run_id(client, world.runner.token, story.jira_key, environment=environment)
    for case_id, status in zip(story.case_ids, statuses, strict=False):
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, status))
    read_tool_json(await finish(client, world.runner.token, run_id))
    return run_id


async def set_failures_status(container: Container, test_case_id: UUID, status: str) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(FailureTable).where(FailureTable.test_case_id == test_case_id).values(status=status)
        )

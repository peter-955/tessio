import asyncio
from uuid import UUID

from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import text

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import assign
from tests.api.gaps.gap_steps import add_active_member
from tests.api.runs.run_steps import finish, start_run_id
from tests.api.suites.suite_steps import (
    DEFAULT_SUITE_NAME,
    record_suite_case,
    seed_suite,
    seed_suite_world,
    start_suite_run_content,
)
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json

COUNT_STATEMENTS = {
    "runs": "SELECT count(*) FROM runs",
    "case_results": "SELECT count(*) FROM case_results",
    "run_cases": "SELECT count(*) FROM run_cases",
    "run_logs": "SELECT count(*) FROM run_logs",
    "failures": "SELECT count(*) FROM failures",
    "notifications": "SELECT count(*) FROM notifications WHERE kind IN ('suite_run_finished', 'failure_assigned')",
}


async def count_rows(container: Container) -> dict[str, int]:
    async with container.database.begin():
        session = container.database.get_current_session()
        return {name: int(await session.scalar(text(statement)) or 0) for name, statement in COUNT_STATEMENTS.items()}


async def find_failure_ids(container: Container) -> list[UUID]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(text("SELECT id FROM failures ORDER BY id"))
        return list(rows)


async def find_failure_result_runs(container: Container) -> list[tuple[UUID, UUID]]:
    async with container.database.begin():
        rows = await container.database.get_current_session().execute(
            text(
                "SELECT opened.run_id, latest.run_id FROM failures "
                "JOIN case_results AS opened ON opened.id = failures.opened_by_case_result_id "
                "JOIN case_results AS latest ON latest.id = failures.latest_case_result_id"
            )
        )
        return [(row[0], row[1]) for row in rows]


async def test_the_suites_downgrade_removes_suite_runs_and_keeps_story_runs(
    migration_client: AsyncClient,
    migration_container: Container,
    recording_mailer: RecordingMailer,
    alembic_config: Config,
) -> None:
    client, container = migration_client, migration_container
    world = await seed_suite_world(client, container, recording_mailer)
    assignee_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.DEV, "Dee Veloper")
    story_run_id = await start_run_id(client, world.runner.token, world.first_story.jira_key)
    for case_id, status in zip(world.first_story.case_ids, ["failed", "passed"], strict=True):
        read_tool_json(await record_suite_case(client, world.runner.token, story_run_id, case_id, status))
    read_tool_json(await finish(client, world.runner.token, story_run_id))
    await seed_suite(client, world)
    suite_run_id = str((await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME))["run_id"])
    for case_id, status in zip(world.case_ids, ["failed", "passed", "failed", "passed"], strict=True):
        read_tool_json(await record_suite_case(client, world.runner.token, suite_run_id, case_id, status))
    read_tool_json(await finish(client, world.runner.token, suite_run_id))
    uploaded = await client.post(
        f"/api/runs/{suite_run_id}/log",
        headers={"authorization": f"Bearer {world.runner.token}"},
        json={"entries": []},
    )
    assert uploaded.status_code in {200, 201, 204}, uploaded.text
    for failure_id in await find_failure_ids(container):
        assert (await assign(client, world.key, failure_id, assignee_id)).status_code == 200
    await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME, parent_run_id=suite_run_id)
    before = await count_rows(container)
    assert (before["runs"], before["failures"], before["run_logs"]) == (3, 2, 1)
    assert before["notifications"] >= 3

    await asyncio.to_thread(command.downgrade, alembic_config, "0023")
    after = await count_rows(container)
    failure_result_runs = await find_failure_result_runs(container)
    await asyncio.to_thread(command.upgrade, alembic_config, "head")

    assert after == {
        "runs": 1,
        "case_results": 2,
        "run_cases": 2,
        "run_logs": 0,
        "failures": 1,
        "notifications": 1,
    }
    assert failure_result_runs == [(UUID(story_run_id), UUID(story_run_id))]

import asyncio

from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import text

from app.container import Container
from tests.api.runs.junit_import.junit_import_steps import import_junit, seed_import_world
from tests.conftest import RecordingMailer

COUNT_STATEMENTS = {
    "ci_runs": "SELECT count(*) FROM runs WHERE executor = 'ci'",
    "case_results": "SELECT count(*) FROM case_results",
    "failures": "SELECT count(*) FROM failures",
}
FAILING_REPORT = (
    b"<testsuite><testcase name='TC-1 pays'/><testcase name='TC-2 refunds'><failure message='boom'/></testcase>"
    b"</testsuite>"
)


async def count_rows(container: Container) -> dict[str, int]:
    async with container.database.begin():
        session = container.database.get_current_session()
        return {name: int(await session.scalar(text(statement)) or 0) for name, statement in COUNT_STATEMENTS.items()}


async def test_the_webhooks_downgrade_removes_ci_runs_without_a_story_or_suite(
    migration_client: AsyncClient,
    migration_container: Container,
    recording_mailer: RecordingMailer,
    alembic_config: Config,
) -> None:
    client, container = migration_client, migration_container
    world = await seed_import_world(client, container, recording_mailer, case_count=2)
    imported = await import_junit(client, world.project.key, FAILING_REPORT)
    assert imported.status_code == 201, imported.text
    before = await count_rows(container)

    await asyncio.to_thread(command.downgrade, alembic_config, "0028")
    after = await count_rows(container)
    await asyncio.to_thread(command.upgrade, alembic_config, "head")

    assert before == {"ci_runs": 1, "case_results": 2, "failures": 1}
    assert after == {"ci_runs": 0, "case_results": 0, "failures": 0}

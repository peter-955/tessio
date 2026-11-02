import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.insights.insight_steps import InsightWorld, sign_in_world
from tests.api.test_data.project_steps import archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer

INSIGHT_ROUTES = ("trends", "coverage-by-label", "top-failing", "flaky", "tokens", "sprint-coverage")


def build_urls(world: InsightWorld) -> list[str]:
    return [f"/api/projects/{world.project.key}/insights/{route}" for route in INSIGHT_ROUTES]


async def test_a_non_member_gets_not_found_on_every_insight(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    urls = build_urls(world)
    outsider_project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, outsider_project, ProjectRole.ADMIN)

    statuses = [(await client.get(url)).status_code for url in urls]

    assert statuses == [404] * len(INSIGHT_ROUTES)


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_role_reads_every_insight(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await sign_in_world(client, container, recording_mailer, role)

    statuses = [(await client.get(url)).status_code for url in build_urls(world)]

    assert statuses == [200] * len(INSIGHT_ROUTES)


async def test_insights_of_an_archived_project_stay_readable(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.QC)
    await archive_project(container, world.project)

    statuses = [(await client.get(url)).status_code for url in build_urls(world)]

    assert statuses == [200] * len(INSIGHT_ROUTES)

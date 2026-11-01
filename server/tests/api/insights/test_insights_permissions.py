import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.insights.insight_steps import InsightWorld, seed_story, sign_in_world
from tests.api.test_data.project_steps import archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer

ENDPOINTS = (
    "/api/projects/{project_key}/stories/{jira_key}/traceability",
    "/api/projects/{project_key}/story-progress",
    "/api/projects/{project_key}/case-latest-results",
    "/api/projects/{project_key}/dashboard",
    "/api/projects/{project_key}/my-work",
)


async def build_urls(container: Container, world: InsightWorld) -> list[str]:
    story = await seed_story(container, world, criterion_codes=("AC1",))
    return [endpoint.format(project_key=world.project.key, jira_key=story.jira_key) for endpoint in ENDPOINTS]


async def test_non_member_gets_not_found_everywhere(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    urls = await build_urls(container, world)
    outsider_project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, outsider_project, ProjectRole.ADMIN)

    statuses = [(await client.get(url)).status_code for url in urls]

    assert statuses == [404] * len(ENDPOINTS)


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_role_can_read_insights(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await sign_in_world(client, container, recording_mailer, role)
    urls = await build_urls(container, world)

    statuses = [(await client.get(url)).status_code for url in urls]

    assert statuses == [200] * len(ENDPOINTS)


async def test_archived_project_insights_stay_readable(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.QC)
    urls = await build_urls(container, world)
    await archive_project(container, world.project)

    statuses = [(await client.get(url)).status_code for url in urls]

    assert statuses == [200] * len(ENDPOINTS)

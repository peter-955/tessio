import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import sign_up_runner
from tests.api.suites.suite_steps import (
    add_cases_by_filter,
    archive_suite,
    create_suite,
    get_suite,
    seed_suite,
    seed_suite_world,
    set_suite_cases,
)
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer

EDITING_ROLES = [ProjectRole.ADMIN, ProjectRole.QC]
READ_ONLY_ROLES = [ProjectRole.PM, ProjectRole.BA, ProjectRole.DEV, ProjectRole.VIEWER]


@pytest.mark.parametrize("role", EDITING_ROLES)
async def test_admin_and_qc_edit_suites(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer, role)

    created = await create_suite(client, world.key)
    suite_id = created.json()["id"]
    cases = await set_suite_cases(client, world.key, suite_id, world.case_ids[:1])
    filtered = await add_cases_by_filter(client, world.key, suite_id, storyKey=world.second_story.jira_key)
    renamed = await client.patch(f"/api/projects/{world.key}/suites/{suite_id}", json={"name": "Renamed"})
    archived = await archive_suite(client, world.key, suite_id)

    assert [created.status_code, cases.status_code, filtered.status_code, renamed.status_code] == [201, 200, 200, 200]
    assert archived.status_code == 200


@pytest.mark.parametrize("role", READ_ONLY_ROLES)
async def test_other_roles_read_suites_but_cannot_edit_them(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    reader = await sign_up_runner(client, container, recording_mailer, world.project, role, "Rita Reader")
    use_session(client, reader.account.session_token)

    listed = await client.get(f"/api/projects/{world.key}/suites")
    detail = await get_suite(client, world.key, suite_id)
    refused = [
        await create_suite(client, world.key, "Mine"),
        await set_suite_cases(client, world.key, suite_id, []),
        await add_cases_by_filter(client, world.key, suite_id, storyKey=world.first_story.jira_key),
        await client.patch(f"/api/projects/{world.key}/suites/{suite_id}", json={"name": "Mine"}),
        await archive_suite(client, world.key, suite_id),
    ]

    assert [suite["id"] for suite in listed.json()] == [suite_id]
    assert detail.status_code == 200
    assert [(response.status_code, response.json()["code"]) for response in refused] == [
        (403, "PERMISSION_DENIED")
    ] * len(refused)


async def test_an_outsider_cannot_see_the_suites(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    other_project = await seed_project(container)
    outsider = await sign_up_runner(client, container, recording_mailer, other_project, ProjectRole.ADMIN, "Otto")
    use_session(client, outsider.account.session_token)

    listed = await client.get(f"/api/projects/{world.key}/suites")
    detail = await get_suite(client, world.key, suite_id)

    assert (listed.status_code, listed.json()["code"]) == (404, "NOT_FOUND")
    assert (detail.status_code, detail.json()["code"]) == (404, "NOT_FOUND")


async def test_an_archived_project_keeps_its_suites_read_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    await archive_project(container, world.project)

    detail = await get_suite(client, world.key, suite_id)
    created = await create_suite(client, world.key, "Late")
    cases = await set_suite_cases(client, world.key, suite_id, [])

    assert detail.status_code == 200
    assert (created.status_code, created.json()["code"]) == (409, "PROJECT_ARCHIVED")
    assert (cases.status_code, cases.json()["code"]) == (409, "PROJECT_ARCHIVED")

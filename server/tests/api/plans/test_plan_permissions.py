import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.plans.plan_steps import (
    close_plan,
    create_plan,
    create_plan_id,
    get_plan,
    plan_path,
    plans_path,
    seed_plan,
    set_plan_items,
    sign_off_plan,
    story_item,
)
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import sign_up_runner
from tests.api.suites.suite_steps import seed_suite_world
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer

EDITING_ROLES = [ProjectRole.ADMIN, ProjectRole.PM, ProjectRole.QC]
NON_EDITING_ROLES = [ProjectRole.BA, ProjectRole.DEV, ProjectRole.VIEWER]
SIGN_OFF_ROLES = [ProjectRole.ADMIN, ProjectRole.QC]
NON_SIGN_OFF_ROLES = [ProjectRole.PM, ProjectRole.BA, ProjectRole.DEV, ProjectRole.VIEWER]


@pytest.mark.parametrize("role", EDITING_ROLES)
async def test_admin_pm_and_qc_create_edit_and_close_plans(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer, role)

    created = await create_plan(client, world.key)
    plan_id = created.json()["id"]
    items = await set_plan_items(client, world.key, plan_id, [story_item(world.first_story)])
    renamed = await client.patch(plan_path(world.key, plan_id), json={"name": "Renamed"})
    closed = await close_plan(client, world.key, plan_id)

    assert [created.status_code, items.status_code, renamed.status_code, closed.status_code] == [201, 200, 200, 200]


@pytest.mark.parametrize("role", NON_EDITING_ROLES)
async def test_other_roles_read_plans_but_cannot_change_them(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    reader = await sign_up_runner(client, container, recording_mailer, world.project, role, "Rita Reader")
    use_session(client, reader.account.session_token)

    listed = await client.get(plans_path(world.key))
    detail = await get_plan(client, world.key, plan_id)
    refused = [
        await create_plan(client, world.key, "Mine"),
        await client.patch(plan_path(world.key, plan_id), json={"name": "Mine"}),
        await set_plan_items(client, world.key, plan_id, []),
        await close_plan(client, world.key, plan_id),
    ]

    assert [plan["id"] for plan in listed.json()] == [plan_id]
    assert detail.status_code == 200
    assert [(response.status_code, response.json()["code"]) for response in refused] == [
        (403, "PERMISSION_DENIED")
    ] * len(refused)


@pytest.mark.parametrize("role", SIGN_OFF_ROLES)
async def test_admin_and_qc_sign_off(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer, role)
    plan_id = await create_plan_id(client, world.key)

    response = await sign_off_plan(client, world.key, plan_id)

    assert response.status_code == 200, response.text


@pytest.mark.parametrize("role", NON_SIGN_OFF_ROLES)
async def test_other_roles_cannot_sign_off(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await create_plan_id(client, world.key)
    member = await sign_up_runner(client, container, recording_mailer, world.project, role, "Sam Member")
    use_session(client, member.account.session_token)

    response = await sign_off_plan(client, world.key, plan_id)

    assert (response.status_code, response.json()["code"]) == (403, "PERMISSION_DENIED")


async def test_an_outsider_cannot_see_the_plans(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await create_plan_id(client, world.key)
    other_project = await seed_project(container)
    outsider = await sign_up_runner(client, container, recording_mailer, other_project, ProjectRole.ADMIN, "Otto")
    use_session(client, outsider.account.session_token)

    listed = await client.get(plans_path(world.key))
    detail = await get_plan(client, world.key, plan_id)
    signed_off = await sign_off_plan(client, world.key, plan_id)

    assert [(response.status_code, response.json()["code"]) for response in (listed, detail, signed_off)] == [
        (404, "NOT_FOUND")
    ] * 3


async def test_an_archived_project_keeps_its_plans_read_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await archive_project(container, world.project)

    detail = await get_plan(client, world.key, plan_id)
    refused = [
        await create_plan(client, world.key, "Late"),
        await set_plan_items(client, world.key, plan_id, []),
        await sign_off_plan(client, world.key, plan_id),
        await close_plan(client, world.key, plan_id),
    ]

    assert detail.status_code == 200
    assert [(response.status_code, response.json()["code"]) for response in refused] == [
        (409, "PROJECT_ARCHIVED")
    ] * len(refused)

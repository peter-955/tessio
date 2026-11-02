import pytest
from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import PROJECT_ROLE_CAPABILITIES, Capability, ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.shared_steps.shared_step_steps import (
    SharedStepProject,
    create_shared_step,
    create_shared_step_json,
    set_up_shared_step_project,
    shared_step_path,
    update_shared_step,
)
from tests.api.test_data.project_steps import sign_up_member
from tests.conftest import RecordingMailer

EDITOR_ROLES = {
    role for role, capabilities in PROJECT_ROLE_CAPABILITIES.items() if Capability.TEST_CASE_EDIT in capabilities
}


async def read_shared_steps(client: AsyncClient, world: SharedStepProject) -> list[Response]:
    return [
        await client.get(shared_step_path(world.key)),
        await client.get(shared_step_path(world.key, "log_in")),
        await client.get(f"{shared_step_path(world.key, 'log_in')}/usage"),
    ]


async def write_shared_steps(client: AsyncClient, world: SharedStepProject) -> list[Response]:
    return [
        await create_shared_step(client, world.key, key="add_to_cart"),
        await update_shared_step(client, world.key, "log_in", 1, title="Sign in"),
    ]


async def set_up_member(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> SharedStepProject:
    world = await set_up_shared_step_project(client, container, recording_mailer, ProjectRole.ADMIN)
    await create_shared_step_json(client, world.key)
    await sign_up_member(client, container, recording_mailer, world.project, role)
    return world


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_member_reads_shared_steps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await set_up_member(client, container, recording_mailer, role)

    responses = await read_shared_steps(client, world)

    assert [response.status_code for response in responses] == [200, 200, 200]


@pytest.mark.parametrize("role", sorted(EDITOR_ROLES))
async def test_editors_write_shared_steps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await set_up_member(client, container, recording_mailer, role)

    responses = await write_shared_steps(client, world)

    assert [response.status_code for response in responses] == [201, 200]


@pytest.mark.parametrize("role", sorted(set(ProjectRole) - EDITOR_ROLES))
async def test_other_roles_cannot_write_shared_steps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    world = await set_up_member(client, container, recording_mailer, role)

    responses = await write_shared_steps(client, world)

    assert [response.status_code for response in responses] == [403, 403]
    assert {response.json()["code"] for response in responses} == {"PERMISSION_DENIED"}


async def test_a_non_member_sees_nothing(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_member(client, container, recording_mailer, ProjectRole.QC)
    outsider = await set_up_shared_step_project(client, container, recording_mailer)
    use_session(client, outsider.runner.account.session_token)

    responses = [*await read_shared_steps(client, world), *await write_shared_steps(client, world)]

    assert {response.status_code for response in responses} == {404}

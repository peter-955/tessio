from uuid import UUID

import pytest
from httpx import AsyncClient

from app.modules.projects.domains.project_changes.entity import ProjectChanges
from app.modules.users import build_actor
from app.shared.common import TessioError
from app.shared.permissions import Actor, ProjectRole
from app.shared.typing.enums import ErrorCode
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_environment
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def set_up_admin(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, Actor]:
    project = await seed_project(data_container)
    user_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)
    async with data_container.database.begin():
        user = await data_container.user_repository.find_by_id(user_id)
    assert user is not None
    return project, build_actor(user)


async def test_the_default_environment_is_set_and_cleared(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, actor = await set_up_admin(client, data_container, recording_mailer)
    environment_id = UUID(await create_environment(client, project))

    set_overview = await data_container.update_project.execute(
        actor, project.key, ProjectChanges(default_environment_id=environment_id)
    )
    renamed_overview = await data_container.update_project.execute(actor, project.key, ProjectChanges(name="Renamed"))
    cleared_overview = await data_container.update_project.execute(
        actor, project.key, ProjectChanges(is_default_environment_cleared=True)
    )

    assert set_overview.project.default_environment_id == environment_id
    assert renamed_overview.project.default_environment_id == environment_id
    assert cleared_overview.project.default_environment_id is None
    async with data_container.database.begin():
        stored_project = await data_container.project_repository.find_by_id(project.id)
    assert stored_project is not None
    assert stored_project.default_environment_id is None
    assert stored_project.name == "Renamed"


async def test_an_environment_of_another_project_is_an_unknown_reference(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, actor = await set_up_admin(client, data_container, recording_mailer)
    other_project = await seed_project(data_container)
    await add_member(data_container, other_project, actor.user_id, ProjectRole.ADMIN)
    foreign_environment_id = UUID(await create_environment(client, other_project))

    with pytest.raises(TessioError) as raised:
        await data_container.update_project.execute(
            actor, project.key, ProjectChanges(default_environment_id=foreign_environment_id)
        )

    assert raised.value.code is ErrorCode.UNKNOWN_REFERENCE


async def test_an_archived_environment_is_an_unknown_reference(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, actor = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")

    with pytest.raises(TessioError) as raised:
        await data_container.update_project.execute(
            actor, project.key, ProjectChanges(default_environment_id=UUID(environment_id))
        )

    assert raised.value.code is ErrorCode.UNKNOWN_REFERENCE
    assert raised.value.message == "Pick an active environment of this project."


async def test_the_project_response_has_a_default_environment_id(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)

    response = await client.get(f"/api/projects/{project.key}")

    assert response.status_code == 200
    assert "defaultEnvironmentId" in response.json()

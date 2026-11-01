from uuid import UUID

from httpx import AsyncClient

from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def seed_secrets(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, str, str]:
    project = await seed_project(data_container)
    await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)
    staging_id = await create_environment(client, project, name="Staging")
    production_id = await create_environment(client, project, name="Production")
    await create_data_item(client, project, "ADMIN_PASSWORD", "project-password", kind="secret")
    await create_data_item(client, project, "API_TOKEN", "project-token", kind="secret")
    await create_data_item(client, project, "USER", "alice")
    await create_data_item(
        client, project, "ADMIN_PASSWORD", "staging-password", kind="secret", environment_id=staging_id
    )
    await create_data_item(client, project, "API_TOKEN", "not-secret-here", environment_id=staging_id)
    await create_data_item(
        client, project, "ADMIN_PASSWORD", "production-password", kind="secret", environment_id=production_id
    )
    return project, staging_id, production_id


async def test_masking_values_include_project_and_environment_secrets(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, staging_id, _ = await seed_secrets(client, data_container, recording_mailer)
    staging_values = await data_container.secret_value_reader.list_secret_values(project.id, UUID(staging_id))
    project_values = await data_container.secret_value_reader.list_secret_values(project.id, None)

    assert sorted(staging_values) == ["project-password", "project-token", "staging-password"]
    assert sorted(project_values) == ["project-password", "project-token"]


async def test_resolve_secrets_returns_the_effective_secret_rows(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, staging_id, production_id = await seed_secrets(client, data_container, recording_mailer)
    keys = ["ADMIN_PASSWORD", "API_TOKEN", "USER", "MISSING"]
    staging = await data_container.secret_value_reader.resolve_secrets(project.id, UUID(staging_id), keys)
    production = await data_container.secret_value_reader.resolve_secrets(project.id, UUID(production_id), keys)
    project_wide = await data_container.secret_value_reader.resolve_secrets(project.id, None, ["API_TOKEN"])

    assert staging == {"ADMIN_PASSWORD": "staging-password"}
    assert production == {"ADMIN_PASSWORD": "production-password", "API_TOKEN": "project-token"}
    assert project_wide == {"API_TOKEN": "project-token"}

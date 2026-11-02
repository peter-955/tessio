import pytest
from httpx import AsyncClient

from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer

EDITOR_ROLES = {ProjectRole.ADMIN, ProjectRole.QC, ProjectRole.DEV}
SECRET_ROLES = {ProjectRole.ADMIN, ProjectRole.QC}


async def seed_project_with_items(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, str, str, str]:
    project = await seed_project(data_container)
    await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)
    environment_id = await create_environment(client, project)
    variable_id = await create_data_item(client, project, "USER", "alice")
    secret_id = await create_data_item(client, project, "ADMIN_PASSWORD", "s3cret", kind="secret")
    return project, environment_id, variable_id, secret_id


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_member_can_list_environments_and_test_data(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, environment_id, _, _ = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, role)

    responses = [
        await client.get(f"/api/projects/{project.key}/environments"),
        await client.get(f"/api/projects/{project.key}/test-data"),
        await client.get(f"/api/projects/{project.key}/test-data/effective", params={"environmentId": environment_id}),
    ]

    assert [response.status_code for response in responses] == [200, 200, 200]
    assert "s3cret" not in responses[1].text


async def test_a_non_member_gets_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _, _, secret_id = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, None)

    responses = [
        await client.get(f"/api/projects/{project.key}/environments"),
        await client.get(f"/api/projects/{project.key}/test-data"),
        await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_admins_qc_and_devs_manage_environments_and_plain_items(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, environment_id, variable_id, _ = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, role)

    created_environment = await client.post(
        f"/api/projects/{project.key}/environments", json={"name": "QA", "baseUrl": "https://qa.test"}
    )
    archived_environment = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")
    created_variable = await client.post(
        f"/api/projects/{project.key}/test-data", json={"key": "LOCALE", "kind": "variable", "value": "en"}
    )
    created_endpoint = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "CHECKOUT", "kind": "variable", "value": "https://shop.test/checkout"},
    )
    updated_variable = await client.put(
        f"/api/projects/{project.key}/test-data/{variable_id}", json={"key": "USER", "kind": "variable", "value": "bo"}
    )
    deleted_variable = await client.delete(f"/api/projects/{project.key}/test-data/{variable_id}")

    is_editor = role in EDITOR_ROLES
    assert created_environment.status_code == (201 if is_editor else 403)
    assert archived_environment.status_code == (200 if is_editor else 403)
    assert created_variable.status_code == (201 if is_editor else 403)
    assert created_endpoint.status_code == (201 if is_editor else 403)
    assert updated_variable.status_code == (200 if is_editor else 403)
    assert deleted_variable.status_code == (204 if is_editor else 403)


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_only_admins_and_qc_write_and_reveal_secrets(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, _, variable_id, secret_id = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, role)

    created_secret = await client.post(
        f"/api/projects/{project.key}/test-data", json={"key": "API_TOKEN", "kind": "secret", "value": "t0ken"}
    )
    variable_to_secret = await client.put(
        f"/api/projects/{project.key}/test-data/{variable_id}", json={"key": "USER", "kind": "secret", "value": "x"}
    )
    secret_to_variable = await client.put(
        f"/api/projects/{project.key}/test-data/{secret_id}",
        json={"key": "ADMIN_PASSWORD", "kind": "variable", "value": "x"},
    )
    revealed = await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal")

    can_use_secrets = role in SECRET_ROLES
    assert created_secret.status_code == (201 if can_use_secrets else 403)
    assert variable_to_secret.status_code == (200 if can_use_secrets else 403)
    assert secret_to_variable.status_code == (200 if can_use_secrets else 403)
    if can_use_secrets:
        assert revealed.status_code == 422
    else:
        assert revealed.status_code == 403


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_deleting_a_secret_needs_secret_edit(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project, _, _, secret_id = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, role)

    revealed = await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal")
    deleted = await client.delete(f"/api/projects/{project.key}/test-data/{secret_id}")

    assert revealed.status_code == (200 if role in SECRET_ROLES else 403)
    assert deleted.status_code == (204 if role in SECRET_ROLES else 403)


async def test_a_workspace_admin_who_is_not_a_member_can_reveal(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _, _, secret_id = await seed_project_with_items(client, data_container, recording_mailer)
    await sign_up_member(client, data_container, recording_mailer, project, None, WorkspaceRole.ADMIN)

    revealed = await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal")

    assert revealed.status_code == 200
    assert revealed.json() == {"value": "s3cret"}


async def test_an_archived_project_is_read_only_but_secrets_can_still_be_revealed(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, environment_id, variable_id, secret_id = await seed_project_with_items(
        client, data_container, recording_mailer
    )
    await archive_project(data_container, project)

    listed_environments = await client.get(f"/api/projects/{project.key}/environments")
    listed_items = await client.get(f"/api/projects/{project.key}/test-data")
    revealed = await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal")
    writes = [
        await client.post(
            f"/api/projects/{project.key}/test-data", json={"key": "LOCALE", "kind": "variable", "value": "en"}
        ),
        await client.put(
            f"/api/projects/{project.key}/test-data/{variable_id}",
            json={"key": "USER", "kind": "variable", "value": "bo"},
        ),
        await client.delete(f"/api/projects/{project.key}/test-data/{variable_id}"),
        await client.post(
            f"/api/projects/{project.key}/environments", json={"name": "QA", "baseUrl": "https://qa.test"}
        ),
        await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive"),
        await client.delete(f"/api/projects/{project.key}/environments/{environment_id}"),
    ]

    assert listed_environments.status_code == 200
    assert listed_items.status_code == 200
    assert revealed.status_code == 200
    assert revealed.json() == {"value": "s3cret"}
    assert [response.status_code for response in writes] == [409] * len(writes)
    assert {response.json()["code"] for response in writes} == {"PROJECT_ARCHIVED"}

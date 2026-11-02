import pytest
from httpx import AsyncClient, Response

from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import read_tool_error
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def set_up_token(
    client: AsyncClient,
    data_container: DataTestContainer,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
) -> tuple[SeededProject, str]:
    project = await seed_project(data_container)
    await sign_up_member(client, data_container, recording_mailer, project, role)
    return project, await create_token(client, project.key)


async def set_test_data(client: AsyncClient, token: str, **arguments: object) -> Response:
    return await call_tool(client, token, "set_test_data", {"kind": "variable", **arguments})


async def list_items(client: AsyncClient, project: SeededProject) -> list[dict[str, object]]:
    response = await client.get(f"/api/projects/{project.key}/test-data")
    assert response.status_code == 200, response.text
    items: list[dict[str, object]] = response.json()
    return items


@pytest.mark.parametrize("kind", ["variable", "endpoint"])
@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.ADMIN])
async def test_a_new_key_is_created_for_the_whole_project(
    client: AsyncClient,
    data_container: DataTestContainer,
    recording_mailer: RecordingMailer,
    kind: str,
    role: ProjectRole,
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer, role)

    response = await set_test_data(client, token, key="SHOP_URL", value="https://shop.test", kind=kind)

    assert read_tool_json(response) == {"action": "created"}
    items = await list_items(client, project)
    assert [(item["key"], item["kind"], item["value"], item["environmentId"]) for item in items] == [
        ("SHOP_URL", "variable", "https://shop.test", None)
    ]


async def test_an_existing_key_is_updated_and_an_equal_value_is_left_unchanged(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "CURRENCY", "EUR")

    updated = await set_test_data(client, token, key="CURRENCY", value="USD")
    unchanged = await set_test_data(client, token, key="CURRENCY", value="USD")

    assert read_tool_json(updated) == {"action": "updated"}
    assert read_tool_json(unchanged) == {"action": "unchanged"}
    items = await list_items(client, project)
    assert [(item["id"], item["value"]) for item in items] == [(item_id, "USD")]


async def test_an_environment_value_overrides_the_project_value_without_changing_it(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project, "Staging")
    await create_data_item(client, project, "SHOP_URL", "https://shop.test")

    response = await set_test_data(
        client, token, key="SHOP_URL", value="https://staging.shop.test", environment="  staging "
    )

    assert read_tool_json(response) == {"action": "created"}
    items = await list_items(client, project)
    assert sorted((item["environmentId"] or "", item["value"]) for item in items) == [
        ("", "https://shop.test"),
        (environment_id, "https://staging.shop.test"),
    ]
    effective = await client.get(
        f"/api/projects/{project.key}/test-data/effective", params={"environmentId": environment_id}
    )
    assert [item["value"] for item in effective.json()] == ["https://staging.shop.test"]


async def test_a_project_write_names_the_environments_that_override_it(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project, "Staging")
    await create_data_item(client, project, "SHOP_URL", "https://staging.shop.test", environment_id=environment_id)

    response = await set_test_data(client, token, key="SHOP_URL", value="https://shop.test")

    assert read_tool_json(response) == {"action": "created", "overridden_in": ["Staging"]}


async def test_a_secret_kind_is_refused_and_nothing_is_saved(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer, ProjectRole.ADMIN)

    response = await set_test_data(client, token, key="ADMIN_PASSWORD", value="hunter2", kind="secret")

    assert read_tool_error(response) == (
        "INVALID_REQUEST: Claude never saves secrets. Add the secret on the Test data page."
    )
    assert await list_items(client, project) == []


async def test_a_key_that_holds_a_secret_is_never_overwritten(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer, ProjectRole.ADMIN)
    await create_environment(client, project, "Staging")
    await create_data_item(client, project, "API_KEY", "very-secret", kind="secret")

    project_write = await set_test_data(client, token, key="API_KEY", value="plain")
    environment_write = await set_test_data(client, token, key="API_KEY", value="plain", environment="Staging")

    assert read_tool_error(project_write) == "INVALID_REQUEST: This key is a secret. Change it on the Test data page."
    assert read_tool_error(environment_write).startswith("INVALID_REQUEST: ")
    items = await list_items(client, project)
    assert [(item["kind"], item["environmentId"]) for item in items] == [("secret", None)]


async def test_an_unknown_environment_is_not_found_and_an_archived_one_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project, "Old")
    archived = await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")
    assert archived.status_code == 200, archived.text

    unknown = await set_test_data(client, token, key="SHOP_URL", value="https://shop.test", environment="Prod")
    archived_write = await set_test_data(client, token, key="SHOP_URL", value="https://shop.test", environment="Old")

    assert read_tool_error(unknown) == "NOT_FOUND: Environment not found."
    assert read_tool_error(archived_write) == "INVALID_REQUEST: This environment is archived."
    assert await list_items(client, project) == []


async def test_an_environment_of_another_project_is_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    other_project = await seed_project(data_container)
    await sign_up_member(client, data_container, recording_mailer, other_project, ProjectRole.QC)
    await create_environment(client, other_project, "Elsewhere")
    project, token = await set_up_token(client, data_container, recording_mailer)

    response = await set_test_data(client, token, key="SHOP_URL", value="https://shop.test", environment="Elsewhere")

    assert read_tool_error(response) == "NOT_FOUND: Environment not found."
    assert await list_items(client, project) == []


async def test_viewers_and_archived_projects_are_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    _, viewer_token = await set_up_token(client, data_container, recording_mailer, ProjectRole.VIEWER)
    archived_project, qc_token = await set_up_token(client, data_container, recording_mailer)
    await archive_project(data_container, archived_project)

    viewer = await set_test_data(client, viewer_token, key="SHOP_URL", value="https://shop.test")
    archived = await set_test_data(client, qc_token, key="SHOP_URL", value="https://shop.test")

    assert read_tool_error(viewer).startswith("PERMISSION_DENIED: ")
    assert read_tool_error(archived).startswith("PROJECT_ARCHIVED: ")


@pytest.mark.parametrize(
    "arguments",
    [
        {"key": "1_STARTS_WITH_A_DIGIT", "value": "x"},
        {"key": "SHOP_URL", "value": ""},
        {"key": "SHOP_URL", "value": "x" * 10001},
        {"key": "SHOP_URL", "value": "x", "kind": "file"},
    ],
)
async def test_invalid_arguments_are_refused(
    client: AsyncClient,
    data_container: DataTestContainer,
    recording_mailer: RecordingMailer,
    arguments: dict[str, object],
) -> None:
    project, token = await set_up_token(client, data_container, recording_mailer)

    response = await set_test_data(client, token, **arguments)

    assert response.json()["result"]["isError"] is True
    assert await list_items(client, project) == []

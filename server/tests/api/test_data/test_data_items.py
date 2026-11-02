from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import text

from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer

SECRET_VALUE = "hunter2-very-secret"


async def set_up_admin(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, UUID]:
    project = await seed_project(data_container)
    user_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)
    return project, user_id


async def read_stored_value(data_container: DataTestContainer, item_id: str) -> tuple[str | None, bytes | None]:
    async with data_container.database.begin():
        row = (
            await data_container.database.get_current_session().execute(
                text("SELECT value, value_encrypted FROM test_data WHERE id = :id"), {"id": UUID(item_id)}
            )
        ).one()
    value: str | None = row[0]
    value_encrypted: bytes | None = row[1]
    return value, value_encrypted


async def test_items_are_created_per_scope_and_listed_project_rows_first(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)

    project_response = await client.post(
        f"/api/projects/{project.key}/test-data", json={"key": "USER", "kind": "variable", "value": "alice"}
    )
    await create_data_item(client, project, "USER", "bob", environment_id=environment_id)
    await create_data_item(client, project, "CHECKOUT", "https://shop.test/checkout", kind="variable")

    assert project_response.status_code == 201
    body = project_response.json()
    assert body.keys() == {"id", "environmentId", "key", "kind", "value", "hasValue", "createdAt", "description"}
    assert body["environmentId"] is None
    assert body["value"] == "alice"
    assert body["hasValue"] is True
    listed = (await client.get(f"/api/projects/{project.key}/test-data")).json()
    assert [(item["key"], item["environmentId"], item["value"]) for item in listed] == [
        ("CHECKOUT", None, "https://shop.test/checkout"),
        ("USER", None, "alice"),
        ("USER", environment_id, "bob"),
    ]


async def test_a_duplicate_key_in_the_same_scope_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await create_data_item(client, project, "USER", "alice")
    await create_data_item(client, project, "USER", "bob", environment_id=environment_id)

    in_project = await client.post(
        f"/api/projects/{project.key}/test-data", json={"key": "USER", "kind": "secret", "value": "x"}
    )
    in_environment = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "USER", "kind": "variable", "value": "x", "environmentId": environment_id},
    )

    assert in_project.status_code == 409
    assert in_project.json()["code"] == "TEST_DATA_KEY_ALREADY_USED"
    assert in_environment.status_code == 409
    assert in_environment.json()["code"] == "TEST_DATA_KEY_ALREADY_USED"


async def test_renaming_onto_a_used_key_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    await create_data_item(client, project, "USER", "alice")
    other_id = await create_data_item(client, project, "OTHER", "x")

    renamed = await client.put(
        f"/api/projects/{project.key}/test-data/{other_id}", json={"key": "USER", "kind": "variable", "value": "x"}
    )
    kept = await client.put(
        f"/api/projects/{project.key}/test-data/{other_id}", json={"key": "OTHER", "kind": "variable", "value": "y"}
    )

    assert renamed.status_code == 409
    assert renamed.json()["code"] == "TEST_DATA_KEY_ALREADY_USED"
    assert kept.status_code == 200
    assert (kept.json()["kind"], kept.json()["value"]) == ("variable", "y")


async def test_an_archived_or_unknown_environment_cannot_get_new_items(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")

    archived = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "USER", "kind": "variable", "value": "x", "environmentId": environment_id},
    )
    unknown = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "USER", "kind": "variable", "value": "x", "environmentId": str(UUID(int=7))},
    )

    assert archived.status_code == 422
    assert archived.json()["code"] == "INVALID_REQUEST"
    assert unknown.status_code == 404


async def test_bad_keys_and_values_are_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)

    bodies = [
        {"key": "1USER", "kind": "variable", "value": "x"},
        {"key": "HAS SPACE", "kind": "variable", "value": "x"},
        {"key": "K" * 101, "kind": "variable", "value": "x"},
        {"key": "USER", "kind": "variable", "value": ""},
        {"key": "USER", "kind": "variable", "value": "x" * 10001},
        {"key": "USER", "kind": "password", "value": "x"},
    ]
    responses = [await client.post(f"/api/projects/{project.key}/test-data", json=body) for body in bodies]

    assert [response.status_code for response in responses] == [422] * len(bodies)


async def test_the_effective_view_prefers_the_environment_row(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    staging_id = await create_environment(client, project, name="Staging")
    production_id = await create_environment(client, project, name="Production")
    await create_data_item(client, project, "USER", "project-user")
    await create_data_item(client, project, "LOCALE", "en")
    await create_data_item(client, project, "USER", "staging-user", environment_id=staging_id)
    await create_data_item(client, project, "ONLY_STAGING", "s", environment_id=staging_id)

    staging = await client.get(f"/api/projects/{project.key}/test-data/effective", params={"environmentId": staging_id})
    production = await client.get(
        f"/api/projects/{project.key}/test-data/effective", params={"environmentId": production_id}
    )
    project_only = await client.get(f"/api/projects/{project.key}/test-data/effective")
    unknown = await client.get(
        f"/api/projects/{project.key}/test-data/effective", params={"environmentId": str(UUID(int=9))}
    )

    assert [(item["key"], item["value"], item["environmentId"]) for item in staging.json()] == [
        ("LOCALE", "en", None),
        ("ONLY_STAGING", "s", staging_id),
        ("USER", "staging-user", staging_id),
    ]
    project_values = [("LOCALE", "en"), ("USER", "project-user")]
    assert [(item["key"], item["value"]) for item in production.json()] == project_values
    assert [(item["key"], item["value"]) for item in project_only.json()] == project_values
    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Environment not found."


async def test_secrets_are_stored_encrypted_and_never_listed(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)

    created = await client.post(
        f"/api/projects/{project.key}/test-data",
        json={"key": "ADMIN_PASSWORD", "kind": "secret", "value": SECRET_VALUE},
    )
    await create_data_item(client, project, "API_TOKEN", SECRET_VALUE, kind="secret", environment_id=environment_id)

    assert created.status_code == 201
    assert created.json()["value"] is None
    assert created.json()["hasValue"] is True
    assert SECRET_VALUE not in created.text
    value, value_encrypted = await read_stored_value(data_container, created.json()["id"])
    assert value is None
    assert value_encrypted is not None
    assert SECRET_VALUE.encode() not in value_encrypted
    assert data_container.secret_cipher.decrypt(value_encrypted).decode() == SECRET_VALUE
    listed = await client.get(f"/api/projects/{project.key}/test-data")
    effective = await client.get(
        f"/api/projects/{project.key}/test-data/effective", params={"environmentId": environment_id}
    )
    assert SECRET_VALUE not in listed.text
    assert SECRET_VALUE not in effective.text
    assert {(item["key"], item["value"], item["hasValue"]) for item in effective.json()} == {
        ("ADMIN_PASSWORD", None, True),
        ("API_TOKEN", None, True),
    }


async def test_updating_a_secret_without_a_value_keeps_the_stored_value(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "ADMIN_PASSWORD", SECRET_VALUE, kind="secret")
    _, original_encrypted = await read_stored_value(data_container, item_id)

    renamed = await client.put(
        f"/api/projects/{project.key}/test-data/{item_id}",
        json={"key": "ROOT_PASSWORD", "kind": "secret", "value": None},
    )

    assert renamed.status_code == 200
    assert renamed.json()["key"] == "ROOT_PASSWORD"
    assert renamed.json()["value"] is None
    assert await read_stored_value(data_container, item_id) == (None, original_encrypted)
    revealed = await client.post(f"/api/projects/{project.key}/test-data/{item_id}/reveal")
    assert revealed.json() == {"value": SECRET_VALUE}


async def test_changing_a_secret_into_a_variable_needs_a_value(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    secret_id = await create_data_item(client, project, "ADMIN_PASSWORD", SECRET_VALUE, kind="secret")
    variable_id = await create_data_item(client, project, "USER", "alice")

    without_value = await client.put(
        f"/api/projects/{project.key}/test-data/{secret_id}", json={"key": "ADMIN_PASSWORD", "kind": "variable"}
    )
    variable_without_value = await client.put(
        f"/api/projects/{project.key}/test-data/{variable_id}", json={"key": "USER", "kind": "secret"}
    )
    with_value = await client.put(
        f"/api/projects/{project.key}/test-data/{secret_id}",
        json={"key": "ADMIN_PASSWORD", "kind": "variable", "value": "now-plain"},
    )

    assert without_value.status_code == 422
    assert without_value.json()["code"] == "INVALID_REQUEST"
    assert variable_without_value.status_code == 422
    assert with_value.status_code == 200
    assert with_value.json()["value"] == "now-plain"
    assert await read_stored_value(data_container, secret_id) == ("now-plain", None)


async def test_delete_removes_the_item(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "USER", "alice")

    deleted = await client.delete(f"/api/projects/{project.key}/test-data/{item_id}")
    deleted_again = await client.delete(f"/api/projects/{project.key}/test-data/{item_id}")

    assert deleted.status_code == 204
    assert deleted_again.status_code == 404
    assert (await client.get(f"/api/projects/{project.key}/test-data")).json() == []


async def test_reveal_returns_the_value_and_writes_one_audit_event(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_admin(client, data_container, recording_mailer)
    item_id = await create_data_item(client, project, "ADMIN_PASSWORD", SECRET_VALUE, kind="secret")

    response = await client.post(f"/api/projects/{project.key}/test-data/{item_id}/reveal")

    assert response.status_code == 200
    assert response.json() == {"value": SECRET_VALUE}
    async with data_container.database.begin():
        events = await data_container.audit_event_repository.list_for_target(UUID(item_id))
    assert [(event.action.value, event.actor_id, event.project_id, event.target_id) for event in events] == [
        ("secret.reveal", user_id, project.id, UUID(item_id))
    ]


async def test_reveal_of_a_variable_or_a_missing_item_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    variable_id = await create_data_item(client, project, "USER", "alice")

    variable = await client.post(f"/api/projects/{project.key}/test-data/{variable_id}/reveal")
    missing = await client.post(f"/api/projects/{project.key}/test-data/{UUID(int=3)}/reveal")

    assert variable.status_code == 422
    assert variable.json()["code"] == "INVALID_REQUEST"
    assert missing.status_code == 404
    async with data_container.database.begin():
        assert await data_container.audit_event_repository.list_for_target(UUID(variable_id)) == []


async def test_items_of_another_project_are_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_admin(client, data_container, recording_mailer)
    other_project, _ = await set_up_admin(client, data_container, recording_mailer)
    foreign_id = await create_data_item(client, other_project, "TOKEN", SECRET_VALUE, kind="secret")
    await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)

    responses = [
        await client.put(
            f"/api/projects/{project.key}/test-data/{foreign_id}", json={"key": "X", "kind": "variable", "value": "y"}
        ),
        await client.delete(f"/api/projects/{project.key}/test-data/{foreign_id}"),
        await client.post(f"/api/projects/{project.key}/test-data/{foreign_id}/reveal"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]

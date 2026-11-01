import json
from uuid import UUID

from httpx import AsyncClient, Response

from app.modules.files import StoredFileKind, StoredFileStatus
from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject, add_member, seed_import_file, seed_project, sign_up_member
from tests.conftest import RecordingMailer

DOTENV_CONTENT = b"""# staging
BASE_URL=https://staging.shop.test
USER=alice
ADMIN_PASSWORD="s3cret"
LOCALE=fr
not a line
"""


async def set_up_member(
    client: AsyncClient,
    data_container: DataTestContainer,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
) -> tuple[SeededProject, UUID]:
    project = await seed_project(data_container)
    user_id = await sign_up_member(client, data_container, recording_mailer, project, role)
    return project, user_id


async def upload(
    data_container: DataTestContainer,
    project: SeededProject,
    user_id: UUID,
    file_name: str,
    content: bytes,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    size: int | None = None,
    kind: StoredFileKind = StoredFileKind.IMPORT,
) -> str:
    object_storage = data_container.in_memory_object_storage
    file_id = await seed_import_file(
        data_container, object_storage, project, user_id, file_name, content, status, size, kind
    )
    return str(file_id)


async def preview(
    client: AsyncClient, project: SeededProject, file_id: str, environment_id: str | None = None
) -> Response:
    return await client.post(
        f"/api/projects/{project.key}/test-data/import/preview",
        json={"fileId": file_id, "environmentId": environment_id},
    )


async def commit(
    client: AsyncClient,
    project: SeededProject,
    file_id: str,
    items: list[tuple[str, str]],
    environment_id: str | None = None,
) -> Response:
    return await client.post(
        f"/api/projects/{project.key}/test-data/import/commit",
        json={
            "fileId": file_id,
            "environmentId": environment_id,
            "items": [{"key": key, "kind": kind} for key, kind in items],
        },
    )


async def test_preview_suggests_kinds_and_actions_and_hides_secret_values(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    await create_data_item(client, project, "USER", "alice")
    await create_data_item(client, project, "ADMIN_PASSWORD", "old-secret", kind="secret")
    await create_data_item(client, project, "LOCALE", "en")
    file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT)

    response = await preview(client, project, file_id)

    assert response.status_code == 200
    assert response.json() == {
        "format": "dotenv",
        "items": [
            {"key": "BASE_URL", "kind": "endpoint", "value": "https://staging.shop.test", "action": "create"},
            {"key": "USER", "kind": "variable", "value": "alice", "action": "unchanged"},
            {"key": "ADMIN_PASSWORD", "kind": "secret", "value": None, "action": "update"},
            {"key": "LOCALE", "kind": "variable", "value": "fr", "action": "update"},
        ],
        "skipped": [{"location": "6", "reason": "invalid_line"}],
    }
    assert "s3cret" not in response.text


async def test_preview_compares_secrets_after_decryption(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    await create_data_item(client, project, "ADMIN_PASSWORD", "s3cret", kind="secret")
    file_id = await upload(data_container, project, user_id, "secrets.json", b'{"ADMIN_PASSWORD": "s3cret"}')

    response = await preview(client, project, file_id)

    assert response.json()["items"] == [
        {"key": "ADMIN_PASSWORD", "kind": "secret", "value": None, "action": "unchanged"}
    ]


async def test_preview_compares_against_the_target_environment_only(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await create_data_item(client, project, "USER", "alice")
    file_id = await upload(data_container, project, user_id, "staging.yaml", b"USER: alice\n")

    response = await preview(client, project, file_id, environment_id)

    assert response.json()["format"] == "yaml"
    assert response.json()["items"] == [{"key": "USER", "kind": "variable", "value": "alice", "action": "create"}]


async def test_commit_counts_created_updated_and_unchanged_items(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    await create_data_item(client, project, "USER", "alice")
    await create_data_item(client, project, "LOCALE", "en")
    file_id = await upload(data_container, project, user_id, ".env.staging", DOTENV_CONTENT)

    response = await commit(
        client,
        project,
        file_id,
        [("BASE_URL", "endpoint"), ("USER", "variable"), ("ADMIN_PASSWORD", "secret"), ("LOCALE", "variable")],
    )

    assert response.status_code == 200
    assert response.json() == {"created": 2, "updated": 1, "unchanged": 1}
    listed = (await client.get(f"/api/projects/{project.key}/test-data")).json()
    assert [(item["key"], item["kind"], item["value"]) for item in listed] == [
        ("ADMIN_PASSWORD", "secret", None),
        ("BASE_URL", "endpoint", "https://staging.shop.test"),
        ("LOCALE", "variable", "fr"),
        ("USER", "variable", "alice"),
    ]
    secret_id = next(item["id"] for item in listed if item["key"] == "ADMIN_PASSWORD")
    revealed = await client.post(f"/api/projects/{project.key}/test-data/{secret_id}/reveal")
    assert revealed.json() == {"value": "s3cret"}


async def test_commit_into_an_environment_uses_the_kinds_the_client_chose(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    content = json.dumps({"admin": {"password": "s3cret", "user": "root"}}).encode()
    file_id = await upload(data_container, project, user_id, "admin.json", content)

    response = await commit(client, project, file_id, [("admin.password", "variable")], environment_id)

    assert response.json() == {"created": 1, "updated": 0, "unchanged": 0}
    listed = (await client.get(f"/api/projects/{project.key}/test-data")).json()
    assert [(item["key"], item["kind"], item["value"], item["environmentId"]) for item in listed] == [
        ("admin.password", "variable", "s3cret", environment_id)
    ]


async def test_commit_of_a_key_not_in_the_file_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT)

    response = await commit(client, project, file_id, [("USER", "variable"), ("MISSING", "variable")])

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"
    assert (await client.get(f"/api/projects/{project.key}/test-data")).json() == []


async def test_a_dev_cannot_commit_secrets_or_overwrite_one(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, _ = await set_up_member(client, data_container, recording_mailer)
    await create_data_item(client, project, "USER", "old", kind="secret")
    dev_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.DEV)
    file_id = await upload(data_container, project, dev_id, ".env", DOTENV_CONTENT)

    previewed = await preview(client, project, file_id)
    with_secret = await commit(client, project, file_id, [("ADMIN_PASSWORD", "secret")])
    over_secret = await commit(client, project, file_id, [("USER", "variable")])
    plain = await commit(client, project, file_id, [("LOCALE", "variable"), ("BASE_URL", "endpoint")])

    assert previewed.status_code == 200
    assert with_secret.status_code == 403
    assert over_secret.status_code == 403
    assert plain.json() == {"created": 2, "updated": 0, "unchanged": 0}


async def test_a_viewer_cannot_preview(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, viewer_id = await set_up_member(client, data_container, recording_mailer, ProjectRole.VIEWER)
    file_id = await upload(data_container, project, viewer_id, ".env", DOTENV_CONTENT)

    assert (await preview(client, project, file_id)).status_code == 403


async def test_a_pending_upload_is_not_completed(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT, StoredFileStatus.PENDING)

    previewed = await preview(client, project, file_id)
    committed = await commit(client, project, file_id, [("USER", "variable")])

    assert previewed.status_code == 409
    assert previewed.json()["code"] == "UPLOAD_NOT_COMPLETED"
    assert committed.json()["code"] == "UPLOAD_NOT_COMPLETED"


async def test_a_file_of_another_project_or_kind_is_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    other_project = await seed_project(data_container)
    await add_member(data_container, other_project, user_id, ProjectRole.QC)
    foreign_file_id = await upload(data_container, other_project, user_id, ".env", DOTENV_CONTENT)
    test_file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT, kind=StoredFileKind.TEST_FILE)

    foreign = await preview(client, project, foreign_file_id)
    wrong_kind = await preview(client, project, test_file_id)
    unknown = await preview(client, project, str(UUID(int=5)))

    assert [foreign.status_code, wrong_kind.status_code, unknown.status_code] == [404, 404, 404]
    assert foreign.json()["message"] == "Import file not found."


async def test_a_file_whose_object_is_gone_is_not_found(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT)
    data_container.in_memory_object_storage.contents.clear()

    response = await preview(client, project, file_id)

    assert response.status_code == 404


async def test_a_file_over_one_megabyte_is_too_large(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    large_by_size = await upload(data_container, project, user_id, ".env", b"USER=alice\n", size=1048577)
    large_by_content = await upload(data_container, project, user_id, ".env", b"A=" + b"x" * 1048576, size=10)

    responses = [await preview(client, project, large_by_size), await preview(client, project, large_by_content)]

    assert [response.status_code for response in responses] == [413, 413]
    assert {response.json()["code"] for response in responses} == {"FILE_TOO_LARGE"}


async def test_an_unsupported_or_broken_file_is_invalid(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    text_file_id = await upload(data_container, project, user_id, "notes.txt", b"USER=alice\n")
    list_file_id = await upload(data_container, project, user_id, "list.json", b"[1, 2]")

    responses = [await preview(client, project, text_file_id), await preview(client, project, list_file_id)]

    assert [response.status_code for response in responses] == [422, 422]
    assert {response.json()["code"] for response in responses} == {"IMPORT_INVALID_FILE"}


async def test_an_archived_target_environment_is_refused(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project, user_id = await set_up_member(client, data_container, recording_mailer)
    environment_id = await create_environment(client, project)
    await client.post(f"/api/projects/{project.key}/environments/{environment_id}/archive")
    file_id = await upload(data_container, project, user_id, ".env", DOTENV_CONTENT)

    previewed = await preview(client, project, file_id, environment_id)
    committed = await commit(client, project, file_id, [("USER", "variable")], environment_id)

    assert previewed.status_code == 422
    assert committed.status_code == 422

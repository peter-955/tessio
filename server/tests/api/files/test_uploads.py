from uuid import UUID, uuid4

from httpx import AsyncClient, Response
from sqlalchemy import text

from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.files.conftest import (
    SIGNED_UPLOAD_URL,
    FilesTestContainer,
    SeededProject,
    add_project_member,
    seed_project,
)
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.conftest import RecordingMailer

ALLOWED_FILE_TYPES = ["text/csv", "application/pdf"]
MEGABYTE = 1048576


async def sign_up_member(
    client: AsyncClient,
    files_container: FilesTestContainer,
    recording_mailer: RecordingMailer,
    project: SeededProject,
    role: ProjectRole | None,
) -> UUID:
    account = await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    if role is not None:
        await add_project_member(files_container, project, account.user_id, role)
    return account.user_id


async def request_upload(
    client: AsyncClient,
    project: SeededProject,
    kind: str = "test_file",
    file_name: str = "data set.csv",
    content_type: str = "text/csv",
    size: int = 2048,
) -> Response:
    return await client.post(
        f"/api/projects/{project.key}/uploads",
        json={"kind": kind, "fileName": file_name, "contentType": content_type, "size": size},
    )


async def read_status(files_container: FilesTestContainer, file_id: str) -> str | None:
    async with files_container.database.begin():
        status: str | None = await files_container.database.get_current_session().scalar(
            text("SELECT status FROM stored_files WHERE id = :id"), {"id": UUID(file_id)}
        )
    return status


async def test_allowed_type_returns_a_signed_upload_and_a_pending_row(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)

    response = await request_upload(client, project)

    assert response.status_code == 201
    body = response.json()
    assert body.keys() == {"fileId", "url", "fields", "objectKey"}
    assert body["url"] == SIGNED_UPLOAD_URL
    assert body["objectKey"] == f"projects/{project.id}/test_file/{body['fileId']}/data-set.csv"
    assert body["fields"]["key"] == body["objectKey"]
    assert body["fields"]["Content-Type"] == "text/csv"
    assert body["fields"]["content-type-prefix"] == "text/csv"
    assert body["fields"]["max-bytes"] == "20971520"
    assert await read_status(files_container, body["fileId"]) == "pending"


async def test_disallowed_type_is_refused(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)

    response = await request_upload(client, project, file_name="shot.png", content_type="image/png")

    assert response.status_code == 422
    assert response.json()["code"] == "FILE_TYPE_NOT_ALLOWED"


async def test_screenshot_images_are_always_allowed_as_evidence(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)

    response = await request_upload(client, project, kind="evidence", file_name="shot.png", content_type="image/png")

    assert response.status_code == 201
    assert "/evidence/" in response.json()["objectKey"]


async def test_a_file_over_20_megabytes_is_refused(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)

    response = await request_upload(client, project, size=21 * MEGABYTE)

    assert response.status_code == 413
    assert response.json()["code"] == "FILE_TOO_LARGE"


async def test_an_empty_file_is_an_invalid_request(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)

    response = await request_upload(client, project, size=0)

    assert response.status_code == 422


async def test_a_viewer_cannot_upload_a_test_file(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.VIEWER)

    response = await request_upload(client, project)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_a_non_member_gets_not_found(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, None)

    response = await request_upload(client, project)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_an_archived_project_refuses_uploads(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES, is_archived=True)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.ADMIN)

    response = await request_upload(client, project)

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_archiving_through_the_api_refuses_further_uploads(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    member = await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    await add_project_member(files_container, project, member.user_id, ProjectRole.ADMIN)
    await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.OWNER)
    archive_response = await client.post(f"/api/projects/{project.key}/archive")
    use_session(client, member.session_token)

    response = await request_upload(client, project)

    assert archive_response.status_code == 200
    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_a_workspace_admin_who_is_not_a_member_acts_as_project_admin(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.ADMIN)

    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")
    complete_response = await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")
    download_response = await client.get(f"/api/projects/{project.key}/files/{upload['fileId']}")

    assert complete_response.status_code == 200
    assert download_response.status_code == 200


async def test_upload_requests_need_a_signed_in_user(client: AsyncClient, files_container: FilesTestContainer) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)

    response = await request_upload(client, project)

    assert response.status_code == 401


async def test_complete_waits_for_the_object_then_marks_the_file_uploaded(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    complete_path = f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete"

    early_response = await client.post(complete_path)
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")
    response = await client.post(complete_path)
    repeated_response = await client.post(complete_path)

    assert early_response.status_code == 409
    assert early_response.json()["code"] == "UPLOAD_NOT_COMPLETED"
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == upload["fileId"]
    assert body["kind"] == "test_file"
    assert body["fileName"] == "data set.csv"
    assert body["contentType"] == "text/csv"
    assert body["size"] == 1500
    assert body["status"] == "uploaded"
    assert repeated_response.json() == body


async def test_complete_deletes_an_object_over_the_limit(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 21 * MEGABYTE, "text/csv")

    response = await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")

    assert response.json()["code"] == "FILE_TOO_LARGE"
    assert upload["objectKey"] in files_container.in_memory_object_storage.deleted_keys
    assert await read_status(files_container, upload["fileId"]) == "pending"


async def test_complete_refuses_an_object_of_another_type(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 100, "text/csv-evil")

    response = await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")

    assert response.json()["code"] == "FILE_TYPE_NOT_ALLOWED"
    assert upload["objectKey"] not in files_container.in_memory_object_storage.objects


async def test_only_the_uploader_can_complete(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.ADMIN)

    response = await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")

    assert response.status_code == 404
    assert await read_status(files_container, upload["fileId"]) == "pending"


async def test_complete_of_a_file_in_another_project_is_not_found(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    other_project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    user_id = await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    await add_project_member(files_container, other_project, user_id, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")

    response = await client.post(f"/api/projects/{other_project.key}/uploads/{upload['fileId']}/complete")

    assert response.status_code == 404


async def test_download_link_is_given_only_for_uploaded_files_of_the_project(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    other_project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    user_id = await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    await add_project_member(files_container, other_project, user_id, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    file_path = f"/api/projects/{project.key}/files/{upload['fileId']}"

    pending_response = await client.get(file_path)
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")
    await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")
    response = await client.get(file_path)
    other_project_response = await client.get(f"/api/projects/{other_project.key}/files/{upload['fileId']}")
    unknown_response = await client.get(f"/api/projects/{project.key}/files/{uuid4()}")

    assert pending_response.status_code == 404
    assert response.status_code == 200
    assert response.json()["url"] == f"{SIGNED_UPLOAD_URL}/{upload['objectKey']}?expires=300&name=data set.csv"
    assert response.json()["expiresAt"]
    assert other_project_response.status_code == 404
    assert unknown_response.status_code == 404


async def test_a_viewer_can_download_and_a_non_member_cannot(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")
    await client.post(f"/api/projects/{project.key}/uploads/{upload['fileId']}/complete")
    file_path = f"/api/projects/{project.key}/files/{upload['fileId']}"

    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.VIEWER)
    viewer_response = await client.get(file_path)
    await sign_up_member(client, files_container, recording_mailer, project, None)
    non_member_response = await client.get(file_path)

    assert viewer_response.status_code == 200
    assert non_member_response.status_code == 404


async def test_avatar_upload_accepts_small_images_without_a_project(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    user_id = str((await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)).user_id)

    response = await client.post(
        "/api/me/avatar-upload", json={"fileName": "me.png", "contentType": "image/png", "size": MEGABYTE}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["objectKey"] == f"users/{user_id}/avatar/{body['fileId']}/me.png"
    assert body["fields"]["max-bytes"] == "2097152"
    async with files_container.database.begin():
        project_id = await files_container.database.get_current_session().scalar(
            text("SELECT project_id FROM stored_files WHERE id = :id"), {"id": UUID(body["fileId"])}
        )
    assert project_id is None


async def test_avatar_upload_refuses_other_types_and_large_files(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)

    pdf_response = await client.post(
        "/api/me/avatar-upload", json={"fileName": "me.pdf", "contentType": "application/pdf", "size": 100}
    )
    large_response = await client.post(
        "/api/me/avatar-upload", json={"fileName": "me.png", "contentType": "image/png", "size": 3 * MEGABYTE}
    )

    assert pdf_response.json()["code"] == "FILE_TYPE_NOT_ALLOWED"
    assert large_response.json()["code"] == "FILE_TOO_LARGE"


async def test_avatar_complete_marks_the_avatar_uploaded(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, files_container, recording_mailer, WorkspaceRole.MEMBER)
    upload = (
        await client.post(
            "/api/me/avatar-upload", json={"fileName": "me.webp", "contentType": "image/webp", "size": 4096}
        )
    ).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 4096, "image/webp")

    response = await client.post(f"/api/me/avatar-upload/{upload['fileId']}/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "uploaded"
    assert response.json()["kind"] == "avatar"


async def test_a_project_file_cannot_be_completed_as_an_avatar(
    client: AsyncClient, files_container: FilesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(files_container, ALLOWED_FILE_TYPES)
    await sign_up_member(client, files_container, recording_mailer, project, ProjectRole.QC)
    upload = (await request_upload(client, project)).json()
    files_container.in_memory_object_storage.put(upload["objectKey"], 1500, "text/csv")

    response = await client.post(f"/api/me/avatar-upload/{upload['fileId']}/complete")

    assert response.status_code == 404

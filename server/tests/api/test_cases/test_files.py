from uuid import UUID

from httpx import AsyncClient, Response

from app.modules.files import StoredFileKind, StoredFileStatus
from tests.api.test_cases.case_steps import (
    CaseProject,
    build_step,
    change_status,
    create_case,
    seed_test_file_upload,
    set_up_case_project,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer


async def attach(
    client: AsyncClient, case_project: CaseProject, key: str, file_id: UUID, base_version_number: int
) -> Response:
    return await client.post(
        f"/api/projects/{case_project.key}/test-cases/TC-1/files",
        json={"key": key, "fileId": str(file_id), "baseVersionNumber": base_version_number},
    )


async def set_up_case(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> CaseProject:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key, steps=[build_step("Upload {{file.cv}}")])
    return case_project


async def test_attaching_a_file_creates_file_version_one_and_a_case_version(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    file_id = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)

    response = await attach(client, case_project, "cv", file_id, 1)

    assert response.status_code == 201, response.text
    body = response.json()
    assert [file["key"] for file in body["files"]] == ["cv"]
    file = body["files"][0]
    assert file["versionCount"] == 1
    assert file["currentVersion"]["number"] == 1
    assert file["currentVersion"]["storedFileId"] == str(file_id)
    assert file["currentVersion"]["fileName"] == "invoice.pdf"
    assert file["currentVersion"]["contentType"] == "application/pdf"
    assert file["currentVersion"]["size"] == 1024
    assert body["currentVersion"]["number"] == 2
    assert body["currentVersion"]["fileVersionIds"] == [file["currentVersion"]["id"]]
    assert body["currentVersion"]["steps"][0]["action"] == "Upload {{file.cv}}"
    assert body["unknownReferences"] == []


async def test_the_same_key_adds_a_file_version_and_pins_every_current_file(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    first_file = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    other_file = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    second_file = await seed_test_file_upload(
        test_cases_container, case_project.project, case_project.user_id, file_name="cv-v2.pdf"
    )
    await attach(client, case_project, "cv", first_file, 1)
    await attach(client, case_project, "avatar", other_file, 2)

    response = await attach(client, case_project, "cv", second_file, 3)

    assert response.status_code == 201, response.text
    body = response.json()
    files = {file["key"]: file for file in body["files"]}
    assert [file["key"] for file in body["files"]] == ["avatar", "cv"]
    assert files["cv"]["versionCount"] == 2
    assert files["cv"]["currentVersion"]["number"] == 2
    assert body["currentVersion"]["number"] == 4
    assert body["currentVersion"]["fileVersionIds"] == [
        files["avatar"]["currentVersion"]["id"],
        files["cv"]["currentVersion"]["id"],
    ]
    versions = await client.get(f"/api/projects/{case_project.key}/test-cases/TC-1/files/cv/versions")
    assert [version["number"] for version in versions.json()] == [2, 1]
    assert [version["fileName"] for version in versions.json()] == ["cv-v2.pdf", "invoice.pdf"]
    case_versions = await client.get(f"/api/projects/{case_project.key}/test-cases/TC-1/versions")
    assert [len(version["fileVersionIds"]) for version in case_versions.json()] == [2, 2, 1, 0]


async def test_unknown_file_key_versions_are_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)

    response = await client.get(f"/api/projects/{case_project.key}/test-cases/TC-1/files/cv/versions")

    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "message": "Test file not found."}


async def test_a_file_of_another_project_is_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    other_project = await seed_project(test_cases_container)
    file_id = await seed_test_file_upload(test_cases_container, other_project, case_project.user_id)

    response = await attach(client, case_project, "cv", file_id, 1)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_a_pending_upload_cannot_be_attached(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    file_id = await seed_test_file_upload(
        test_cases_container, case_project.project, case_project.user_id, StoredFileStatus.PENDING
    )

    response = await attach(client, case_project, "cv", file_id, 1)

    assert response.status_code == 409
    assert response.json()["code"] == "UPLOAD_NOT_COMPLETED"


async def test_an_import_file_cannot_be_attached(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    file_id = await seed_test_file_upload(
        test_cases_container, case_project.project, case_project.user_id, kind=StoredFileKind.IMPORT
    )

    response = await attach(client, case_project, "cv", file_id, 1)

    assert response.status_code == 422
    assert response.json() == {"code": "INVALID_REQUEST", "message": "Upload the file as a test file."}


async def test_a_stored_file_is_attached_only_once(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    file_id = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    await attach(client, case_project, "cv", file_id, 1)

    response = await attach(client, case_project, "photo", file_id, 2)

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


async def test_attach_checks_the_base_version_and_keeps_a_ready_case_ready(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    first_file = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    second_file = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    await attach(client, case_project, "cv", first_file, 1)
    await change_status(client, case_project.key, "TC-1", "in_review")
    await change_status(client, case_project.key, "TC-1", "ready")

    stale = await attach(client, case_project, "cv", second_file, 1)
    response = await attach(client, case_project, "cv", second_file, 2)

    assert stale.status_code == 409
    assert stale.json()["code"] == "CONFLICT"
    assert response.status_code == 201
    assert response.json()["status"] == "ready"


async def test_invalid_file_keys_are_rejected(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case(client, test_cases_container, recording_mailer)
    file_id = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)

    response = await attach(client, case_project, "1 bad key", file_id, 1)

    assert response.status_code == 422

from httpx import AsyncClient

from app.shared.permissions import ProjectRole
from tests.api.test_data.conftest import DataTestContainer
from tests.api.test_data.project_steps import seed_import_file, seed_project, sign_up_member
from tests.conftest import RecordingMailer

DOTENV_CONTENT = b"BASE_URL=https://staging.shop.test\nADMIN_PASSWORD=s3cret\n"


async def test_another_members_import_file_cannot_be_previewed_or_committed(
    client: AsyncClient, data_container: DataTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(data_container)
    uploader_id = await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.QC)
    file_id = await seed_import_file(
        data_container, data_container.in_memory_object_storage, project, uploader_id, ".env", DOTENV_CONTENT
    )
    await sign_up_member(client, data_container, recording_mailer, project, ProjectRole.ADMIN)

    preview_response = await client.post(
        f"/api/projects/{project.key}/test-data/import/preview", json={"fileId": str(file_id), "environmentId": None}
    )
    commit_response = await client.post(
        f"/api/projects/{project.key}/test-data/import/commit",
        json={"fileId": str(file_id), "environmentId": None, "items": [{"key": "BASE_URL", "kind": "variable"}]},
    )

    assert preview_response.status_code == 404
    assert preview_response.json()["code"] == "NOT_FOUND"
    assert commit_response.status_code == 404
    assert commit_response.json()["code"] == "NOT_FOUND"

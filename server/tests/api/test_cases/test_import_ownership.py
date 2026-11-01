from httpx import AsyncClient

from app.shared.permissions import ProjectRole
from tests.api.test_cases.case_steps import set_up_case_project
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import seed_import_file, sign_up_member
from tests.conftest import RecordingMailer


async def test_another_members_case_import_cannot_be_previewed_or_committed(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    file_id = await seed_import_file(
        test_cases_container,
        test_cases_container.in_memory_object_storage,
        case_project.project,
        case_project.user_id,
        "cases.csv",
        b"Story;Title;Step\nX-1;Pay;Open cart\n",
    )
    await sign_up_member(client, test_cases_container, recording_mailer, case_project.project, ProjectRole.ADMIN)

    preview_response = await client.post(
        f"/api/projects/{case_project.key}/test-case-imports/preview", json={"fileId": str(file_id)}
    )
    commit_response = await client.post(
        f"/api/projects/{case_project.key}/test-case-imports/commit", json={"fileId": str(file_id), "indexes": [0]}
    )

    assert preview_response.status_code == 404
    assert preview_response.json()["code"] == "NOT_FOUND"
    assert commit_response.status_code == 404
    assert commit_response.json()["code"] == "NOT_FOUND"

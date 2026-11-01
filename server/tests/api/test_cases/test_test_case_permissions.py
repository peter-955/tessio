from uuid import UUID

import pytest
from httpx import AsyncClient, Response

from app.shared.permissions import ProjectRole
from tests.api.test_cases.case_steps import (
    CaseProject,
    build_step,
    build_xlsx,
    create_case,
    create_case_code,
    seed_test_file_upload,
    set_up_case_project,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import archive_project, seed_import_file, sign_up_member
from tests.conftest import RecordingMailer

EDITOR_ROLES = {ProjectRole.ADMIN, ProjectRole.QC}


async def set_up_project_with_case(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> CaseProject:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer, role=ProjectRole.ADMIN)
    await create_case_code(client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")])
    return case_project


async def read_everything(client: AsyncClient, case_project: CaseProject) -> list[Response]:
    base = f"/api/projects/{case_project.key}/test-cases"
    return [
        await client.get(base),
        await client.get(f"{base}/TC-1"),
        await client.get(f"{base}/TC-1/versions"),
    ]


async def write_everything(
    client: AsyncClient, test_cases_container: CasesContainer, case_project: CaseProject, importer_id: UUID
) -> list[Response]:
    base = f"/api/projects/{case_project.key}"
    test_file_id = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    import_file_id = await seed_import_file(
        test_cases_container,
        test_cases_container.in_memory_object_storage,
        case_project.project,
        importer_id,
        "cases.xlsx",
        build_xlsx({case_project.story.jira_key: [["Title", "Step"], ["Imported", "Do it"]]}),
    )
    return [
        await create_case(client, case_project.key, case_project.story.jira_key),
        await client.patch(f"{base}/test-cases/TC-1", json={"baseVersionNumber": 1, "title": "Changed"}),
        await client.put(f"{base}/test-cases/TC-1/status", json={"status": "in_review"}),
        await client.post(f"{base}/test-cases/TC-1/review"),
        await client.post(
            f"{base}/test-cases/TC-1/files",
            json={"key": "invoice", "fileId": str(test_file_id), "baseVersionNumber": 2},
        ),
        await client.post(f"{base}/test-case-imports/preview", json={"fileId": str(import_file_id)}),
        await client.post(f"{base}/test-case-imports/commit", json={"fileId": str(import_file_id), "indexes": [0]}),
    ]


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_member_reads_test_cases(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    case_project = await set_up_project_with_case(client, test_cases_container, recording_mailer)
    await sign_up_member(client, test_cases_container, recording_mailer, case_project.project, role)

    responses = await read_everything(client, case_project)

    assert [response.status_code for response in responses] == [200, 200, 200]


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_only_admins_and_qc_write_test_cases(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    case_project = await set_up_project_with_case(client, test_cases_container, recording_mailer)
    member_id = await sign_up_member(client, test_cases_container, recording_mailer, case_project.project, role)

    responses = await write_everything(client, test_cases_container, case_project, member_id)

    statuses = [response.status_code for response in responses]
    if role in EDITOR_ROLES:
        assert statuses == [201, 200, 200, 200, 201, 200, 201], [response.text for response in responses]
    else:
        assert statuses == [403] * 7
        assert {response.json()["code"] for response in responses} == {"PERMISSION_DENIED"}


async def test_a_non_member_gets_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_project_with_case(client, test_cases_container, recording_mailer)
    outsider_id = await sign_up_member(client, test_cases_container, recording_mailer, case_project.project, None)

    responses = [
        *await read_everything(client, case_project),
        *await write_everything(client, test_cases_container, case_project, outsider_id),
    ]

    assert {response.status_code for response in responses} == {404}


async def test_an_archived_project_is_read_only(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_project_with_case(client, test_cases_container, recording_mailer)
    await archive_project(test_cases_container, case_project.project)

    reads = await read_everything(client, case_project)
    writes = await write_everything(client, test_cases_container, case_project, case_project.user_id)

    assert [response.status_code for response in reads] == [200, 200, 200]
    assert {response.status_code for response in writes} == {409}
    assert {response.json()["code"] for response in writes} == {"PROJECT_ARCHIVED"}

import pytest
from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.labels.label_steps import (
    create_label,
    create_label_id,
    delete_label,
    set_case_labels,
    update_label,
)
from tests.api.test_cases.case_steps import CaseProject, create_case_code, set_up_case_project
from tests.api.test_data.project_steps import archive_project, sign_up_member
from tests.conftest import RecordingMailer

EDITOR_ROLES = {ProjectRole.ADMIN, ProjectRole.QC}


async def set_up_labelled_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[CaseProject, str]:
    case_project = await set_up_case_project(client, container, recording_mailer, role=ProjectRole.ADMIN)
    label_id = await create_label_id(client, case_project.key, "Smoke")
    await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, "TC-1", [label_id])
    return case_project, label_id


async def read_labels(client: AsyncClient, case_project: CaseProject) -> list[Response]:
    base = f"/api/projects/{case_project.key}"
    return [
        await client.get(f"{base}/labels"),
        await client.get(f"{base}/test-cases", params={"label": "Smoke"}),
    ]


async def write_labels(client: AsyncClient, case_project: CaseProject, label_id: str) -> list[Response]:
    return [
        await create_label(client, case_project.key, "Checkout"),
        await update_label(client, case_project.key, label_id, color="red"),
        await set_case_labels(client, case_project.key, "TC-1", []),
        await delete_label(client, case_project.key, label_id),
    ]


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_member_reads_labels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    case_project, _ = await set_up_labelled_case(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, case_project.project, role)

    responses = await read_labels(client, case_project)

    assert [response.status_code for response in responses] == [200, 200]
    assert [label["name"] for label in responses[0].json()] == ["Smoke"]
    assert [case["code"] for case in responses[1].json()] == ["TC-1"]


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_only_admins_and_qc_change_labels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    case_project, label_id = await set_up_labelled_case(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, case_project.project, role)

    responses = await write_labels(client, case_project, label_id)

    statuses = [response.status_code for response in responses]
    if role in EDITOR_ROLES:
        assert statuses == [201, 200, 200, 204], [response.text for response in responses]
    else:
        assert statuses == [403] * 4
        assert {response.json()["code"] for response in responses} == {"PERMISSION_DENIED"}


async def test_a_non_member_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project, label_id = await set_up_labelled_case(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, case_project.project, None)

    responses = [*await read_labels(client, case_project), *await write_labels(client, case_project, label_id)]

    assert {response.status_code for response in responses} == {404}


async def test_an_archived_project_keeps_labels_read_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project, label_id = await set_up_labelled_case(client, container, recording_mailer)
    await archive_project(container, case_project.project)

    reads = await read_labels(client, case_project)
    writes = await write_labels(client, case_project, label_id)

    assert [response.status_code for response in reads] == [200, 200]
    assert {response.status_code for response in writes} == {409}
    assert {response.json()["code"] for response in writes} == {"PROJECT_ARCHIVED"}


async def test_a_label_of_another_project_cannot_be_changed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, other_label_id = await set_up_labelled_case(client, container, recording_mailer)
    case_project = await set_up_case_project(client, container, recording_mailer)

    responses = [
        await update_label(client, case_project.key, other_label_id, name="Mine"),
        await delete_label(client, case_project.key, other_label_id),
    ]

    assert [response.status_code for response in responses] == [404, 404]

import pytest
from httpx import AsyncClient

from app.shared.permissions import ProjectRole
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_cases.review_comment_steps import (
    act_as,
    add_comment,
    add_comment_id,
    list_comments,
    resolve_comment,
    set_up_review_project,
    sign_up_project_member,
)
from tests.api.test_data.project_steps import archive_project, sign_up_member
from tests.conftest import RecordingMailer

EDITOR_ROLES = {ProjectRole.ADMIN, ProjectRole.QC}


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_member_reads_and_only_admins_and_qc_write_review_comments(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    comment_id = await add_comment_id(client, review_project)
    member = await sign_up_project_member(
        client, test_cases_container, recording_mailer, review_project.project, role, "Mia Member"
    )
    act_as(client, member)

    listed = await client.get(review_project.comments_path)
    added = await add_comment(client, review_project)
    resolved = await resolve_comment(client, review_project, comment_id)

    assert listed.status_code == 200
    if role in EDITOR_ROLES:
        assert [added.status_code, resolved.status_code] == [201, 200]
    else:
        assert [added.status_code, resolved.status_code] == [403, 403]
        assert {added.json()["code"], resolved.json()["code"]} == {"PERMISSION_DENIED"}


async def test_a_non_member_gets_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    comment_id = await add_comment_id(client, review_project)
    await sign_up_member(client, test_cases_container, recording_mailer, review_project.project, None)

    responses = [
        await client.get(review_project.comments_path),
        await add_comment(client, review_project),
        await resolve_comment(client, review_project, comment_id),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]


async def test_an_archived_project_keeps_comments_readable_and_refuses_writes(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    comment_id = await add_comment_id(client, review_project)
    await archive_project(test_cases_container, review_project.project)

    comments = await list_comments(client, review_project)
    added = await add_comment(client, review_project)
    resolved = await resolve_comment(client, review_project, comment_id)

    assert len(comments) == 1
    assert [added.status_code, resolved.status_code] == [409, 409]
    assert {added.json()["code"], resolved.json()["code"]} == {"PROJECT_ARCHIVED"}

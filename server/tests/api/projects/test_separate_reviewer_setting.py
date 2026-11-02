from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.test_cases.review_comment_steps import sign_up_project_member
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer


async def test_the_project_admin_turns_the_separate_reviewer_rule_on_and_off(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.ADMIN, "Ann Admin")
    path = f"/api/projects/{project.key}"

    initial = await client.get(path)
    turned_on = await client.patch(path, json={"requireSeparateReviewer": True})
    renamed = await client.patch(path, json={"name": "Renamed"})
    turned_off = await client.patch(path, json={"requireSeparateReviewer": False})

    assert initial.status_code == 200
    assert initial.json()["requireSeparateReviewer"] is False
    assert turned_on.status_code == 200, turned_on.text
    assert turned_on.json()["requireSeparateReviewer"] is True
    assert renamed.json()["requireSeparateReviewer"] is True
    assert turned_off.json()["requireSeparateReviewer"] is False


async def test_only_the_project_admin_changes_the_separate_reviewer_rule(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    admin = await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.ADMIN, "Ann Admin")
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.QC, "Quinn QC")
    path = f"/api/projects/{project.key}"

    by_qc = await client.patch(path, json={"requireSeparateReviewer": True})
    use_session(client, admin.session_token)
    after = await client.get(path)

    assert by_qc.status_code == 403
    assert by_qc.json()["code"] == "PERMISSION_DENIED"
    assert after.json()["requireSeparateReviewer"] is False

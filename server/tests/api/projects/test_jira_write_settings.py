from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.projects.infrastructure import ProjectTable
from app.shared.permissions import ProjectRole
from tests.api.test_cases.review_comment_steps import sign_up_project_member
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer


async def unlink_from_jira(container: Container, project: SeededProject) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(jira_project_key=None, jira_board_id=None)
        )


async def test_the_project_admin_sets_the_bug_issue_type_and_when_results_are_posted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.ADMIN, "Ann Admin")
    path = f"/api/projects/{project.key}"

    initial = await client.get(path)
    changed = await client.patch(path, json={"jiraBugIssueType": "  Defect ", "jiraPostResults": "every_run"})
    renamed = await client.patch(path, json={"name": "Renamed"})

    assert initial.json()["jiraBugIssueType"] == "Bug"
    assert initial.json()["jiraPostResults"] == "off"
    assert changed.status_code == 200, changed.text
    assert changed.json()["jiraBugIssueType"] == "Defect"
    assert changed.json()["jiraPostResults"] == "every_run"
    assert renamed.json()["jiraBugIssueType"] == "Defect"
    assert renamed.json()["jiraPostResults"] == "every_run"


async def test_invalid_jira_settings_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.ADMIN, "Ann Admin")
    path = f"/api/projects/{project.key}"

    for body in ({"jiraPostResults": "sometimes"}, {"jiraBugIssueType": "   "}, {"jiraBugIssueType": "x" * 61}):
        response = await client.patch(path, json=body)

        assert response.status_code == 422, body
        assert "detail" in response.json()


async def test_a_project_without_jira_cannot_set_jira_write_settings(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await unlink_from_jira(container, project)
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.ADMIN, "Ann Admin")
    path = f"/api/projects/{project.key}"

    issue_type = await client.patch(path, json={"jiraBugIssueType": "Defect"})
    post_results = await client.patch(path, json={"jiraPostResults": "on_sign_off"})

    assert issue_type.status_code == 409
    assert issue_type.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert post_results.status_code == 409


async def test_only_the_project_admin_changes_the_jira_write_settings(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_project_member(client, container, recording_mailer, project, ProjectRole.QC, "Quinn QC")

    response = await client.patch(f"/api/projects/{project.key}", json={"jiraPostResults": "every_run"})

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"

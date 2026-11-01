from httpx import AsyncClient, Response

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import (
    add_active_member,
    answer_gap,
    raise_gap_id,
    seed_story,
    seed_test_case,
    sign_up_account,
)
from tests.api.projects.user_steps import deactivate_user, use_session
from tests.api.test_data.project_steps import add_member, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer


def read_ids(response: Response) -> list[str]:
    assert response.status_code == 200, response.text
    return [gap["id"] for gap in response.json()]


async def test_project_list_filters_by_story_status_and_assignee(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    first_story = await seed_story(container, project, criterion_codes=("AC1",))
    second_story = await seed_story(container, project)
    analyst = await sign_up_account(client, container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    tester = await sign_up_account(client, container, recording_mailer, project, ProjectRole.QC, "Quinn Tester")
    await add_active_member(container, recording_mailer, project, ProjectRole.QC, "Second Tester")
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.PM)
    direct_id = await raise_gap_id(client, project.key, first_story, targetType="criterion", targetRef="AC1")
    queued_id = await raise_gap_id(client, project.key, first_story, type="missing_step")
    resolved_id = await raise_gap_id(client, project.key, second_story)
    assert (await answer_gap(client, project.key, resolved_id)).status_code == 200
    gaps_url = f"/api/projects/{project.key}/gaps"

    all_ids = read_ids(await client.get(gaps_url))
    story_ids = read_ids(await client.get(gaps_url, params={"storyKey": first_story.jira_key.lower()}))
    open_ids = read_ids(await client.get(gaps_url, params={"status": "open"}))
    resolved_ids = read_ids(await client.get(gaps_url, params={"status": "resolved"}))
    use_session(client, analyst.session_token)
    analyst_ids = read_ids(await client.get(gaps_url, params={"mine": "true"}))
    analyst_open_ids = read_ids(await client.get(gaps_url, params={"mine": "true", "status": "open"}))
    use_session(client, tester.session_token)
    tester_ids = read_ids(await client.get(gaps_url, params={"mine": "true"}))

    assert all_ids == [resolved_id, queued_id, direct_id]
    assert story_ids == [queued_id, direct_id]
    assert open_ids == [queued_id, direct_id]
    assert resolved_ids == [resolved_id]
    assert analyst_ids == [resolved_id, direct_id]
    assert analyst_open_ids == [direct_id]
    assert tester_ids == [queued_id]


async def test_project_list_shows_target_codes_names_and_assignee_status(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1", "AC2"))
    analyst_id = await add_active_member(container, recording_mailer, project, ProjectRole.BA, "Bao Analyst")
    raiser_id = await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await seed_test_case(container, project, story.id, 7, raiser_id)
    criterion_gap_id = await raise_gap_id(client, project.key, story, targetType="criterion", targetRef="AC2")
    case_gap_id = await raise_gap_id(client, project.key, story, targetType="test_case", targetRef="TC-7")
    await deactivate_user(container, analyst_id)

    response = await client.get(f"/api/projects/{project.key}/gaps")

    gaps_by_id = {gap["id"]: gap for gap in response.json()}
    assert gaps_by_id[criterion_gap_id]["targetRef"] == "AC2"
    assert gaps_by_id[case_gap_id]["targetRef"] == "TC-7"
    assert gaps_by_id[criterion_gap_id]["assigneeName"] == "Bao Analyst"
    assert gaps_by_id[criterion_gap_id]["assigneeStatus"] == "deactivated"
    assert gaps_by_id[criterion_gap_id]["raisedByName"] == "Test User"
    assert gaps_by_id[criterion_gap_id]["isRaisedViaClaude"] is False


async def test_project_list_refuses_unknown_story_and_non_members(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)

    unknown_story = await client.get(f"/api/projects/{project.key}/gaps", params={"storyKey": "NOPE-1"})
    await sign_up_member(client, container, recording_mailer, project, None)
    non_member = await client.get(f"/api/projects/{project.key}/gaps")

    assert unknown_story.status_code == 404
    assert unknown_story.json() == {"code": "NOT_FOUND", "message": "Story not found."}
    assert non_member.status_code == 404


async def test_viewers_read_gaps_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    gap_id = await raise_gap_id(client, project.key, story)
    await archive_project(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.VIEWER)

    response = await client.get(f"/api/projects/{project.key}/gaps")

    assert read_ids(response) == [gap_id]


async def test_inbox_lists_direct_and_role_queue_gaps_across_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    first_project = await seed_project(container)
    second_project = await seed_project(container)
    archived_project = await seed_project(container)
    first_story = await seed_story(container, first_project)
    second_story = await seed_story(container, second_project)
    archived_story = await seed_story(container, archived_project)
    member = await sign_up_account(client, container, recording_mailer, first_project, ProjectRole.BA, "Ina Inbox")
    await add_member(container, second_project, member.user_id, ProjectRole.BA)
    await add_member(container, archived_project, member.user_id, ProjectRole.BA)
    await add_active_member(container, recording_mailer, second_project, ProjectRole.BA, "Other Analyst")
    await add_active_member(container, recording_mailer, first_project, ProjectRole.QC, "Quinn Tester")
    await sign_up_member(client, container, recording_mailer, first_project, None, WorkspaceRole.ADMIN)
    direct_id = await raise_gap_id(client, first_project.key, first_story)
    await raise_gap_id(client, first_project.key, first_story, type="missing_step")
    queued_id = await raise_gap_id(client, second_project.key, second_story)
    resolved_id = await raise_gap_id(client, second_project.key, second_story, assigneeId=str(member.user_id))
    assert (await answer_gap(client, second_project.key, resolved_id)).status_code == 200
    await raise_gap_id(client, archived_project.key, archived_story)
    await archive_project(container, archived_project)
    use_session(client, member.session_token)

    open_response = await client.get("/api/gaps/inbox")
    all_response = await client.get("/api/gaps/inbox", params={"includeResolved": "true"})

    assert read_ids(open_response) == [queued_id, direct_id]
    assert read_ids(all_response) == [resolved_id, queued_id, direct_id]
    first_gap = open_response.json()[0]
    assert first_gap["projectKey"] == second_project.key
    assert first_gap["projectName"] == f"Project {second_project.key}"
    assert first_gap["storyJiraKey"] == second_story.jira_key
    assert first_gap["assigneeRole"] == "ba"


async def test_inbox_needs_a_session(client: AsyncClient) -> None:
    client.cookies.clear()

    response = await client.get("/api/gaps/inbox")

    assert response.status_code == 401

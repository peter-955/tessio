from httpx import AsyncClient

from app.container import Container
from app.modules.stories import TestStatus as StoryTestStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import seed_story, sign_up_account
from tests.api.projects.user_steps import use_session
from tests.api.runs.junit_import.junit_import_steps import import_junit
from tests.api.runs.run_steps import seed_environment, seed_runnable_story
from tests.api.stories.story_steps import set_test_status
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def find_events(publisher: RecordingLiveEventPublisher, event_type: LiveEventType) -> list[dict[str, str]]:
    return [event.ids for event in publisher.events if event.type is event_type]


async def test_raising_a_gap_and_signing_off_a_story_publish_their_events(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    signed_off_story = await seed_story(container, project)
    await set_test_status(container, project, signed_off_story.jira_key, StoryTestStatus.IN_TEST)
    qc = await sign_up_account(client, container, recording_mailer, project, ProjectRole.QC)
    use_session(client, qc.session_token)

    raised = await client.post(
        f"/api/projects/{project.key}/stories/{story.jira_key}/gaps",
        json={"type": "missing_ac", "question": "Which currencies?"},
    )
    signed_off = await client.put(
        f"/api/projects/{project.key}/stories/{signed_off_story.jira_key}/test-status", json={"testStatus": "passed"}
    )

    assert raised.status_code == 201, raised.text
    assert signed_off.status_code == 200, signed_off.text
    assert find_events(recording_live_event_publisher, LiveEventType.GAP_RAISED) == [
        {"gapId": raised.json()["id"], "storyId": str(story.id)}
    ]
    assert find_events(recording_live_event_publisher, LiveEventType.STORY_SIGNED_OFF) == [
        {"storyId": str(signed_off_story.id), "jiraKey": signed_off_story.jira_key}
    ]


async def test_changing_a_failure_status_publishes_failure_status_changed(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(container)
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    story = await seed_runnable_story(container, project, admin.user_id, 1, 1)
    await seed_environment(container, project)
    use_session(client, admin.session_token)
    imported = await import_junit(
        client, project.key, b"<testsuite><testcase name='TC-1'><failure message='boom'/></testcase></testsuite>"
    )
    failure_id = (await client.get(f"/api/projects/{project.key}/failures")).json()[0]["id"]

    fixed = await client.put(f"/api/projects/{project.key}/failures/{failure_id}/status", json={"status": "fixed"})
    reimported = await import_junit(
        client, project.key, b"<testsuite><testcase name='TC-1'><failure message='again'/></testcase></testsuite>"
    )

    assert imported.status_code == 201, imported.text
    assert fixed.status_code == 200, fixed.text
    assert reimported.status_code == 201, reimported.text
    assert find_events(recording_live_event_publisher, LiveEventType.FAILURE_STATUS_CHANGED) == [
        {
            "failureId": failure_id,
            "status": "fixed",
            "storyId": str(story.story_id),
            "testCaseId": str(story.case_ids[0]),
        },
        {
            "failureId": failure_id,
            "status": "reopened",
            "storyId": str(story.story_id),
            "testCaseId": str(story.case_ids[0]),
        },
    ]

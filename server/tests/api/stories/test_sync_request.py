from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient

from app.modules.projects import JiraConnectionChecker
from app.modules.projects.infrastructure import StaticJiraConnectionChecker
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.stories.story_steps import set_sync_state
from tests.api.test_data.project_steps import archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_sync_request_is_queued_once_and_announced(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project = await seed_project(stories_container)
    user_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.BA)

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert body["queuedAt"] is not None
    assert body["startedAt"] is None
    assert body["errorCode"] is None
    jobs = stories_container.recording_job_queue.jobs
    assert len(jobs) == 1
    assert jobs[0].queue_name is QueueName.JIRA
    assert jobs[0].job_name is JobName.JIRA_SYNC_PROJECT
    assert jobs[0].data == {"projectId": str(project.id)}
    assert jobs[0].job_id == f"jira-sync:{project.id}"
    started_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.JIRA_SYNC_STARTED
    ]
    assert len(started_events) == 1
    assert started_events[0].project_id == project.id
    assert started_events[0].ids == {"projectKey": project.key}
    status_response = await client.get(f"/api/projects/{project.key}/sync")
    assert status_response.json()["status"] == "queued"
    async with stories_container.database.begin():
        state = await stories_container.project_sync_state_repository.find(project.id)
    assert state is not None
    assert state.requested_by == user_id


async def test_a_second_request_while_queued_records_no_new_job(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.PM)
    first = await client.post(f"/api/projects/{project.key}/sync")

    second = await client.post(f"/api/projects/{project.key}/sync")

    assert second.status_code == 202
    assert second.json() == first.json()
    assert len(stories_container.recording_job_queue.jobs) == 1


@pytest.mark.parametrize("status", [ProjectSyncStatus.QUEUED, ProjectSyncStatus.RUNNING])
async def test_a_stale_request_is_enqueued_again(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    status: ProjectSyncStatus,
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    stale_at = datetime.now(UTC) - timedelta(minutes=16)
    await set_sync_state(stories_container, project, status, stale_at)

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert datetime.fromisoformat(response.json()["queuedAt"]) > stale_at
    assert len(stories_container.recording_job_queue.jobs) == 1


async def test_a_recent_request_is_not_enqueued_again(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await set_sync_state(
        stories_container, project, ProjectSyncStatus.QUEUED, datetime.now(UTC) - timedelta(minutes=14)
    )

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == 202
    assert stories_container.recording_job_queue.jobs == []


async def test_a_sync_needs_a_jira_connection(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    checker: JiraConnectionChecker = StaticJiraConnectionChecker(is_configured=False)
    stories_container.__dict__["jira_connection_checker"] = checker

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == 409
    assert response.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert stories_container.recording_job_queue.jobs == []


async def test_an_archived_project_cannot_sync(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await archive_project(stories_container, project)

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"
    assert stories_container.recording_job_queue.jobs == []


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (ProjectRole.ADMIN, 202),
        (ProjectRole.PM, 202),
        (ProjectRole.BA, 202),
        (ProjectRole.QC, 403),
        (ProjectRole.DEV, 403),
        (ProjectRole.VIEWER, 403),
        (None, 404),
    ],
)
async def test_only_admins_pms_and_bas_can_sync(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    role: ProjectRole | None,
    expected_status: int,
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, role)

    response = await client.post(f"/api/projects/{project.key}/sync")

    assert response.status_code == expected_status
    assert len(stories_container.recording_job_queue.jobs) == (1 if expected_status == 202 else 0)


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_the_sync_status_is_never_before_the_first_sync(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, role)

    response = await client.get(f"/api/projects/{project.key}/sync")

    assert response.status_code == 200
    assert response.json() == {
        "status": "never",
        "queuedAt": None,
        "startedAt": None,
        "finishedAt": None,
        "lastSucceededAt": None,
        "errorCode": None,
    }


async def test_a_non_member_cannot_read_the_sync_status(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(stories_container)
    await sign_up_member(client, stories_container, recording_mailer, project, None)

    response = await client.get(f"/api/projects/{project.key}/sync")

    assert response.status_code == 404

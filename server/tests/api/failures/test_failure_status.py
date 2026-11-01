from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.failures import FailureEventKind, FailureStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import (
    FailureScenario,
    change_status,
    find_only_failure,
    list_event_rows,
    open_failure,
    seed_scenario,
    set_failure_status,
)
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.test_data.project_steps import archive_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_failure(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    status: FailureStatus = FailureStatus.OPEN,
) -> tuple[FailureScenario, UUID]:
    scenario = await seed_scenario(client, container, recording_mailer)
    failure_id = await open_failure(container, scenario)
    if status is not FailureStatus.OPEN:
        await set_failure_status(container, failure_id, status)
    return scenario, failure_id


def list_failure_changed_ids(recording_live_event_publisher: RecordingLiveEventPublisher) -> list[str]:
    return [
        event.ids["failureId"]
        for event in recording_live_event_publisher.events
        if event.type is LiveEventType.FAILURE_CHANGED
    ]


@pytest.mark.parametrize("current", [FailureStatus.OPEN, FailureStatus.REOPENED])
async def test_dev_marks_a_failure_fixed(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    current: FailureStatus,
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer, current)
    developer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV, "Dee Dev")

    response = await change_status(client, scenario.project.key, failure_id, "fixed")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "fixed"
    assert body["isActive"] is True
    assert body["statusChangedByName"] == "Dee Dev"
    assert body["statusChangedAt"] is not None
    row = await find_only_failure(container, scenario.case.id)
    assert row.status is FailureStatus.FIXED
    assert row.status_changed_by == developer.user_id
    events = await list_event_rows(container, failure_id)
    assert (events[-1].kind, events[-1].from_status, events[-1].to_status, events[-1].actor_id) == (
        FailureEventKind.STATUS_CHANGED,
        current,
        FailureStatus.FIXED,
        developer.user_id,
    )
    assert list_failure_changed_ids(recording_live_event_publisher) == [str(failure_id)]


@pytest.mark.parametrize("target", ["verified", "reopened"])
async def test_qc_verifies_or_reopens_a_fixed_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, target: str
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer, FailureStatus.FIXED)
    tester = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC, "Quinn QC")

    response = await change_status(client, scenario.project.key, failure_id, target)

    assert response.status_code == 200, response.text
    assert response.json()["status"] == target
    assert response.json()["isActive"] is (target == "reopened")
    events = await list_event_rows(container, failure_id)
    assert (events[-1].from_status, events[-1].to_status, events[-1].actor_id) == (
        FailureStatus.FIXED,
        FailureStatus(target),
        tester.user_id,
    )


async def test_admin_can_fix_and_verify(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.ADMIN)

    fixed = await change_status(client, scenario.project.key, failure_id, "fixed")
    verified = await change_status(client, scenario.project.key, failure_id, "verified")

    assert fixed.status_code == 200, fixed.text
    assert verified.status_code == 200, verified.text
    assert [event.kind for event in await list_event_rows(container, failure_id)] == [
        FailureEventKind.OPENED,
        FailureEventKind.STATUS_CHANGED,
        FailureEventKind.STATUS_CHANGED,
    ]


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (FailureStatus.OPEN, "verified"),
        (FailureStatus.OPEN, "reopened"),
        (FailureStatus.REOPENED, "verified"),
        (FailureStatus.FIXED, "fixed"),
        (FailureStatus.VERIFIED, "fixed"),
        (FailureStatus.VERIFIED, "verified"),
        (FailureStatus.VERIFIED, "reopened"),
    ],
)
async def test_other_transitions_are_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    current: FailureStatus,
    target: str,
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer, current)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.ADMIN)

    response = await change_status(client, scenario.project.key, failure_id, target)

    assert response.status_code == 409
    assert response.json() == {
        "code": "INVALID_STATUS_TRANSITION",
        "message": "This failure status change is not allowed.",
    }
    assert (await find_only_failure(container, scenario.case.id)).status is current
    assert len(await list_event_rows(container, failure_id)) == 1
    assert list_failure_changed_ids(recording_live_event_publisher) == []


async def test_status_cannot_be_set_back_to_open(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer, FailureStatus.FIXED)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.ADMIN)

    response = await change_status(client, scenario.project.key, failure_id, "open")
    unknown = await change_status(client, scenario.project.key, failure_id, "closed")

    assert response.status_code == 422
    assert unknown.status_code == 422
    assert (await find_only_failure(container, scenario.case.id)).status is FailureStatus.FIXED


@pytest.mark.parametrize(
    ("role", "current", "target"),
    [
        *[
            (role, current, target)
            for role in (ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER)
            for current, target in (
                (FailureStatus.OPEN, "fixed"),
                (FailureStatus.FIXED, "verified"),
                (FailureStatus.FIXED, "reopened"),
            )
        ],
        (ProjectRole.QC, FailureStatus.OPEN, "fixed"),
        (ProjectRole.QC, FailureStatus.REOPENED, "fixed"),
        (ProjectRole.DEV, FailureStatus.FIXED, "verified"),
        (ProjectRole.DEV, FailureStatus.FIXED, "reopened"),
    ],
)
async def test_roles_without_the_capability_are_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole,
    current: FailureStatus,
    target: str,
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer, current)
    await sign_up_member(client, container, recording_mailer, scenario.project, role)

    response = await change_status(client, scenario.project.key, failure_id, target)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"
    assert (await find_only_failure(container, scenario.case.id)).status is current


async def test_a_non_member_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, scenario.project, None)

    response = await change_status(client, scenario.project.key, failure_id, "fixed")

    assert response.status_code == 404


async def test_an_unknown_failure_gets_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, _ = await seed_failure(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.ADMIN)

    response = await change_status(client, scenario.project.key, uuid4(), "fixed")

    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "message": "Failure not found."}


async def test_an_archived_project_refuses_status_changes(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario, failure_id = await seed_failure(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.DEV)
    await archive_project(container, scenario.project)

    response = await change_status(client, scenario.project.key, failure_id, "fixed")

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.modules.runs import ResultStatus
from app.modules.test_cases.infrastructure import TestCaseTable as CaseTable
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.test_cases.case_steps import set_up_case_project
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_cases.flaky_steps import (
    FlakyCase,
    create_flaky_case,
    get_case_json,
    list_case_codes,
    list_quarantine_events,
    quarantine,
    recompute,
    release,
    seed_history,
    seed_result,
)
from tests.api.test_data.project_steps import sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher

QUARANTINE_ROLES = {ProjectRole.ADMIN, ProjectRole.QC}


async def move_quarantine_back(container: CasesContainer, flaky_case: FlakyCase, age: timedelta) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(CaseTable)
            .where(CaseTable.id == flaky_case.test_case_id)
            .values(quarantined_at=datetime.now(UTC) - age)
        )


async def test_qc_quarantines_a_case_with_a_reason_and_releases_it(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    other_case = await create_flaky_case(client, test_cases_container, case_project)
    recording_live_event_publisher.events.clear()

    quarantined = await quarantine(client, flaky_case, "  Fails on slow networks  ")

    assert quarantined.status_code == 200, quarantined.text
    body = quarantined.json()
    assert (body["isQuarantined"], body["quarantineReason"], body["quarantinedBy"]) == (
        True,
        "Fails on slow networks",
        str(case_project.user_id),
    )
    assert body["quarantinedAt"] is not None
    assert await list_case_codes(client, case_project.key, quarantined="true") == [flaky_case.code]
    assert await list_case_codes(client, case_project.key, quarantined="false") == [other_case.code]
    summary = next(
        case
        for case in (await client.get(f"/api/projects/{case_project.key}/test-cases")).json()
        if case["code"] == flaky_case.code
    )
    assert (summary["isQuarantined"], summary["quarantinedAt"]) == (True, body["quarantinedAt"])

    released = await release(client, flaky_case)

    assert released.status_code == 200, released.text
    assert (released.json()["isQuarantined"], released.json()["quarantineReason"]) == (False, None)
    events = await list_quarantine_events(client, flaky_case)
    assert [(event["kind"], event["actorId"], event["actorName"], event["reason"]) for event in events] == [
        ("released", str(case_project.user_id), "Test User", None),
        ("quarantined", str(case_project.user_id), "Test User", "Fails on slow networks"),
    ]
    assert [(event.type, event.ids["code"]) for event in recording_live_event_publisher.events] == [
        (LiveEventType.TEST_CASE_CHANGED, flaky_case.code),
        (LiveEventType.TEST_CASE_CHANGED, flaky_case.code),
    ]


async def test_quarantine_and_release_are_idempotent(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    first = await quarantine(client, flaky_case, "First reason")

    second = await quarantine(client, flaky_case, "Second reason")
    release_once = await release(client, flaky_case)
    release_twice = await release(client, flaky_case)

    assert second.status_code == 200, second.text
    assert (second.json()["quarantinedAt"], second.json()["quarantineReason"]) == (
        first.json()["quarantinedAt"],
        "First reason",
    )
    assert (release_once.status_code, release_twice.status_code) == (200, 200)
    assert [event["kind"] for event in await list_quarantine_events(client, flaky_case)] == [
        "released",
        "quarantined",
    ]


async def test_a_blank_reason_is_stored_as_no_reason(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)

    response = await quarantine(client, flaky_case, "   ")

    assert response.status_code == 200, response.text
    assert response.json()["quarantineReason"] is None


async def test_a_reason_longer_than_500_characters_is_refused(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)

    response = await quarantine(client, flaky_case, "x" * 501)

    assert response.status_code == 422, response.text
    assert (await get_case_json(client, flaky_case))["isQuarantined"] is False


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_only_admins_and_qc_quarantine_cases(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer, role=ProjectRole.ADMIN)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await sign_up_member(client, test_cases_container, recording_mailer, case_project.project, role)

    put_response = await quarantine(client, flaky_case)
    delete_response = await release(client, flaky_case)
    events_response = await client.get(
        f"/api/projects/{case_project.key}/test-cases/{flaky_case.code}/quarantine-events"
    )

    expected = 200 if role in QUARANTINE_ROLES else 403
    assert (put_response.status_code, delete_response.status_code, events_response.status_code) == (
        expected,
        expected,
        200,
    )


async def test_another_projects_case_is_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    other_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    other_case = await create_flaky_case(client, test_cases_container, other_project)
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    base = f"/api/projects/{case_project.key}/test-cases/{other_case.code}"

    responses = [
        await client.put(f"{base}/quarantine", json={}),
        await client.delete(f"{base}/quarantine"),
        await client.get(f"{base}/quarantine-events"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]


async def test_ten_passes_in_a_row_after_quarantine_release_the_case(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    response = await quarantine(client, flaky_case, "Flaky checkout")
    assert response.status_code == 200, response.text
    await move_quarantine_back(test_cases_container, flaky_case, timedelta(hours=2))
    await seed_history(test_cases_container, flaky_case, "PPPPPPPPP")
    await recompute(test_cases_container, flaky_case)
    after_nine = await get_case_json(client, flaky_case)

    await seed_history(test_cases_container, flaky_case, "P", datetime.now(UTC) + timedelta(minutes=1))
    await recompute(test_cases_container, flaky_case)

    after_ten = await get_case_json(client, flaky_case)
    assert after_nine["isQuarantined"] is True
    assert (after_ten["isQuarantined"], after_ten["quarantinedAt"], after_ten["quarantineReason"]) == (
        False,
        None,
        None,
    )
    events = await list_quarantine_events(client, flaky_case)
    assert [(event["kind"], event["actorId"], event["actorName"]) for event in events] == [
        ("auto_released", None, None),
        ("quarantined", str(case_project.user_id), "Test User"),
    ]


async def test_a_failure_after_quarantine_keeps_the_case_quarantined(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await quarantine(client, flaky_case)
    await move_quarantine_back(test_cases_container, flaky_case, timedelta(hours=2))
    await seed_history(test_cases_container, flaky_case, "PPPPPPPPPF")

    await recompute(test_cases_container, flaky_case)

    assert (await get_case_json(client, flaky_case))["isQuarantined"] is True


async def test_passes_before_the_quarantine_do_not_count_towards_release(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "P" * 10, datetime.now(UTC) - timedelta(hours=3))
    await quarantine(client, flaky_case)
    await seed_result(test_cases_container, flaky_case, ResultStatus.PASSED, datetime.now(UTC) + timedelta(minutes=1))

    await recompute(test_cases_container, flaky_case)

    assert (await get_case_json(client, flaky_case))["isQuarantined"] is True

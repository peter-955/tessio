from datetime import UTC, datetime
from uuid import uuid7

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.failures import FailureEventKind, FailureStatus
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable
from tests.api.failures.failure_steps import (
    as_failures_container,
    find_only_failure,
    list_event_rows,
    list_failure_rows,
    record,
    seed_case,
    seed_case_result,
    seed_run,
    seed_scenario,
    set_failure_status,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_failed_result_opens_an_unassigned_failure(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)

    recorded = await record(container, scenario, ResultStatus.FAILED)

    failure = await find_only_failure(container, scenario.case.id)
    assert failure.status is FailureStatus.OPEN
    assert failure.assignee_id is None
    assert failure.project_id == scenario.project.id
    assert failure.story_id == scenario.story.id
    assert failure.opened_by_case_result_id == recorded.case_result_id
    assert failure.latest_case_result_id == recorded.case_result_id
    events = await list_event_rows(container, failure.id)
    assert [(event.kind, event.from_status, event.to_status) for event in events] == [
        (FailureEventKind.OPENED, None, FailureStatus.OPEN)
    ]
    assert events[0].case_result_id == recorded.case_result_id
    assert events[0].actor_id is None
    assert recording_live_event_publisher.events == []


@pytest.mark.parametrize("status", [ResultStatus.BLOCKED, ResultStatus.SKIPPED, ResultStatus.PASSED])
async def test_other_results_open_nothing(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, status: ResultStatus
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)

    await record(container, scenario, status)

    assert await list_failure_rows(container, scenario.case.id) == []


async def test_a_second_failed_result_updates_the_open_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    first = await record(container, scenario, ResultStatus.FAILED)

    second = await record(container, scenario, ResultStatus.FAILED)

    failure = await find_only_failure(container, scenario.case.id)
    assert failure.status is FailureStatus.OPEN
    assert failure.opened_by_case_result_id == first.case_result_id
    assert failure.latest_case_result_id == second.case_result_id
    events = await list_event_rows(container, failure.id)
    assert [event.kind for event in events] == [FailureEventKind.OPENED, FailureEventKind.FAILED_AGAIN]
    assert events[1].case_result_id == second.case_result_id


async def test_blocked_skipped_and_passed_leave_an_open_failure_alone(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    first = await record(container, scenario, ResultStatus.FAILED)

    for status in (ResultStatus.BLOCKED, ResultStatus.SKIPPED, ResultStatus.PASSED):
        await record(container, scenario, status)

    failure = await find_only_failure(container, scenario.case.id)
    assert failure.status is FailureStatus.OPEN
    assert failure.latest_case_result_id == first.case_result_id
    assert len(await list_event_rows(container, failure.id)) == 1


async def test_a_failed_result_reopens_a_fixed_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    await record(container, scenario, ResultStatus.FAILED)
    opened = await find_only_failure(container, scenario.case.id)
    await set_failure_status(container, opened.id, FailureStatus.FIXED)

    again = await record(container, scenario, ResultStatus.FAILED)

    failure = await find_only_failure(container, scenario.case.id)
    assert failure.id == opened.id
    assert failure.status is FailureStatus.REOPENED
    assert failure.latest_case_result_id == again.case_result_id
    assert failure.status_changed_at is not None
    assert failure.status_changed_by is None
    events = await list_event_rows(container, failure.id)
    assert [(event.kind, event.from_status, event.to_status) for event in events] == [
        (FailureEventKind.OPENED, None, FailureStatus.OPEN),
        (FailureEventKind.STATUS_CHANGED, FailureStatus.FIXED, FailureStatus.REOPENED),
    ]
    assert events[1].case_result_id == again.case_result_id
    assert events[1].actor_id is None


async def test_a_passed_result_keeps_a_fixed_failure_fixed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    await record(container, scenario, ResultStatus.FAILED)
    opened = await find_only_failure(container, scenario.case.id)
    await set_failure_status(container, opened.id, FailureStatus.FIXED)

    await record(container, scenario, ResultStatus.PASSED)

    failure = await find_only_failure(container, scenario.case.id)
    assert failure.status is FailureStatus.FIXED
    assert len(await list_event_rows(container, failure.id)) == 1


async def test_a_failed_result_after_verified_opens_a_new_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    await record(container, scenario, ResultStatus.FAILED)
    verified = await find_only_failure(container, scenario.case.id)
    await set_failure_status(container, verified.id, FailureStatus.VERIFIED)

    again = await record(container, scenario, ResultStatus.FAILED)

    rows = await list_failure_rows(container, scenario.case.id)
    assert [row.status for row in rows] == [FailureStatus.VERIFIED, FailureStatus.OPEN]
    assert rows[0].id == verified.id
    assert rows[0].latest_case_result_id == verified.latest_case_result_id
    assert rows[1].opened_by_case_result_id == again.case_result_id
    assert len(await list_event_rows(container, verified.id)) == 1


async def test_failures_of_two_cases_are_separate(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    other_case = await seed_case(container, scenario.project, scenario.story.id, 2, scenario.runner.user_id)

    await record(container, scenario, ResultStatus.FAILED)
    await record(container, scenario, ResultStatus.FAILED, case=other_case)

    first = await find_only_failure(container, scenario.case.id)
    second = await find_only_failure(container, other_case.id)
    assert first.id != second.id
    assert len(await list_event_rows(container, first.id)) == 1
    assert len(await list_event_rows(container, second.id)) == 1


async def test_the_handler_joins_the_caller_transaction(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    run_id = await seed_run(container, scenario)
    first = await seed_case_result(container, scenario, run_id, scenario.case, ResultStatus.PASSED)
    handler = as_failures_container(container).apply_case_result
    case_result_id = uuid7()
    now = datetime.now(UTC)

    with pytest.raises(RuntimeError):
        async with container.database.begin():
            container.database.get_current_session().add(
                CaseResultTable(
                    id=case_result_id,
                    run_id=await seed_run(container, scenario),
                    test_case_id=scenario.case.id,
                    test_case_version_id=scenario.case.version_id,
                    status=ResultStatus.FAILED,
                    duration_ms=None,
                    recorded_by=scenario.runner.user_id,
                    created_at=now,
                )
            )
            await handler.handle(
                first.model_copy(
                    update={"case_result_id": case_result_id, "status": ResultStatus.FAILED, "recorded_at": now}
                )
            )
            assert len(await list_failure_rows(container, scenario.case.id)) == 1
            raise RuntimeError

    assert await list_failure_rows(container, scenario.case.id) == []

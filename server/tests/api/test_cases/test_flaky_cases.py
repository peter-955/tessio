from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.modules.runs import ResultStatus, RunExecutor
from app.modules.test_cases import RecomputeFlakyJobHandler, SweepFlakyJobHandler
from app.shared.events import LiveEventType
from app.shared.typing.enums import JobName, QueueName
from tests.api.test_cases.case_steps import build_step, set_up_case_project, update_case
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_cases.flaky_steps import (
    create_flaky_case,
    get_case_json,
    list_case_codes,
    recompute,
    seed_history,
    seed_result,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_three_flips_in_the_last_ten_results_make_a_case_flaky(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    steady_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "PFPPPPPPPF")
    await seed_history(test_cases_container, steady_case, "PFPPPPPPPP")

    await recompute(test_cases_container, flaky_case)
    await recompute(test_cases_container, steady_case)

    flaky = await get_case_json(client, flaky_case)
    steady = await get_case_json(client, steady_case)
    assert (flaky["isFlaky"], flaky["flakyScore"], flaky["flakySince"] is not None) == (True, 3, True)
    assert (steady["isFlaky"], steady["flakyScore"], steady["flakySince"]) == (False, 2, None)
    assert await list_case_codes(client, case_project.key, flaky="true") == [flaky_case.code]
    assert await list_case_codes(client, case_project.key, flaky="false") == [steady_case.code]


async def test_only_the_last_ten_results_count(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "PPPPPPPPPP" + "FPFPFP")

    await recompute(test_cases_container, flaky_case)

    detail = await get_case_json(client, flaky_case)
    assert (detail["isFlaky"], detail["flakyScore"]) == (False, 0)


async def test_skipped_and_blocked_results_do_not_count_as_flips(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    newest = datetime.now(UTC)
    statuses = [ResultStatus.PASSED, ResultStatus.BLOCKED, ResultStatus.PASSED, ResultStatus.SKIPPED]
    for minutes, status in enumerate(statuses * 3):
        await seed_result(test_cases_container, flaky_case, status, newest - timedelta(minutes=minutes))

    await recompute(test_cases_container, flaky_case)

    detail = await get_case_json(client, flaky_case)
    assert (detail["isFlaky"], detail["flakyScore"]) == (False, 0)


async def test_a_new_case_version_resets_the_flaky_flag(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "PFPFPF")
    await recompute(test_cases_container, flaky_case)
    assert (await get_case_json(client, flaky_case))["isFlaky"] is True

    response = await update_case(client, case_project.key, flaky_case.code, 1, steps=[build_step("Pay again")])
    assert response.status_code == 200, response.text
    assert (response.json()["isFlaky"], response.json()["flakyScore"]) == (False, 0)
    after_edit = await get_case_json(client, flaky_case)
    await recompute(test_cases_container, flaky_case)
    after_recompute = await get_case_json(client, flaky_case)

    assert (after_edit["isFlaky"], after_edit["flakyScore"]) == (False, 0)
    assert (after_recompute["isFlaky"], after_recompute["flakyScore"]) == (False, 0)


async def test_results_on_an_older_version_do_not_count(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "PFPFPF", datetime.now(UTC) - timedelta(hours=2))
    response = await update_case(client, case_project.key, flaky_case.code, 1, steps=[build_step("Pay again")])
    assert response.status_code == 200, response.text
    await seed_history(test_cases_container, flaky_case, "PFP")

    await recompute(test_cases_container, flaky_case)

    detail = await get_case_json(client, flaky_case)
    assert (detail["isFlaky"], detail["flakyScore"]) == (False, 2)


async def test_a_case_stops_being_flaky_when_its_results_settle(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "PFPF", datetime.now(UTC) - timedelta(hours=1))
    await recompute(test_cases_container, flaky_case)
    flaky_since = (await get_case_json(client, flaky_case))["flakySince"]
    await seed_history(test_cases_container, flaky_case, "P")
    await recompute(test_cases_container, flaky_case)
    still_flaky = await get_case_json(client, flaky_case)
    await seed_history(test_cases_container, flaky_case, "PPPPPPP")

    await recompute(test_cases_container, flaky_case)

    settled = await get_case_json(client, flaky_case)
    assert (still_flaky["isFlaky"], still_flaky["flakySince"]) == (True, flaky_since)
    assert (settled["isFlaky"], settled["flakySince"]) == (False, None)


async def test_a_manual_and_a_claude_result_that_differ_within_a_day_disagree(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    disagreeing_case = await create_flaky_case(client, test_cases_container, case_project)
    agreeing_case = await create_flaky_case(client, test_cases_container, case_project)
    now = datetime.now(UTC)
    await seed_result(
        test_cases_container, disagreeing_case, ResultStatus.PASSED, now - timedelta(hours=5), RunExecutor.MANUAL
    )
    await seed_result(test_cases_container, disagreeing_case, ResultStatus.FAILED, now, RunExecutor.CLAUDE)
    await seed_result(
        test_cases_container, agreeing_case, ResultStatus.FAILED, now - timedelta(hours=5), RunExecutor.MANUAL
    )
    await seed_result(test_cases_container, agreeing_case, ResultStatus.FAILED, now, RunExecutor.CLAUDE)

    await recompute(test_cases_container, disagreeing_case)
    await recompute(test_cases_container, agreeing_case)

    disagreeing = await get_case_json(client, disagreeing_case)
    agreeing = await get_case_json(client, agreeing_case)
    assert (disagreeing["isDisagreeing"], disagreeing["disagreedAt"] is not None) == (True, True)
    assert (agreeing["isDisagreeing"], agreeing["disagreedAt"]) == (False, None)
    assert await list_case_codes(client, case_project.key, disagreeing="true") == [disagreeing_case.code]
    assert await list_case_codes(client, case_project.key, disagreeing="false") == [agreeing_case.code]
    latest = await client.get(f"/api/projects/{case_project.key}/case-latest-results")
    assert latest.status_code == 200, latest.text
    flags = {case["code"]: case["isDisagreeing"] for case in latest.json()}
    assert flags == {disagreeing_case.code: True, agreeing_case.code: False}


async def test_results_more_than_a_day_apart_do_not_disagree(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    now = datetime.now(UTC)
    await seed_result(
        test_cases_container, flaky_case, ResultStatus.PASSED, now - timedelta(hours=25), RunExecutor.MANUAL
    )
    await seed_result(test_cases_container, flaky_case, ResultStatus.FAILED, now, RunExecutor.CLAUDE)

    await recompute(test_cases_container, flaky_case)

    assert (await get_case_json(client, flaky_case))["isDisagreeing"] is False


async def test_a_disagreement_on_an_older_version_is_cleared_by_a_new_version(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    now = datetime.now(UTC)
    await seed_result(
        test_cases_container, flaky_case, ResultStatus.PASSED, now - timedelta(hours=1), RunExecutor.MANUAL
    )
    await seed_result(test_cases_container, flaky_case, ResultStatus.FAILED, now, RunExecutor.CLAUDE)
    await recompute(test_cases_container, flaky_case)
    assert (await get_case_json(client, flaky_case))["isDisagreeing"] is True

    response = await update_case(client, case_project.key, flaky_case.code, 1, steps=[build_step("Pay again")])
    assert response.status_code == 200, response.text
    await recompute(test_cases_container, flaky_case)

    assert (await get_case_json(client, flaky_case))["isDisagreeing"] is False


async def test_case_latest_results_show_flaky_and_quarantine_flags(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    plain_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "FPFP")
    await recompute(test_cases_container, flaky_case)
    response = await client.put(
        f"/api/projects/{case_project.key}/test-cases/{plain_case.code}/quarantine", json={"reason": "Slow network"}
    )
    assert response.status_code == 200, response.text

    latest = await client.get(f"/api/projects/{case_project.key}/case-latest-results")

    assert latest.status_code == 200, latest.text
    flags = {case["code"]: (case["isFlaky"], case["isQuarantined"]) for case in latest.json()}
    assert flags == {flaky_case.code: (True, False), plain_case.code: (False, True)}


async def test_a_recompute_that_changes_the_case_publishes_a_live_event(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "FPFP")
    recording_live_event_publisher.events.clear()

    await recompute(test_cases_container, flaky_case)
    await recompute(test_cases_container, flaky_case)

    assert [(event.type, event.ids["code"]) for event in recording_live_event_publisher.events] == [
        (LiveEventType.TEST_CASE_CHANGED, flaky_case.code)
    ]


async def test_the_recompute_job_reads_the_case_id_from_its_data(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    flaky_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, flaky_case, "FPFP")
    handler = RecomputeFlakyJobHandler(test_cases_container.recompute_flaky)

    await handler.handle({"testCaseId": "not-a-uuid"})
    await handler.handle({})
    unchanged = await get_case_json(client, flaky_case)
    await handler.handle({"testCaseId": str(flaky_case.test_case_id)})

    assert unchanged["isFlaky"] is False
    assert (await get_case_json(client, flaky_case))["isFlaky"] is True


async def test_the_nightly_sweep_recomputes_every_case(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    first_case = await create_flaky_case(client, test_cases_container, case_project)
    second_case = await create_flaky_case(client, test_cases_container, case_project)
    await seed_history(test_cases_container, first_case, "FPFP")
    await seed_history(test_cases_container, second_case, "PFPF")

    await SweepFlakyJobHandler(test_cases_container.sweep_flaky).handle({})

    assert (await get_case_json(client, first_case))["isFlaky"] is True
    assert (await get_case_json(client, second_case))["isFlaky"] is True


async def test_the_sweep_is_scheduled_nightly_and_both_jobs_have_handlers(
    test_cases_container: CasesContainer,
) -> None:
    schedules = {schedule.job_name: schedule for schedule in test_cases_container.job_schedules}
    maintenance_handlers = test_cases_container.job_handlers[QueueName.MAINTENANCE]

    sweep = schedules[JobName.TEST_CASES_SWEEP_FLAKY]
    assert (sweep.scheduler_id, sweep.queue_name, sweep.cron_pattern) == (
        "test_cases.sweep_flaky",
        QueueName.MAINTENANCE,
        "45 3 * * *",
    )
    assert isinstance(maintenance_handlers[JobName.TEST_CASES_RECOMPUTE_FLAKY], RecomputeFlakyJobHandler)
    assert isinstance(maintenance_handlers[JobName.TEST_CASES_SWEEP_FLAKY], SweepFlakyJobHandler)

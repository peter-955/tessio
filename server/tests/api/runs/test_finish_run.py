from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.container import Container
from app.modules.files.infrastructure import StoredFileTable
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.runs import CriterionImpact, CriterionStatus, RunReport
from app.modules.runs.infrastructure import RunTable, StepResultTable
from app.modules.users import WorkspaceRole
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    read_tool_error_code,
    record_case_id,
    seed_runnable_story,
    seed_secret,
    sign_up_runner,
    start_run_id,
)
from tests.api.runs.runs_test_container import RunsTestContainer
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def start_a_run(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    case_count: int = 3,
    step_count: int = 2,
) -> tuple[Runner, SeededRunnableStory, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count, step_count)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    return runner, story, run_id


async def find_run_row(container: Container, run_id: str) -> RunTable:
    async with container.database.begin():
        row = await container.database.get_current_session().scalar(select(RunTable).where(RunTable.id == UUID(run_id)))
    assert row is not None
    return row


@pytest.mark.parametrize(
    ("statuses", "expected_status"),
    [
        (["passed", "failed"], "failed"),
        (["passed", "blocked"], "failed"),
        (["passed", "skipped"], "passed"),
        (["skipped", "skipped"], "passed"),
    ],
)
async def test_run_status_follows_the_results(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    statuses: list[str],
    expected_status: str,
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, case_count=2)
    for case_id, status in zip(story.case_ids, statuses, strict=True):
        await record_case_id(client, runner.token, run_id, case_id, status)

    content = read_tool_json(await finish(client, runner.token, run_id))

    assert content == {"status": expected_status, "missing_screenshots": []}
    run_row = await find_run_row(container, run_id)
    assert run_row.status == expected_status
    assert run_row.abort_reason is None
    assert run_row.finished_at is not None


async def test_a_run_without_results_is_aborted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id = await start_a_run(client, container, recording_mailer)

    content = read_tool_json(await finish(client, runner.token, run_id))

    assert content["status"] == "aborted"
    run_row = await find_run_row(container, run_id)
    assert run_row.abort_reason == "no_results"


async def test_report_holds_counts_failed_cases_and_a_masked_summary(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, case_count=3)
    await seed_secret(container, story.project, "API_KEY", "sk-live-123")
    failing_steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Opened"},
        {"order": 2, "status": "failed", "actual_result": "Spinner forever", "error": "Timeout"},
    ]
    await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed")
    await record_case_id(client, runner.token, run_id, story.case_ids[1], "failed", failing_steps)

    read_tool_json(await finish(client, runner.token, run_id, "Key sk-live-123 expired midway"))

    run_row = await find_run_row(container, run_id)
    assert run_row.summary == f"Key {MASKED_VALUE} expired midway"
    report = run_row.report
    assert isinstance(report, dict)
    assert report["counts"] == {"total": 3, "passed": 1, "failed": 1, "blocked": 0, "skipped": 0, "not_reported": 1}
    assert report["summary"] == f"Key {MASKED_VALUE} expired midway"
    failed_cases = RunReport.model_validate(report).failed_cases
    assert len(failed_cases) == 1
    assert failed_cases[0].test_case_id == story.case_ids[1]
    assert failed_cases[0].status == "failed"
    assert failed_cases[0].step_order == 2
    assert failed_cases[0].step_action == "Action 2"
    assert failed_cases[0].actual_result == "Spinner forever"
    assert failed_cases[0].error == "Timeout"


async def test_uploaded_screenshots_are_verified_and_the_rest_are_missing(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, runs_container, recording_mailer, case_count=1)
    steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/1.png"},
        {"order": 2, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/2.png"},
    ]
    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed", steps)
    uploaded_key = f"projects/{story.project.id}/screenshot/{case_result_id}/1.jpg"
    runs_container.in_memory_object_storage.put(uploaded_key, b"jpeg-bytes")

    content = read_tool_json(await finish(client, runner.token, run_id))

    missing = content["missing_screenshots"]
    assert isinstance(missing, list)
    assert len(missing) == 1
    assert missing[0]["step_order"] == 2
    assert str(missing[0]["code"]).startswith("TC-")
    async with runs_container.database.begin():
        session = runs_container.database.get_current_session()
        stored_files = list(
            await session.scalars(
                select(StoredFileTable)
                .join(StepResultTable, StepResultTable.screenshot_file_id == StoredFileTable.id)
                .where(StepResultTable.case_result_id == UUID(case_result_id))
                .order_by(StepResultTable.step_order)
            )
        )
    assert [(stored_file.status, stored_file.object_key) for stored_file in stored_files] == [
        ("uploaded", uploaded_key),
        ("missing", f"projects/{story.project.id}/screenshot/{case_result_id}/2"),
    ]
    assert stored_files[0].file_name == "1.jpg"
    assert stored_files[0].content_type == "image/jpeg"
    assert stored_files[0].size == len(b"jpeg-bytes")
    run_row = await find_run_row(runs_container, run_id)
    assert isinstance(run_row.report, dict)
    assert run_row.report["missing_screenshots"] == [
        {
            "case_result_id": case_result_id,
            "test_case_id": str(story.case_ids[0]),
            "code": missing[0]["code"],
            "step_order": 2,
            "iteration": None,
        }
    ]


async def test_finish_publishes_and_notifies_the_starter_and_qc(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, case_count=2)
    other_qc = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.QC, "Other QC")
    viewer = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.VIEWER, "Viewer")
    await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed")
    await record_case_id(client, runner.token, run_id, story.case_ids[1], "blocked")
    recording_live_event_publisher.events.clear()

    read_tool_json(await finish(client, runner.token, run_id))

    finished_events = [
        event.ids for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_FINISHED
    ]
    assert finished_events == [{"runId": run_id, "storyId": str(story.story_id), "status": "failed"}]
    async with container.database.begin():
        notifications = list(
            await container.database.get_current_session().scalars(
                select(NotificationTable).where(NotificationTable.project_id == story.project.id)
            )
        )
    recipients = {notification.user_id for notification in notifications}
    assert recipients == {runner.account.user_id, other_qc.account.user_id}
    assert viewer.account.user_id not in recipients
    payload = notifications[0].payload
    assert payload["kind"] == "run_finished"
    assert payload["run_id"] == run_id
    assert payload["story_jira_key"] == story.jira_key
    assert payload["outcome"] == "failed"
    assert (payload["passed_count"], payload["failed_count"], payload["blocked_count"]) == (1, 0, 1)


async def test_another_runner_cannot_finish_but_an_admin_can(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, run_id = await start_a_run(client, container, recording_mailer)
    other_qc = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.QC, "Other QC")
    admin = await sign_up_runner(
        client, container, recording_mailer, story.project, ProjectRole.ADMIN, "Admin", WorkspaceRole.MEMBER
    )

    refused = await finish(client, other_qc.token, run_id)
    allowed = await finish(client, admin.token, run_id)

    assert read_tool_error_code(refused) == "RUN_NOT_OWNED"
    assert read_tool_json(allowed)["status"] == "aborted"


async def test_finishing_twice_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id = await start_a_run(client, container, recording_mailer)
    read_tool_json(await finish(client, runner.token, run_id))

    response = await finish(client, runner.token, run_id)

    assert read_tool_error_code(response) == "RUN_NOT_RUNNING"


async def test_unknown_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, _ = await start_a_run(client, container, recording_mailer)

    response = await finish(client, runner.token, str(uuid4()))

    assert read_tool_error_code(response) == "NOT_FOUND"


async def test_report_takes_the_criterion_impacts_from_the_calculator(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, runs_container, recording_mailer, case_count=1)
    impact = CriterionImpact(
        criterion_id=uuid4(),
        code="AC1",
        text="Shoppers can pay by card",
        status=CriterionStatus.FAILED,
        run_case_codes=["TC-1"],
        failed_case_codes=["TC-1"],
    )
    runs_container.stub_criterion_impact_calculator.impacts = [impact]
    await record_case_id(client, runner.token, run_id, story.case_ids[0], "failed")

    read_tool_json(await finish(client, runner.token, run_id))

    assert runs_container.stub_criterion_impact_calculator.calls == [(story.project.id, UUID(run_id))]
    run_row = await find_run_row(runs_container, run_id)
    assert isinstance(run_row.report, dict)
    assert run_row.report["criterion_impacts"] == [impact.model_dump(mode="json")]


@pytest.mark.parametrize("role", [ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER])
async def test_other_roles_cannot_finish(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    _, story, run_id = await start_a_run(client, container, recording_mailer)
    member = await sign_up_runner(client, container, recording_mailer, story.project, role, "Member")

    response = await finish(client, member.token, run_id)

    assert read_tool_error_code(response) == "PERMISSION_DENIED"

from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select

from app.container import Container
from app.modules.files.infrastructure import StoredFileTable
from app.modules.runs.infrastructure import CaseResultTable, RunTable, StepResultTable
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    read_tool_error,
    read_tool_error_code,
    record_case,
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
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, step_count: int = 3
) -> tuple[Runner, SeededRunnableStory, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, step_count=step_count)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    return runner, story, run_id


async def find_step_rows(container: Container, case_result_id: str) -> list[StepResultTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(StepResultTable)
            .where(StepResultTable.case_result_id == UUID(case_result_id))
            .order_by(StepResultTable.step_order)
        )
        return list(rows)


async def test_result_and_steps_are_saved_with_unreported_steps_skipped(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Home page shown"},
        {"order": 3, "status": "failed", "actual_result": "Error banner", "error": "500 on submit"},
    ]

    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "failed", steps)

    async with container.database.begin():
        session = container.database.get_current_session()
        case_row = await session.scalar(select(CaseResultTable).where(CaseResultTable.id == UUID(case_result_id)))
        run_row = await session.scalar(select(RunTable).where(RunTable.id == UUID(run_id)))
    assert case_row is not None
    assert case_row.status == "failed"
    assert case_row.duration_ms == 900
    assert case_row.recorded_by == runner.account.user_id
    assert case_row.test_case_id == story.case_ids[0]
    assert run_row is not None
    assert run_row.last_activity_at >= run_row.started_at
    step_rows = await find_step_rows(container, case_result_id)
    assert [(row.step_order, row.status, row.actual_result, row.error) for row in step_rows] == [
        (1, "passed", "Home page shown", None),
        (2, "skipped", None, None),
        (3, "failed", "Error banner", "500 on submit"),
    ]


async def test_secret_values_are_masked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, step_count=1)
    await seed_secret(container, story.project, "ADMIN_PASSWORD", "hunter2-secret", story.environment_id)
    steps: list[dict[str, object]] = [
        {
            "order": 1,
            "status": "failed",
            "actual_result": "Typed hunter2-secret into the form",
            "error": "Login hunter2-secret refused",
        }
    ]

    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "failed", steps)

    step_rows = await find_step_rows(container, case_result_id)
    assert step_rows[0].actual_result == f"Typed {MASKED_VALUE} into the form"
    assert step_rows[0].error == f"Login {MASKED_VALUE} refused"


async def test_each_screenshot_gets_a_pending_stored_file(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, step_count=2)
    steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/1.png"},
        {"order": 2, "status": "passed", "actual_result": "Shown"},
    ]

    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed", steps)

    step_rows = await find_step_rows(container, case_result_id)
    assert step_rows[1].screenshot_file_id is None
    async with container.database.begin():
        stored_file = await container.database.get_current_session().scalar(
            select(StoredFileTable).where(StoredFileTable.id == step_rows[0].screenshot_file_id)
        )
    assert stored_file is not None
    assert stored_file.status == "pending"
    assert stored_file.kind == "screenshot"
    assert stored_file.object_key == f"projects/{story.project.id}/screenshot/{case_result_id}/1"
    assert stored_file.file_name == "1.jpg"
    assert stored_file.content_type == "image/jpeg"
    assert stored_file.uploaded_by == runner.account.user_id
    assert stored_file.project_id == story.project.id


async def test_recording_calls_the_handler_and_publishes_an_event(
    client: AsyncClient,
    runs_container: RunsTestContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    runner, story, run_id = await start_a_run(client, runs_container, recording_mailer)
    recording_live_event_publisher.events.clear()

    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "blocked")

    recorded = runs_container.recording_case_result_recorded_handler.recorded
    assert len(recorded) == 1
    assert recorded[0].case_result_id == UUID(case_result_id)
    assert recorded[0].run_id == UUID(run_id)
    assert recorded[0].story_id == story.story_id
    assert recorded[0].project_id == story.project.id
    assert recorded[0].test_case_id == story.case_ids[0]
    assert recorded[0].status == "blocked"
    assert recorded[0].recorded_by == runner.account.user_id
    assert [(event.type, event.ids) for event in recording_live_event_publisher.events] == [
        (
            LiveEventType.RUN_CASE_RECORDED,
            {
                "runId": run_id,
                "caseResultId": case_result_id,
                "testCaseId": str(story.case_ids[0]),
                "storyId": str(story.story_id),
            },
        )
    ]


async def test_another_runner_cannot_record_into_the_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, run_id = await start_a_run(client, container, recording_mailer)
    other = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.QC, "Other QC")

    response = await record_case(client, other.token, run_id, story.case_ids[0])

    assert read_tool_error_code(response) == "RUN_NOT_OWNED"


async def test_a_finished_run_takes_no_more_results(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    read_tool_json(await finish(client, runner.token, run_id))

    response = await record_case(client, runner.token, run_id, story.case_ids[0])

    assert read_tool_error_code(response) == "RUN_NOT_RUNNING"


async def test_a_case_is_recorded_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    await record_case_id(client, runner.token, run_id, story.case_ids[0])

    response = await record_case(client, runner.token, run_id, story.case_ids[0])

    assert read_tool_error_code(response) == "CASE_RESULT_EXISTS"


async def test_a_case_outside_the_run_is_unknown(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id = await start_a_run(client, container, recording_mailer)

    response = await record_case(client, runner.token, run_id, uuid4())

    assert read_tool_error_code(response) == "UNKNOWN_REFERENCE"


async def test_bad_step_orders_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, step_count=2)
    unknown_step: list[dict[str, object]] = [{"order": 5, "status": "passed", "actual_result": "Shown"}]
    twice: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Shown"},
        {"order": 1, "status": "failed", "actual_result": "Shown"},
    ]

    unknown_response = await record_case(client, runner.token, run_id, story.case_ids[0], "passed", unknown_step)
    twice_response = await record_case(client, runner.token, run_id, story.case_ids[0], "passed", twice)

    assert read_tool_error(unknown_response).startswith("INVALID_REQUEST: Step 5 is not a step of TC-")
    assert read_tool_error_code(twice_response) == "INVALID_REQUEST"


async def test_an_unknown_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, _ = await start_a_run(client, container, recording_mailer)

    response = await record_case(client, runner.token, str(uuid4()), story.case_ids[0])

    assert read_tool_error_code(response) == "NOT_FOUND"


async def test_a_negative_duration_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)

    response = await record_case(client, runner.token, run_id, story.case_ids[0], duration_ms=-1)

    assert response.json()["result"]["isError"] is True

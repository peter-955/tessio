from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from httpx import AsyncClient, Response
from sqlalchemy import update

from app.container import Container
from app.modules.run_logs.domains.uploaded_run_log.entity import UploadedLogEntry
from app.modules.run_logs.typing.enums import RunLogEntryKind, RunLogPhase
from app.modules.run_logs.utils.run_log_phases import assign_phases
from app.modules.runs.infrastructure import RunTable
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    record_case,
    seed_runnable_story,
    seed_secret,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher

SECRET = "hunter2-very-secret"
CHROME = "mcp__claude-in-chrome__computer"
TESSIO = "mcp__plugin_tessio_tessio__"
STARTED_AT = datetime(2026, 11, 1, 9, 0, tzinfo=UTC)


def at(seconds: int) -> str:
    return (STARTED_AT + timedelta(seconds=seconds)).isoformat()


def build_log(case_ids: list[UUID], run_id: str) -> dict[str, object]:
    first, second = case_ids
    return {
        "is_cut": False,
        "usage": {
            "input_tokens": 12,
            "cache_creation_input_tokens": 3400,
            "cache_read_input_tokens": 56000,
            "output_tokens": 789,
        },
        "entries": [
            {"kind": "action", "at": at(0), "tool": f"{TESSIO}start_run", "input": {"story_key": "SHOP-1"}},
            {"kind": "action", "at": at(1), "tool": "Bash", "input": {"command": "curl -fsS https://shop.test"}},
            {"kind": "note", "at": at(2), "text": "Signing in as the buyer."},
            {
                "kind": "action",
                "at": at(3),
                "tool": CHROME,
                "input": {"action": "type", "text": SECRET},
                "output": f"Typed {SECRET}",
                "duration_ms": 420,
            },
            {
                "kind": "action",
                "at": at(4),
                "tool": f"{TESSIO}record_case_result",
                "input": {"run_id": run_id, "case_id": str(first)},
            },
            {"kind": "action", "at": at(5), "tool": CHROME, "input": {"action": "left_click"}, "is_error": True},
            {
                "kind": "action",
                "at": at(6),
                "tool": f"{TESSIO}record_case_result",
                "input": {"run_id": run_id, "case_id": str(second)},
            },
            {"kind": "note", "at": at(7), "text": "x" * 5000},
            {"kind": "action", "at": at(8), "tool": f"{TESSIO}finish_run", "input": {"run_id": run_id}},
        ],
    }


async def finished_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[SeededRunnableStory, Runner, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    await seed_secret(container, project, "buyer_password", SECRET)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    for case_id in story.case_ids:
        await record_case(client, runner.token, run_id, case_id)
    await finish(client, runner.token, run_id)
    return story, runner, run_id


async def upload(client: AsyncClient, token: str, run_id: str, body: dict[str, object]) -> Response:
    return await client.post(f"/api/runs/{run_id}/log", json=body, headers={"authorization": f"Bearer {token}"})


async def read_log(
    client: AsyncClient, runner: Runner, story: SeededRunnableStory, run_id: str, **params: str
) -> Response:
    use_session(client, runner.account.session_token)
    return await client.get(f"/api/projects/{story.project.key}/runs/{run_id}/log", params=params)


async def test_the_log_is_masked_cut_and_grouped_by_case(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    story, runner, run_id = await finished_run(client, container, recording_mailer)

    response = await upload(client, runner.token, run_id, build_log(story.case_ids, run_id))
    log = (await read_log(client, runner, story, run_id)).json()

    assert response.status_code == 201, response.text
    assert response.json()["entryCount"] == 9
    assert log["usage"] == {
        "inputTokens": 12,
        "cacheCreationInputTokens": 3400,
        "cacheReadInputTokens": 56000,
        "outputTokens": 789,
    }
    first, second = (str(case_id) for case_id in story.case_ids)
    assert [(entry["phase"], entry["testCaseId"]) for entry in log["entries"]] == [
        ("setup", None),
        ("setup", None),
        ("setup", None),
        ("case", first),
        ("case", first),
        ("case", second),
        ("case", second),
        ("wrap_up", None),
        ("wrap_up", None),
    ]
    typed = log["entries"][3]
    assert typed["input"] == {"action": "type", "text": MASKED_VALUE}
    assert typed["output"] == f"Typed {MASKED_VALUE}"
    assert typed["durationMs"] == 420
    assert log["entries"][2] == {
        "position": 2,
        "phase": "setup",
        "testCaseId": None,
        "kind": "note",
        "at": "2026-11-01T09:00:02Z",
        "tool": None,
        "input": None,
        "output": "Signing in as the buyer.",
        "isError": False,
        "durationMs": None,
    }
    assert len(log["entries"][7]["output"]) == 4000
    assert log["entries"][5]["isError"] is True
    assert recording_live_event_publisher.events[-1].type is LiveEventType.RUN_LOG_RECEIVED


async def test_the_log_can_be_read_for_one_case_and_sending_it_again_replaces_it(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    story, runner, run_id = await finished_run(client, container, recording_mailer)
    await upload(client, runner.token, run_id, build_log(story.case_ids, run_id))
    shorter: dict[str, object] = {"entries": [{"kind": "note", "at": at(0), "text": "Again"}]}

    one_case = (await read_log(client, runner, story, run_id, caseId=str(story.case_ids[1]))).json()
    await upload(client, runner.token, run_id, shorter)
    replaced = (await read_log(client, runner, story, run_id)).json()

    assert [entry["position"] for entry in one_case["entries"]] == [5, 6]
    assert [entry["output"] for entry in replaced["entries"]] == ["Again"]
    assert replaced["usage"]["outputTokens"] == 0


async def test_a_run_without_a_log_says_so(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    story, runner, run_id = await finished_run(client, container, recording_mailer)

    log = (await read_log(client, runner, story, run_id)).json()

    assert log == {"receivedAt": None, "isCut": False, "usage": None, "entries": []}


async def test_the_log_is_refused_while_the_run_is_running_and_after_a_day(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    body = build_log(story.case_ids, run_id)

    running = await upload(client, runner.token, run_id, body)
    await finish(client, runner.token, run_id)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunTable)
            .where(RunTable.id == UUID(run_id))
            .values(finished_at=datetime.now(UTC) - timedelta(hours=25))
        )
    late = await upload(client, runner.token, run_id, body)

    assert (running.status_code, running.json()["code"]) == (409, "CONFLICT")
    assert (late.status_code, late.json()["code"]) == (409, "CONFLICT")


async def test_only_the_starter_can_send_the_log(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    story, _, run_id = await finished_run(client, container, recording_mailer)
    other = await sign_up_runner(client, container, recording_mailer, story.project, name="Olga Other")

    response = await upload(client, other.token, run_id, build_log(story.case_ids, run_id))
    unknown = await upload(client, other.token, str(uuid4()), build_log(story.case_ids, run_id))

    assert (response.status_code, response.json()["code"]) == (403, "RUN_NOT_OWNED")
    assert unknown.status_code == 404


async def test_a_viewer_can_read_the_log(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    story, runner, run_id = await finished_run(client, container, recording_mailer)
    await upload(client, runner.token, run_id, build_log(story.case_ids, run_id))
    viewer = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.VIEWER, "Vi Viewer")

    log = (await read_log(client, viewer, story, run_id)).json()

    assert len(log["entries"]) == 9


def test_entries_before_the_first_browser_action_are_setup_when_no_case_is_recorded() -> None:
    entries = [
        UploadedLogEntry(kind=RunLogEntryKind.ACTION, at=STARTED_AT, tool="Bash"),
        UploadedLogEntry(kind=RunLogEntryKind.NOTE, at=STARTED_AT, text="Down"),
    ]

    assert assign_phases(entries, set()) == [(RunLogPhase.SETUP, None), (RunLogPhase.SETUP, None)]

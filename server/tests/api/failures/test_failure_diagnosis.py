from uuid import UUID

from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.failures.test_run_result_wiring import WiredStory, set_up_wired_story
from tests.api.projects.user_steps import use_session
from tests.api.runs.manual.manual_run_steps import build_step, finish_manual_run, record_case
from tests.api.runs.run_steps import finish, record_case_id, start_run_id
from tests.api.story_context.story_context_steps import STAGING_PASSWORD, add_token_holder
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

FAILING_STEP = {
    "order": 1,
    "status": "failed",
    "actual_result": "The payment page shows Something went wrong",
    "error": "Expected the order confirmation",
    "page_url": "https://staging.shop.test/checkout?session=abc#pay",
    "console_errors": ["TypeError: Cannot read properties of undefined (reading 'card')"],
    "failed_requests": [
        {
            "method": "post",
            "path": "/api/payments?card=4242",
            "status": 502,
            "excerpt": f"Bad gateway for {STAGING_PASSWORD}",
        }
    ],
}


async def run_with_diagnosis(client: AsyncClient, wired_story: WiredStory, cause: str = "app_bug") -> str:
    token = wired_story.holder.token
    run_id = await start_run_id(client, token, wired_story.context_project.story.jira_key)
    recorded = await call_tool(
        client,
        token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(wired_story.failing_case.id),
            "status": "failed",
            "duration_ms": 900,
            "steps": [FAILING_STEP],
            "suspected_cause": cause,
            "cause_reason": "The payments API answered 502",
        },
    )
    read_tool_json(recorded)
    await record_case_id(client, token, run_id, wired_story.passing_case.id, "passed")
    read_tool_json(await finish(client, token, run_id))
    return run_id


async def find_failure_id(client: AsyncClient, wired_story: WiredStory) -> UUID:
    use_session(client, wired_story.holder.account.session_token)
    listed = await client.get(
        f"/api/projects/{wired_story.context_project.key}/failures",
        params={"testCaseId": str(wired_story.failing_case.id)},
    )
    [failure] = listed.json()
    return UUID(failure["id"])


async def change_cause(client: AsyncClient, wired_story: WiredStory, failure_id: UUID, **body: object) -> Response:
    return await client.put(f"/api/projects/{wired_story.context_project.key}/failures/{failure_id}/cause", json=body)


async def test_a_failed_step_keeps_its_diagnosis_and_the_case_its_suspected_cause(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    wired_story = await set_up_wired_story(client, container, recording_mailer)
    run_id = await run_with_diagnosis(client, wired_story)
    use_session(client, wired_story.holder.account.session_token)

    detail = await client.get(f"/api/projects/{wired_story.context_project.key}/runs/{run_id}")

    assert STAGING_PASSWORD not in detail.text
    failing_case, passing_case = detail.json()["cases"]
    assert failing_case["result"]["suspectedCause"] == "app_bug"
    assert failing_case["result"]["causeReason"] == "The payments API answered 502"
    assert failing_case["steps"][0]["diagnosis"] == {
        "pageUrl": "https://staging.shop.test/checkout",
        "consoleErrors": ["TypeError: Cannot read properties of undefined (reading 'card')"],
        "failedRequests": [
            {"method": "POST", "path": "/api/payments", "status": 502, "excerpt": "Bad gateway for ••••"}
        ],
    }
    assert passing_case["result"]["suspectedCause"] is None
    assert passing_case["steps"][0]["diagnosis"] is None
    [failed_case_report] = detail.json()["report"]["failedCases"]
    assert failed_case_report["suspectedCause"] == "app_bug"
    assert failed_case_report["causeReason"] == "The payments API answered 502"

    failure = await client.get(
        f"/api/projects/{wired_story.context_project.key}/failures/{await find_failure_id(client, wired_story)}"
    )
    assert failure.json()["cause"] == "app_bug"
    assert failure.json()["causeReason"] == "The payments API answered 502"
    assert failure.json()["failedStep"]["diagnosis"]["failedRequests"][0]["status"] == 502


async def test_a_person_can_change_the_cause_and_later_failures_keep_it(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    wired_story = await set_up_wired_story(client, container, recording_mailer)
    await run_with_diagnosis(client, wired_story)
    failure_id = await find_failure_id(client, wired_story)

    changed = await change_cause(client, wired_story, failure_id, cause="test_data", reason="  The card expired  ")
    await run_with_diagnosis(client, wired_story, cause="environment")
    use_session(client, wired_story.holder.account.session_token)
    detail = await client.get(f"/api/projects/{wired_story.context_project.key}/failures/{failure_id}")

    assert changed.status_code == 200, changed.text
    assert changed.json()["cause"] == "test_data"
    assert changed.json()["causeReason"] == "The card expired"
    assert changed.json()["causeChangedAt"] is not None
    assert detail.json()["cause"] == "test_data"
    cause_events = [event for event in detail.json()["events"] if event["kind"] == "cause_changed"]
    assert [(event["fromCause"], event["toCause"], event["actorName"]) for event in cause_events] == [
        ("app_bug", "test_data", "Claude Owner")
    ]


async def test_a_viewer_cannot_change_the_cause(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    wired_story = await set_up_wired_story(client, container, recording_mailer)
    await run_with_diagnosis(client, wired_story)
    failure_id = await find_failure_id(client, wired_story)
    viewer = await add_token_holder(
        client, container, recording_mailer, wired_story.context_project.project, ProjectRole.VIEWER, "Vera Viewer"
    )
    use_session(client, viewer.account.session_token)

    refused = await change_cause(client, wired_story, failure_id, cause="test_data")

    assert refused.status_code == 403


async def test_a_manual_result_keeps_the_testers_suspected_cause_only_when_it_fails(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    wired_story = await set_up_wired_story(client, container, recording_mailer)
    use_session(client, wired_story.holder.account.session_token)
    project_key = wired_story.context_project.key
    started = await client.post(
        f"/api/projects/{project_key}/runs", json={"storyKey": wired_story.context_project.story.jira_key}
    )
    run_id = started.json()["id"]

    failing = await record_case(
        client,
        project_key,
        run_id,
        wired_story.failing_case.id,
        steps=[build_step(1, "failed")],
        suspectedCause="environment",
        causeReason="Staging was down",
    )
    passing = await record_case(
        client,
        project_key,
        run_id,
        wired_story.passing_case.id,
        steps=[build_step(1, "passed")],
        suspectedCause="app_bug",
    )
    await finish_manual_run(client, project_key, run_id)
    detail = await client.get(f"/api/projects/{project_key}/runs/{run_id}")

    assert failing.status_code == 200, failing.text
    assert passing.status_code == 200, passing.text
    results = [case["result"] for case in detail.json()["cases"]]
    assert [(result["suspectedCause"], result["causeReason"]) for result in results] == [
        ("environment", "Staging was down"),
        (None, None),
    ]

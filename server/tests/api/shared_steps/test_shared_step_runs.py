from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from httpx import AsyncClient, Response
from pydantic import JsonValue

from app.container import Container
from app.modules.shared_steps import SharedStepRepository
from app.modules.test_cases import CaseStepExpander
from app.modules.test_cases import TestCaseVersion as CaseVersion
from tests.api.runs.run_steps import build_steps, finish, read_tool_error_code, start_run_for
from tests.api.shared_steps.shared_step_steps import (
    SharedStepProject,
    create_case_with,
    create_shared_step_json,
    drop_run_snapshots,
    find_case_id,
    get_run_detail,
    make_ready,
    set_up_shared_step_project,
    update_shared_step,
)
from tests.api.suites.suite_steps import create_suite_id, set_suite_cases
from tests.api.test_cases.case_steps import seed_data_item
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

ROLE_ROWS: list[JsonValue] = [{"role": "admin"}, {"role": "viewer"}]
EXPANDED_STEPS = [
    {"order": 1, "action": "Open {{data.base_url}}/sign-in", "expected": "The sign-in form is shown"},
    {"order": 2, "action": "Sign in as {{param.role}}", "expected": "The dashboard is shown"},
    {"order": 3, "action": "Pay", "expected": "Paid"},
]


@dataclass(frozen=True)
class DataDrivenWorld:
    world: SharedStepProject
    data_case_id: UUID
    plain_case_id: UUID

    @property
    def key(self) -> str:
        return self.world.key

    @property
    def token(self) -> str:
        return self.world.runner.token

    @property
    def story_key(self) -> str:
        return self.world.story.jira_key


async def set_up_data_driven_world(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> DataDrivenWorld:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await seed_data_item(container, world.project, "base_url")
    await create_shared_step_json(client, world.key)
    data_code = await create_case_with(
        client,
        world.key,
        world.story.jira_key,
        steps=[{"sharedStepKey": "log_in"}, {"action": "Pay", "expected": "Paid"}],
        parameters=["role"],
        dataRows=ROLE_ROWS,
    )
    plain_code = await create_case_with(
        client, world.key, world.story.jira_key, steps=[{"action": "Browse", "expected": "Shown"}]
    )
    for code in (data_code, plain_code):
        await make_ready(client, world.key, code)
    return DataDrivenWorld(
        world=world,
        data_case_id=await find_case_id(client, world.key, data_code),
        plain_case_id=await find_case_id(client, world.key, plain_code),
    )


async def start(client: AsyncClient, world: DataDrivenWorld, **arguments: object) -> dict[str, object]:
    return read_tool_json(await start_run_for(client, world.token, world.story_key, **arguments))


async def record(
    client: AsyncClient,
    world: DataDrivenWorld,
    run_id: str,
    case_id: UUID,
    status: str,
    iteration: int | None = None,
    step_count: int = 3,
) -> Response:
    arguments: dict[str, object] = {
        "run_id": run_id,
        "case_id": str(case_id),
        "status": status,
        "duration_ms": 500,
        "steps": build_steps([status] * step_count),
    }
    if iteration is not None:
        arguments["iteration"] = iteration
    return await call_tool(client, world.token, "record_case_result", arguments)


async def record_id(
    client: AsyncClient,
    world: DataDrivenWorld,
    run_id: str,
    case_id: UUID,
    status: str,
    iteration: int | None = None,
    step_count: int = 3,
) -> str:
    content = read_tool_json(await record(client, world, run_id, case_id, status, iteration, step_count))
    case_result_id = content["case_result_id"]
    assert isinstance(case_result_id, str)
    return case_result_id


def find_case(content: dict[str, object], case_id: UUID) -> dict[str, object]:
    cases = content["cases"]
    assert isinstance(cases, list)
    found: dict[str, object] = next(case for case in cases if case["case_id"] == str(case_id))
    return found


async def test_start_run_expands_shared_steps_renumbers_them_and_lists_the_data_rows(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)

    content = await start(client, world)

    data_case = find_case(content, world.data_case_id)
    plain_case = find_case(content, world.plain_case_id)
    assert data_case["steps"] == EXPANDED_STEPS
    assert data_case["parameters"] == ["role"]
    assert data_case["data_rows"] == ROLE_ROWS
    assert plain_case["steps"] == [{"order": 1, "action": "Browse", "expected": "Shown"}]
    assert "parameters" not in plain_case
    assert "data_rows" not in plain_case


async def test_a_run_keeps_its_snapshot_after_the_shared_step_changes(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])

    await update_shared_step(client, world.key, "log_in", 1, steps=[{"action": "Sign in with SSO"}])
    await record_id(client, world, run_id, world.data_case_id, "passed", iteration=0, step_count=3)
    detail = (await get_run_detail(client, world.key, run_id)).json()
    await finish(client, world.token, run_id)
    next_run = await start(client, world)

    data_case = next(case for case in detail["cases"] if case["testCaseId"] == str(world.data_case_id))
    assert [(step["order"], step["action"], step["status"]) for step in data_case["steps"]] == [
        (1, "Open {{data.base_url}}/sign-in", "passed"),
        (2, "Sign in as {{param.role}}", "passed"),
        (3, "Pay", "passed"),
    ]
    assert find_case(next_run, world.data_case_id)["steps"] == [
        {"order": 1, "action": "Sign in with SSO", "expected": None},
        {"order": 2, "action": "Pay", "expected": "Paid"},
    ]


async def test_step_results_are_checked_against_the_snapshot(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])

    beyond_snapshot = await call_tool(
        client,
        world.token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(world.data_case_id),
            "status": "passed",
            "duration_ms": 1,
            "steps": build_steps(["passed"] * 4),
        },
    )

    assert read_tool_error_code(beyond_snapshot) == "INVALID_REQUEST"


async def test_the_context_tools_return_expanded_steps_and_data_rows(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key, "Sign-in regression")
    suite_response = await set_suite_cases(client, world.key, suite_id, [world.data_case_id])
    assert suite_response.status_code == 200, suite_response.text

    story_context = read_tool_json(
        await call_tool(client, world.token, "get_story_context", {"story_key": world.story_key})
    )
    suite_context = read_tool_json(
        await call_tool(client, world.token, "get_suite_context", {"suite": "Sign-in regression"})
    )

    story_cases = story_context["cases"]
    assert isinstance(story_cases, list)
    story_case = next(case for case in story_cases if case["id"] == str(world.data_case_id))
    suite_stories = suite_context["stories"]
    assert isinstance(suite_stories, list)
    suite_case = suite_stories[0]["cases"][0]
    for case in (story_case, suite_case):
        assert case["steps"] == EXPANDED_STEPS
        assert case["parameters"] == ["role"]
        assert case["data_rows"] == ROLE_ROWS
        assert case["data_keys"] == ["base_url"]
    for context in (story_context, suite_context):
        data = context["data"]
        assert isinstance(data, list)
        assert [entry["key"] for entry in data] == ["base_url"]


class RecordingCaseStepExpander(CaseStepExpander):
    def __init__(self, shared_step_repository: SharedStepRepository) -> None:
        super().__init__(shared_step_repository)
        self.expanded_project_ids: list[UUID] = []

    async def expand(self, project_id: UUID, versions: Sequence[CaseVersion]) -> list[CaseVersion]:
        self.expanded_project_ids.append(project_id)
        return await super().expand(project_id, versions)


async def test_the_story_context_reader_uses_the_container_case_step_expander(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    recording_expander = RecordingCaseStepExpander(container.shared_step_repository)
    container.__dict__.pop("story_context_reader", None)
    container.__dict__["case_step_expander"] = recording_expander

    async with container.database.begin():
        cases = await container.story_context_reader.list_ready_cases(world.world.story.id)

    assert recording_expander.expanded_project_ids == [world.world.project.id]
    data_case = next(case for case in cases if case.id == world.data_case_id)
    assert [step.order for step in data_case.steps] == [1, 2, 3]


async def test_each_iteration_is_recorded_once_and_must_exist(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])

    await record_id(client, world, run_id, world.data_case_id, "passed", iteration=0)
    await record_id(client, world, run_id, world.data_case_id, "passed", iteration=1)
    again = await call_tool(
        client,
        world.token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(world.data_case_id),
            "status": "passed",
            "duration_ms": 1,
            "steps": build_steps(["passed"]),
        },
    )
    out_of_range = await call_tool(
        client,
        world.token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(world.data_case_id),
            "status": "passed",
            "duration_ms": 1,
            "steps": build_steps(["passed"]),
            "iteration": 2,
        },
    )
    plain_second = await call_tool(
        client,
        world.token,
        "record_case_result",
        {
            "run_id": run_id,
            "case_id": str(world.plain_case_id),
            "status": "passed",
            "duration_ms": 1,
            "steps": build_steps(["passed"]),
            "iteration": 1,
        },
    )

    assert read_tool_error_code(again) == "CASE_RESULT_EXISTS"
    assert read_tool_error_code(out_of_range) == "ITERATION_OUT_OF_RANGE"
    assert read_tool_error_code(plain_second) == "ITERATION_OUT_OF_RANGE"


async def test_the_worst_iteration_decides_the_case_result_counts_failures_and_latest_result(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])

    failed_id = await record_id(client, world, run_id, world.data_case_id, "failed", iteration=0)
    await record_id(client, world, run_id, world.data_case_id, "failed", iteration=1)
    await record_id(client, world, run_id, world.plain_case_id, "passed", step_count=1)
    finished = read_tool_json(await finish(client, world.token, run_id))
    detail = (await get_run_detail(client, world.key, run_id)).json()
    runs = (await client.get(f"/api/projects/{world.key}/runs")).json()
    latest = (await client.get(f"/api/projects/{world.key}/case-latest-results")).json()
    failures = (await client.get(f"/api/projects/{world.key}/failures")).json()

    assert finished["status"] == "failed"
    data_case = next(case for case in detail["cases"] if case["testCaseId"] == str(world.data_case_id))
    assert data_case["result"]["status"] == "failed"
    assert data_case["result"]["iteration"] == 0
    assert data_case["parameters"] == ["role"]
    assert [
        (iteration["iteration"], iteration["values"], iteration["result"]["status"])
        for iteration in data_case["iterations"]
    ] == [(0, {"role": "admin"}, "failed"), (1, {"role": "viewer"}, "failed")]
    assert next(case for case in detail["cases"] if case["testCaseId"] == str(world.plain_case_id))["iterations"] == []
    assert detail["counts"] == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "blocked": 0,
        "skipped": 0,
        "notReported": 0,
    }
    assert detail["report"]["counts"]["failed"] == 1
    listed_run = next(run for run in runs if run["id"] == run_id)
    assert listed_run["counts"]["failed"] == 1
    assert listed_run["counts"]["passed"] == 1
    latest_by_case = {item["caseId"]: item["latestResult"] for item in latest}
    assert latest_by_case[str(world.data_case_id)]["status"] == "failed"
    case_failures = [failure for failure in failures if failure["testCaseId"] == str(world.data_case_id)]
    assert len(case_failures) == 1
    assert case_failures[0]["openedByCaseResultId"] == failed_id
    assert case_failures[0]["latestCaseResultId"] == failed_id


async def test_a_failures_result_history_names_each_iteration(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])
    first_id = await record_id(client, world, run_id, world.data_case_id, "failed", iteration=0)
    second_id = await record_id(client, world, run_id, world.data_case_id, "passed", iteration=1)
    plain_id = await record_id(client, world, run_id, world.plain_case_id, "failed", step_count=1)
    failures = (await client.get(f"/api/projects/{world.key}/failures")).json()
    failure_ids = {failure["testCaseId"]: failure["id"] for failure in failures}

    data_detail = await client.get(f"/api/projects/{world.key}/failures/{failure_ids[str(world.data_case_id)]}")
    plain_detail = await client.get(f"/api/projects/{world.key}/failures/{failure_ids[str(world.plain_case_id)]}")

    assert data_detail.status_code == 200, data_detail.text
    assert [(result["caseResultId"], result["iteration"]) for result in data_detail.json()["results"]] == [
        (second_id, 1),
        (first_id, 0),
    ]
    assert plain_detail.status_code == 200, plain_detail.text
    assert [(result["caseResultId"], result["iteration"]) for result in plain_detail.json()["results"]] == [
        (plain_id, None)
    ]


async def test_a_passed_iteration_never_hides_a_failed_one(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])

    await record_id(client, world, run_id, world.data_case_id, "passed", iteration=1)
    await record_id(client, world, run_id, world.data_case_id, "failed", iteration=0)
    await record_id(client, world, run_id, world.plain_case_id, "passed", step_count=1)
    detail = (await get_run_detail(client, world.key, run_id)).json()
    latest = (await client.get(f"/api/projects/{world.key}/case-latest-results")).json()

    data_case = next(case for case in detail["cases"] if case["testCaseId"] == str(world.data_case_id))
    assert data_case["result"]["status"] == "failed"
    latest_by_case = {item["caseId"]: item["latestResult"] for item in latest}
    assert latest_by_case[str(world.data_case_id)]["status"] == "failed"


async def test_the_manual_route_records_an_iteration(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    created = await client.post(
        f"/api/projects/{world.key}/runs",
        json={"storyKey": world.story_key, "testCaseIds": [str(world.data_case_id)]},
    )
    assert created.status_code == 201, created.text
    run_id = created.json()["id"]
    path = f"/api/projects/{world.key}/runs/{run_id}/cases/{world.data_case_id}"
    steps = [{"order": order, "status": "passed", "actualResult": "Fine"} for order in (1, 2, 3)]

    first = await client.put(path, json={"steps": steps, "iteration": 1})
    again = await client.put(path, json={"steps": steps, "iteration": 1})
    out_of_range = await client.put(path, json={"steps": steps, "iteration": 2})
    beyond_snapshot = await client.put(path, json={"steps": [{"order": 4, "status": "passed"}]})

    manual_case = created.json()["cases"][0]
    assert [step["action"] for step in manual_case["steps"]] == [
        "Open {{data.base_url}}/sign-in",
        "Sign in as {{param.role}}",
        "Pay",
    ]
    assert manual_case["parameters"] == ["role"]
    assert manual_case["dataRows"] == ROLE_ROWS
    assert first.status_code == 200, first.text
    assert again.status_code == 409
    assert again.json()["code"] == "CASE_RESULT_EXISTS"
    assert out_of_range.status_code == 422
    assert out_of_range.json()["code"] == "ITERATION_OUT_OF_RANGE"
    assert beyond_snapshot.status_code == 422


async def test_an_old_run_without_a_snapshot_falls_back_to_the_case_version(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world, case_ids=[str(world.plain_case_id)]))["run_id"])
    await drop_run_snapshots(container, run_id)

    too_many = await record(client, world, run_id, world.plain_case_id, "passed", step_count=2)
    await record_id(client, world, run_id, world.plain_case_id, "passed", step_count=1)
    detail = (await get_run_detail(client, world.key, run_id)).json()

    assert read_tool_error_code(too_many) == "INVALID_REQUEST"
    assert [(step["order"], step["action"], step["status"]) for step in detail["cases"][0]["steps"]] == [
        (1, "Browse", "passed")
    ]


async def test_iterations_of_one_run_count_once_for_the_flaky_score(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    for statuses in (("passed", "failed"), ("passed", "passed"), ("failed", "passed")):
        run_id = str((await start(client, world, case_ids=[str(world.data_case_id)]))["run_id"])
        for iteration, status in enumerate(statuses):
            await record_id(client, world, run_id, world.data_case_id, status, iteration=iteration)
        await finish(client, world.token, run_id)

    await container.recompute_flaky.execute(world.data_case_id)
    detail = (await client.get(f"/api/projects/{world.key}/test-cases/TC-1")).json()

    assert detail["flakyScore"] == 2

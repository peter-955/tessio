from httpx import AsyncClient

from app.container import Container
from tests.api.runs.run_steps import finish
from tests.api.shared_steps.shared_step_steps import get_run_detail
from tests.api.shared_steps.test_shared_step_runs import set_up_data_driven_world, start
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def test_missing_screenshots_name_the_iteration_of_a_data_driven_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    run_id = str((await start(client, world))["run_id"])
    recordings = [(world.data_case_id, 0), (world.data_case_id, 1), (world.plain_case_id, None)]
    for case_id, iteration in recordings:
        arguments: dict[str, object] = {
            "run_id": run_id,
            "case_id": str(case_id),
            "status": "passed",
            "duration_ms": 10,
            "steps": [{"order": 1, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/1.jpg"}],
        }
        if iteration is not None:
            arguments["iteration"] = iteration
        read_tool_json(await call_tool(client, world.token, "record_case_result", arguments))

    content = read_tool_json(await finish(client, world.token, run_id))

    detail = (await get_run_detail(client, world.key, run_id)).json()
    code_by_case_id = {case["testCaseId"]: case["code"] for case in detail["cases"]}
    data_code = code_by_case_id[str(world.data_case_id)]
    plain_code = code_by_case_id[str(world.plain_case_id)]
    missing = content["missing_screenshots"]
    assert isinstance(missing, list)
    assert sorted(missing, key=lambda item: (item["code"], item.get("iteration", -1))) == sorted(
        [
            {"code": data_code, "step_order": 1, "iteration": 0},
            {"code": data_code, "step_order": 1, "iteration": 1},
            {"code": plain_code, "step_order": 1},
        ],
        key=lambda item: (item["code"], item.get("iteration", -1)),
    )
    report = detail["report"]
    iterations_by_case = {
        (item["testCaseId"], item["iteration"]) for item in report["missingScreenshots"] if item["stepOrder"] == 1
    }
    assert iterations_by_case == {
        (str(world.data_case_id), 0),
        (str(world.data_case_id), 1),
        (str(world.plain_case_id), None),
    }


async def test_the_manual_record_reply_names_the_iteration(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_data_driven_world(client, container, recording_mailer)
    created = await client.post(
        f"/api/projects/{world.key}/runs",
        json={"storyKey": world.story_key, "testCaseIds": [str(world.data_case_id), str(world.plain_case_id)]},
    )
    assert created.status_code == 201, created.text
    run_id = created.json()["id"]
    steps = [{"order": 1, "status": "passed", "actualResult": "Fine"}]

    data_reply = await client.put(
        f"/api/projects/{world.key}/runs/{run_id}/cases/{world.data_case_id}", json={"steps": steps, "iteration": 1}
    )
    plain_reply = await client.put(
        f"/api/projects/{world.key}/runs/{run_id}/cases/{world.plain_case_id}", json={"steps": steps}
    )

    assert data_reply.status_code == 200, data_reply.text
    assert data_reply.json()["iteration"] == 1
    assert plain_reply.status_code == 200, plain_reply.text
    assert plain_reply.json()["iteration"] == 0
    detail = (await get_run_detail(client, world.key, run_id)).json()
    data_case = next(case for case in detail["cases"] if case["testCaseId"] == str(world.data_case_id))
    assert [(item["iteration"], item["result"] is not None) for item in data_case["iterations"]] == [
        (0, False),
        (1, True),
    ]
    assert data_case["iterations"][1]["result"]["id"] == data_reply.json()["id"]

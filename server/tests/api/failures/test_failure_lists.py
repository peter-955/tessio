from uuid import UUID

from httpx import AsyncClient, Response

from app.container import Container
from app.modules.failures import FailureStatus
from app.modules.runs import ResultStatus
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import (
    SeededStep,
    assign,
    find_only_failure,
    open_failure,
    record,
    seed_case,
    seed_scenario,
    seed_screenshot,
    set_failure_status,
)
from tests.api.gaps.gap_steps import add_active_member, seed_story, sign_up_account
from tests.api.projects.user_steps import use_session
from tests.api.test_data.project_steps import sign_up_member
from tests.conftest import RecordingMailer


def read_ids(response: Response) -> list[str]:
    assert response.status_code == 200, response.text
    return [failure["id"] for failure in response.json()]


async def test_the_list_filters_failures(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    other_story = await seed_story(container, scenario.project)
    second_case = await seed_case(container, scenario.project, scenario.story.id, 2, scenario.runner.user_id)
    third_case = await seed_case(container, scenario.project, other_story.id, 3, scenario.runner.user_id)
    first_id = await open_failure(container, scenario)
    await record(container, scenario, ResultStatus.FAILED, case=second_case)
    second_id = (await find_only_failure(container, second_case.id)).id
    await record(container, scenario, ResultStatus.FAILED, case=third_case)
    third_id = (await find_only_failure(container, third_case.id)).id
    await set_failure_status(container, second_id, FailureStatus.FIXED)
    await set_failure_status(container, third_id, FailureStatus.VERIFIED)
    developer_id = await add_active_member(container, recording_mailer, scenario.project, ProjectRole.DEV, "Dee Dev")
    tester = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.QC)
    assert (await assign(client, scenario.project.key, first_id, developer_id)).status_code == 200
    url = f"/api/projects/{scenario.project.key}/failures"

    all_ids = read_ids(await client.get(url))
    fixed_or_verified = read_ids(await client.get(url, params=[("status", "fixed"), ("status", "verified")]))
    open_ids = read_ids(await client.get(url, params={"status": "open"}))
    assigned_ids = read_ids(await client.get(url, params={"assigneeId": str(developer_id)}))
    tester_ids = read_ids(await client.get(url, params={"assigneeId": str(tester.user_id)}))
    unassigned_ids = read_ids(await client.get(url, params={"unassigned": "true"}))
    story_ids = read_ids(await client.get(url, params={"storyKey": other_story.jira_key.lower()}))
    unknown_story_ids = read_ids(await client.get(url, params={"storyKey": "NOPE-1"}))
    case_ids = read_ids(await client.get(url, params={"testCaseId": str(second_case.id)}))

    assert all_ids == [str(third_id), str(second_id), str(first_id)]
    assert fixed_or_verified == [str(third_id), str(second_id)]
    assert open_ids == [str(first_id)]
    assert assigned_ids == [str(first_id)]
    assert tester_ids == []
    assert unassigned_ids == [str(third_id), str(second_id)]
    assert story_ids == [str(third_id)]
    assert unknown_story_ids == []
    assert case_ids == [str(second_id)]


async def test_the_list_item_carries_the_case_story_and_latest_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    await record(container, scenario, ResultStatus.FAILED)
    latest = await record(container, scenario, ResultStatus.FAILED)

    response = await client.get(f"/api/projects/{scenario.project.key}/failures")

    assert response.status_code == 200, response.text
    [item] = response.json()
    assert item["projectKey"] == scenario.project.key
    assert item["storyId"] == str(scenario.story.id)
    assert item["storyJiraKey"] == scenario.story.jira_key
    assert item["storyTitle"] == f"Story {scenario.story.jira_key}"
    assert item["testCaseId"] == str(scenario.case.id)
    assert item["testCaseCode"] == "TC-1"
    assert item["testCaseTitle"] == "Case 1"
    assert item["status"] == "open"
    assert item["isActive"] is True
    assert item["assigneeId"] is None
    assert item["latestCaseResultId"] == str(latest.case_result_id)
    assert item["latestRunId"] == str(latest.run_id)
    assert item["latestFailedAt"] is not None


async def test_both_assignee_filters_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)

    response = await client.get(
        f"/api/projects/{scenario.project.key}/failures",
        params={"assigneeId": str(scenario.runner.user_id), "unassigned": "true"},
    )

    assert response.status_code == 422
    assert response.json() == {"code": "INVALID_REQUEST", "message": "Use either assigneeId or unassigned, not both."}


async def test_another_projects_failure_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    failure_id = await open_failure(container, scenario)
    other = await seed_scenario(client, container, recording_mailer)

    detail = await client.get(f"/api/projects/{other.project.key}/failures/{failure_id}")
    listed = await client.get(f"/api/projects/{other.project.key}/failures")

    assert detail.status_code == 404
    assert detail.json() == {"code": "NOT_FOUND", "message": "Failure not found."}
    assert read_ids(listed) == []


async def test_a_non_member_cannot_list(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    await open_failure(container, scenario)
    await sign_up_member(client, container, recording_mailer, scenario.project, None)

    response = await client.get(f"/api/projects/{scenario.project.key}/failures")

    assert response.status_code == 404


async def test_the_detail_has_the_failed_step_history_and_events(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    screenshot_id = await seed_screenshot(container, scenario.project, scenario.runner.user_id)
    earlier = await record(container, scenario, ResultStatus.PASSED)
    opening = await record(container, scenario, ResultStatus.FAILED)
    passed = await record(container, scenario, ResultStatus.PASSED)
    latest = await record(
        container,
        scenario,
        ResultStatus.FAILED,
        steps=(
            SeededStep(order=1, status=ResultStatus.PASSED, actual_result="Opened the cart."),
            SeededStep(
                order=2,
                status=ResultStatus.FAILED,
                actual_result="The total stayed at 0.",
                error="Expected 42.",
                screenshot_file_id=screenshot_id,
            ),
            SeededStep(order=3, status=ResultStatus.FAILED, actual_result="Checkout stayed disabled."),
        ),
    )
    failure_id = (await find_only_failure(container, scenario.case.id)).id
    developer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.DEV, "Dee Dev")
    assert (await assign(client, scenario.project.key, failure_id, developer.user_id)).status_code == 200
    assert (
        await client.put(f"/api/projects/{scenario.project.key}/failures/{failure_id}/status", json={"status": "fixed"})
    ).status_code == 200
    viewer = await sign_up_account(client, container, recording_mailer, scenario.project, ProjectRole.VIEWER)
    use_session(client, viewer.session_token)

    response = await client.get(f"/api/projects/{scenario.project.key}/failures/{failure_id}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["id"] == str(failure_id)
    assert body["status"] == "fixed"
    assert body["assigneeName"] == "Dee Dev"
    assert body["statusChangedByName"] == "Dee Dev"
    assert body["failedStep"] == {
        "stepOrder": 2,
        "actualResult": "The total stayed at 0.",
        "error": "Expected 42.",
        "screenshotFileId": str(screenshot_id),
    }
    assert [result["caseResultId"] for result in body["results"]] == [
        str(latest.case_result_id),
        str(passed.case_result_id),
        str(opening.case_result_id),
    ]
    assert str(earlier.case_result_id) not in [result["caseResultId"] for result in body["results"]]
    first_result = body["results"][0]
    assert first_result["runId"] == str(latest.run_id)
    assert first_result["runStatus"] == "failed"
    assert first_result["runExecutor"] == "claude"
    assert first_result["status"] == "failed"
    assert first_result["durationMs"] == 1200
    assert first_result["startedByName"] == "Quinn Runner"
    assert [(event["kind"], event["toStatus"]) for event in body["events"]] == [
        ("opened", "open"),
        ("failed_again", None),
        ("assigned", None),
        ("status_changed", "fixed"),
    ]
    opened_event, failed_again_event, assigned_event, fixed_event = body["events"]
    assert opened_event["runId"] == str(opening.run_id)
    assert opened_event["actorId"] is None
    assert failed_again_event["caseResultId"] == str(latest.case_result_id)
    assert assigned_event["assigneeName"] == "Dee Dev"
    assert assigned_event["actorName"] == "Dee Dev"
    assert fixed_event["fromStatus"] == "open"
    assert fixed_event["actorId"] == str(developer.user_id)


async def test_a_failed_result_without_steps_has_no_failed_step(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    failure_id: UUID = await open_failure(container, scenario)

    response = await client.get(f"/api/projects/{scenario.project.key}/failures/{failure_id}")

    assert response.status_code == 200, response.text
    assert response.json()["failedStep"] is None
    assert len(response.json()["results"]) == 1

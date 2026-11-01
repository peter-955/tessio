from httpx import AsyncClient

from app.container import Container
from app.modules.failures import FailureStatus
from app.modules.runs import ResultStatus
from app.modules.stories import TestStatus as StoryTestStatus
from app.shared.permissions import ProjectRole
from tests.api.failures.failure_steps import (
    as_failures_container,
    change_status,
    find_only_failure,
    open_failure,
    record,
    seed_case,
    seed_scenario,
    set_failure_status,
    set_story_test_status,
)
from tests.api.gaps.gap_steps import seed_story
from tests.api.test_data.project_steps import sign_up_member
from tests.conftest import RecordingMailer


async def test_the_counter_counts_active_failures_per_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    other_story = await seed_story(container, scenario.project)
    cases = [
        await seed_case(container, scenario.project, scenario.story.id, number, scenario.runner.user_id)
        for number in (2, 3, 4)
    ]
    other_case = await seed_case(container, scenario.project, other_story.id, 5, scenario.runner.user_id)
    for case, status in zip(cases, (FailureStatus.FIXED, FailureStatus.REOPENED, FailureStatus.VERIFIED), strict=True):
        await record(container, scenario, ResultStatus.FAILED, case=case)
        await set_failure_status(container, (await find_only_failure(container, case.id)).id, status)
    await open_failure(container, scenario)
    await record(container, scenario, ResultStatus.FAILED, case=other_case)
    empty_story = await seed_story(container, scenario.project)
    counter = as_failures_container(container).count_active_failures

    assert await counter.count_active_for_story(scenario.project.id, scenario.story.id) == 3
    assert await counter.count_active_for_story(scenario.project.id, other_story.id) == 1
    assert await counter.count_active_for_story(scenario.project.id, empty_story.id) == 0


async def test_an_active_failure_blocks_story_sign_off_until_verified(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    scenario = await seed_scenario(client, container, recording_mailer)
    failure_id = await open_failure(container, scenario)
    await set_story_test_status(container, scenario.story.id, StoryTestStatus.IN_TEST)
    await sign_up_member(client, container, recording_mailer, scenario.project, ProjectRole.ADMIN)
    sign_off_url = f"/api/projects/{scenario.project.key}/stories/{scenario.story.jira_key}/test-status"

    blocked = await client.put(sign_off_url, json={"testStatus": "passed"})
    assert (await change_status(client, scenario.project.key, failure_id, "fixed")).status_code == 200
    still_blocked = await client.put(sign_off_url, json={"testStatus": "passed"})
    assert (await change_status(client, scenario.project.key, failure_id, "verified")).status_code == 200
    allowed = await client.put(sign_off_url, json={"testStatus": "passed"})

    assert blocked.status_code == 409
    assert blocked.json()["code"] == "STORY_SIGN_OFF_BLOCKED"
    assert still_blocked.status_code == 409
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["testStatus"] == "passed"

from httpx import AsyncClient

from app.container import Container
from app.shared.typing.enums import JobName, QueueName
from tests.api.runs.manual.manual_run_steps import record_case_status, seed_manual_run_project, start_manual_run_id
from tests.api.runs.run_steps import (
    record_case,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue


def build_recompute_job(test_case_id: object) -> RecordedJob:
    return RecordedJob(
        queue_name=QueueName.MAINTENANCE,
        job_name=JobName.TEST_CASES_RECOMPUTE_FLAKY,
        data={"testCaseId": str(test_case_id)},
        job_id=None,
    )


async def test_a_claude_result_requests_a_flaky_recompute_for_its_case(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    recording_job_queue.jobs.clear()

    await record_case_id(client, runner.token, run_id, story.case_ids[0], "failed")
    await record_case_id(client, runner.token, run_id, story.case_ids[1], "passed")

    assert recording_job_queue.jobs == [
        build_recompute_job(story.case_ids[0]),
        build_recompute_job(story.case_ids[1]),
    ]


async def test_a_refused_result_requests_no_recompute(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed")
    recording_job_queue.jobs.clear()

    response = await record_case(client, runner.token, run_id, story.case_ids[0], "failed")

    assert response.json()["result"]["isError"] is True
    assert recording_job_queue.jobs == []


async def test_a_manual_result_requests_a_flaky_recompute_for_its_case(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    recording_job_queue.jobs.clear()

    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "passed")

    assert recording_job_queue.jobs == [build_recompute_job(seeded.cases[0].id)]

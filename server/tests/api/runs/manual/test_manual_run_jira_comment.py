from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.projects import JiraPostResults
from app.modules.projects.infrastructure import ProjectTable
from app.shared.typing.enums import JobName
from tests.api.runs.manual.manual_run_steps import (
    finish_manual_run,
    record_case_status,
    seed_manual_run_project,
    start_manual_run_id,
)
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue


async def test_finishing_a_manual_run_queues_the_story_comment_when_every_run_is_chosen(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable)
            .where(ProjectTable.id == seeded.project.id)
            .values(jira_post_results=JiraPostResults.EVERY_RUN)
        )
    run_id = await start_manual_run_id(client, seeded)
    for case in seeded.cases:
        await record_case_status(client, seeded.key, run_id, case.id, "passed")

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 200, response.text
    jobs = [job for job in recording_job_queue.jobs if job.job_name is JobName.JIRA_POST_COMMENT]
    assert [job.data for job in jobs] == [
        {
            "trigger": "run_finished",
            "projectId": str(seeded.project.id),
            "storyId": str(seeded.story_id),
            "runId": run_id,
        }
    ]


async def test_finishing_a_manual_run_with_no_results_queues_no_comment(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable)
            .where(ProjectTable.id == seeded.project.id)
            .values(jira_post_results=JiraPostResults.EVERY_RUN)
        )
    run_id = await start_manual_run_id(client, seeded)

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "aborted"
    assert [job for job in recording_job_queue.jobs if job.job_name is JobName.JIRA_POST_COMMENT] == []

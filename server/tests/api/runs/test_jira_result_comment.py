from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.jira import JiraDocumentBlockKind, JiraUnreachableError, JiraWriteNotAllowedError
from app.modules.projects import JiraPostResults
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs import PostJiraResultCommentJobHandler, RunStatus
from app.modules.runs.infrastructure import RunTable
from app.modules.stories import StorySource
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import StoryTable
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.failures.failure_steps import set_story_test_status
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.stories.story_steps import seed_jira_connection
from tests.api.test_data.project_steps import SeededProject, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.mcp_steps import read_tool_json
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue


def get_fake_jira_client(container: Container) -> FakeJiraClient:
    jira_client = container.jira_client
    assert isinstance(jira_client, FakeJiraClient)
    return jira_client


async def set_post_results(container: Container, project: SeededProject, setting: JiraPostResults) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(jira_post_results=setting)
        )


async def run_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    setting: JiraPostResults,
    statuses: tuple[str, ...] = ("passed", "failed"),
) -> tuple[Runner, SeededRunnableStory, str]:
    project = await seed_project(container)
    await set_post_results(container, project, setting)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    await seed_jira_connection(container, runner.account.user_id)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=len(statuses))
    run_id = await start_run_id(client, runner.token, story.jira_key)
    for case_id, status in zip(story.case_ids, statuses, strict=True):
        await record_case_id(client, runner.token, run_id, case_id, status)
    return runner, story, run_id


def list_comment_jobs(recording_job_queue: RecordingJobQueue) -> list[RecordedJob]:
    return [job for job in recording_job_queue.jobs if job.job_name is JobName.JIRA_POST_COMMENT]


def list_comment_lines(fake_jira: FakeJiraClient) -> list[str]:
    return [text for comment in fake_jira.comments for block in comment.body for text in block.texts]


async def test_every_run_posts_the_counts_on_the_story_after_the_run_finishes(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, story, run_id = await run_story(client, container, recording_mailer, JiraPostResults.EVERY_RUN)

    finished = await finish(client, runner.token, run_id)

    assert finished.status_code == 200, finished.text
    jobs = list_comment_jobs(recording_job_queue)
    assert [(job.queue_name, job.data, job.job_id) for job in jobs] == [
        (
            QueueName.JIRA,
            {
                "trigger": "run_finished",
                "projectId": str(story.project.id),
                "storyId": str(story.story_id),
                "runId": run_id,
            },
            f"jira-comment:{run_id}:{story.story_id}",
        )
    ]
    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle(jobs[0].data)
    fake_jira = get_fake_jira_client(container)
    assert [comment.issue_key for comment in fake_jira.comments] == [story.jira_key]
    lines = list_comment_lines(fake_jira)
    assert lines[0] == "Tessio: a test run finished (failed)."
    assert "Passed: 1 of 2" in lines
    assert "Failed: 1" in lines
    assert "Environment: Staging" in lines
    link = fake_jira.comments[0].body[-1]
    assert link.kind is JiraDocumentBlockKind.LINK
    assert link.link_url is not None
    assert link.link_url.endswith(f"/projects/{story.project.key}/runs/{run_id}")


@pytest.mark.parametrize("setting", [JiraPostResults.OFF, JiraPostResults.ON_SIGN_OFF])
async def test_no_comment_is_queued_after_a_run_unless_every_run_is_chosen(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    setting: JiraPostResults,
) -> None:
    runner, _, run_id = await run_story(client, container, recording_mailer, setting)

    assert (await finish(client, runner.token, run_id)).status_code == 200

    assert list_comment_jobs(recording_job_queue) == []


async def test_a_run_finished_with_no_results_queues_no_comment(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    project = await seed_project(container)
    await set_post_results(container, project, JiraPostResults.EVERY_RUN)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    await seed_jira_connection(container, runner.account.user_id)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)

    finished = await finish(client, runner.token, run_id)

    assert finished.status_code == 200, finished.text
    assert read_tool_json(finished)["status"] == "aborted"
    assert list_comment_jobs(recording_job_queue) == []


async def test_a_comment_job_for_an_aborted_run_posts_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, _, run_id = await run_story(client, container, recording_mailer, JiraPostResults.EVERY_RUN)
    assert (await finish(client, runner.token, run_id)).status_code == 200
    await set_run_status(container, UUID(run_id), RunStatus.ABORTED)

    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle(
        list_comment_jobs(recording_job_queue)[0].data
    )

    assert get_fake_jira_client(container).comments == []


async def test_sign_off_posts_the_latest_run_counts_on_the_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, story, run_id = await run_story(
        client, container, recording_mailer, JiraPostResults.ON_SIGN_OFF, ("passed", "passed")
    )
    assert (await finish(client, runner.token, run_id)).status_code == 200
    await set_story_test_status(container, story.story_id, StoryTestStatus.IN_TEST)
    await sign_up_member(client, container, recording_mailer, story.project, ProjectRole.QC)

    signed_off = await client.put(
        f"/api/projects/{story.project.key}/stories/{story.jira_key}/test-status", json={"testStatus": "passed"}
    )

    assert signed_off.status_code == 200, signed_off.text
    jobs = list_comment_jobs(recording_job_queue)
    assert [(job.data, job.job_id) for job in jobs] == [
        (
            {"trigger": "sign_off", "projectId": str(story.project.id), "storyId": str(story.story_id), "runId": None},
            None,
        )
    ]
    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle(jobs[0].data)
    lines = list_comment_lines(get_fake_jira_client(container))
    assert lines[0] == f"Tessio: {story.jira_key} was signed off."
    assert "Passed: 2 of 2" in lines
    link_url = get_fake_jira_client(container).comments[0].body[-1].link_url
    assert link_url is not None
    assert link_url.endswith(f"/projects/{story.project.key}/stories/{story.jira_key}")


async def test_sign_off_skips_a_later_run_that_was_aborted(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, story, run_id = await run_story(
        client, container, recording_mailer, JiraPostResults.ON_SIGN_OFF, ("passed", "passed")
    )
    assert (await finish(client, runner.token, run_id)).status_code == 200
    aborted_run_id = await start_run_id(client, runner.token, story.jira_key)
    aborted = await finish(client, runner.token, aborted_run_id)
    assert read_tool_json(aborted)["status"] == "aborted"
    await set_story_test_status(container, story.story_id, StoryTestStatus.IN_TEST)
    await sign_up_member(client, container, recording_mailer, story.project, ProjectRole.QC)

    signed_off = await client.put(
        f"/api/projects/{story.project.key}/stories/{story.jira_key}/test-status", json={"testStatus": "passed"}
    )

    assert signed_off.status_code == 200, signed_off.text
    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle(
        list_comment_jobs(recording_job_queue)[0].data
    )
    lines = list_comment_lines(get_fake_jira_client(container))
    assert "Passed: 2 of 2" in lines
    link_url = get_fake_jira_client(container).comments[0].body[-1].link_url
    assert link_url is not None
    assert link_url.endswith(f"/projects/{story.project.key}/stories/{story.jira_key}")


async def test_a_story_written_in_tessio_gets_no_comment(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, story, run_id = await run_story(client, container, recording_mailer, JiraPostResults.EVERY_RUN)
    assert (await finish(client, runner.token, run_id)).status_code == 200
    await mark_written_in_tessio(container, story.story_id)

    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle(
        list_comment_jobs(recording_job_queue)[0].data
    )

    assert get_fake_jira_client(container).comments == []


async def test_a_refused_comment_is_dropped_and_an_unreachable_jira_is_retried(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    runner, _, run_id = await run_story(client, container, recording_mailer, JiraPostResults.EVERY_RUN)
    assert (await finish(client, runner.token, run_id)).status_code == 200
    job_data = list_comment_jobs(recording_job_queue)[0].data
    fake_jira = get_fake_jira_client(container)
    handler = PostJiraResultCommentJobHandler(container.post_jira_result_comment)
    fake_jira.comment_errors.extend([JiraWriteNotAllowedError(), JiraUnreachableError()])

    await handler.handle(job_data)
    with pytest.raises(JiraUnreachableError):
        await handler.handle(job_data)
    await handler.handle(job_data)

    assert len(fake_jira.comments) == 1


async def test_invalid_comment_job_data_is_ignored(container: Container) -> None:
    await PostJiraResultCommentJobHandler(container.post_jira_result_comment).handle({"trigger": "sign_off"})

    assert get_fake_jira_client(container).comments == []


async def set_run_status(container: Container, run_id: UUID, status: RunStatus) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunTable).where(RunTable.id == run_id).values(status=status)
        )


async def mark_written_in_tessio(container: Container, story_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable).where(StoryTable.id == story_id).values(source=StorySource.TESSIO)
        )

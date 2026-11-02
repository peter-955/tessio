from datetime import UTC, datetime

from httpx import AsyncClient

from app.container import Container
from app.modules.files import StoredFileStatus
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.notifications.notification_steps import remove_member
from tests.api.plans.plan_steps import create_plan_id, set_plan_items, story_item
from tests.api.projects.user_steps import use_session
from tests.api.reports.recording_pdf_renderer import FAKE_PDF_PREFIX
from tests.api.reports.report_steps import (
    FAILED_ACTUAL_RESULT,
    RUN_SUMMARY,
    SECRET_VALUE,
    deactivate_user,
    find_export_job,
    find_stored_file,
    read_single_file,
    request_export,
    run_export_job,
    seed_export_world,
)
from tests.api.test_data.project_steps import add_member, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_run_export_is_queued_with_a_pending_report_file(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    world = await seed_export_world(client, container, recording_mailer)

    response = await request_export(client, world.project.key, f"runs/{world.run_id}", "md")

    assert response.status_code == 202, response.text
    body = response.json()
    assert body["format"] == "md"
    assert body["source"] == "run"
    assert body["sourceId"] == world.run_id
    assert body["sourceLabel"].startswith(world.story.jira_key)
    assert body["fileName"] == f"run-{world.story.jira_key}-{datetime.now(UTC):%Y-%m-%d}.md"
    job = find_export_job(recording_job_queue, body["fileId"])
    assert (job.queue_name, job.job_name) == (QueueName.REPORTS, JobName.REPORT_EXPORT)
    assert job.data["requesterId"] == str(world.runner.account.user_id)
    stored_file = await find_stored_file(container, body["fileId"])
    assert stored_file.kind == "report"
    assert stored_file.status == StoredFileStatus.PENDING
    pending_link = await client.get(f"/api/projects/{world.project.key}/files/{body['fileId']}")
    assert pending_link.status_code == 404


async def test_the_markdown_export_holds_the_report_with_secrets_masked(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    file_id = (await request_export(client, world.project.key, f"runs/{world.run_id}", "md")).json()["fileId"]

    await run_export_job(container, find_export_job(recording_job_queue, file_id))

    key, content, content_type = read_single_file(world.writer)
    markdown = content.decode()
    assert key.endswith(".md")
    assert content_type.startswith("text/markdown")
    assert markdown.startswith(f"# Run report · {world.story.jira_key}")
    assert "## Failed and blocked cases" in markdown
    assert "## Cases" in markdown
    assert "| TC-" in markdown
    assert SECRET_VALUE not in markdown
    assert FAILED_ACTUAL_RESULT.replace(SECRET_VALUE, MASKED_VALUE) in markdown
    assert RUN_SUMMARY.replace(SECRET_VALUE, MASKED_VALUE) in markdown
    assert r"\<b\>500\</b\> \| boom" in markdown
    stored_file = await find_stored_file(container, file_id)
    assert stored_file.status == StoredFileStatus.UPLOADED
    assert stored_file.size == len(content)
    assert stored_file.sha256 is not None
    download = await client.get(f"/api/projects/{world.project.key}/files/{file_id}")
    assert download.status_code == 200, download.text
    notifications = (await client.get("/api/notifications")).json()["items"]
    report_ready = [item for item in notifications if item["kind"] == "report_ready"]
    assert len(report_ready) == 1
    assert report_ready[0]["payload"]["fileId"] == file_id
    assert report_ready[0]["payload"]["source"] == "run"
    assert report_ready[0]["payload"]["sourceId"] == world.run_id
    assert any(
        event.type is LiveEventType.REPORT_READY
        and event.user_id == world.runner.account.user_id
        and event.ids == {"fileId": file_id, "format": "md"}
        for event in recording_live_event_publisher.events
    )


async def test_the_pdf_export_renders_masked_and_escaped_html(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    file_id = (await request_export(client, world.project.key, f"runs/{world.run_id}", "pdf")).json()["fileId"]

    await run_export_job(container, find_export_job(recording_job_queue, file_id))

    key, content, content_type = read_single_file(world.writer)
    assert key.endswith(".pdf")
    assert content_type == "application/pdf"
    assert content.startswith(b"%PDF")
    assert content.startswith(FAKE_PDF_PREFIX)
    (html,) = world.pdf_renderer.html_pages
    assert SECRET_VALUE not in html
    assert MASKED_VALUE in html
    assert "&lt;b&gt;500&lt;/b&gt;" in html
    assert "<b>500</b>" not in html


async def test_a_story_and_a_plan_can_be_exported(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    plan_id = await create_plan_id(client, world.project.key, "Release 3.0")
    assert (await set_plan_items(client, world.project.key, plan_id, [story_item(world.story)])).status_code == 200

    story_response = await request_export(client, world.project.key, f"stories/{world.story.jira_key}", "md")
    plan_response = await request_export(client, world.project.key, f"plans/{plan_id}", "md")

    assert story_response.status_code == 202, story_response.text
    assert plan_response.status_code == 202, plan_response.text
    assert story_response.json()["fileName"] == f"story-{world.story.jira_key}.md"
    assert plan_response.json()["fileName"] == "plan-Release-3.0.md"
    await run_export_job(container, find_export_job(recording_job_queue, story_response.json()["fileId"]))
    await run_export_job(container, find_export_job(recording_job_queue, plan_response.json()["fileId"]))
    documents = {key.rsplit("/", 1)[-1]: content.decode() for key, (content, _) in world.writer.files.items()}
    story_markdown = documents[f"story-{world.story.jira_key}.md"]
    plan_markdown = documents["plan-Release-3.0.md"]
    assert story_markdown.startswith(f"# Story report · {world.story.jira_key}")
    assert "## Acceptance criteria" in story_markdown
    assert "## Runs" in story_markdown
    assert plan_markdown.startswith("# Test plan report · Release 3.0")
    assert "## Progress" in plan_markdown
    assert "## Scope" in plan_markdown
    assert SECRET_VALUE not in story_markdown + plan_markdown


async def test_exports_are_refused_for_unknown_sources_and_formats(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    other_project = await seed_project(container)
    queued_before = len(recording_job_queue.jobs)

    unknown_run = await request_export(client, world.project.key, "runs/0190f3b6-0000-7000-8000-000000000000", "md")
    unknown_story = await request_export(client, world.project.key, "stories/NOPE-1", "md")
    other_project_run = await request_export(client, other_project.key, f"runs/{world.run_id}", "md")
    bad_format = await request_export(client, world.project.key, f"runs/{world.run_id}", "docx")

    assert (unknown_run.status_code, unknown_run.json()["code"]) == (404, "NOT_FOUND")
    assert (unknown_story.status_code, unknown_story.json()["code"]) == (404, "NOT_FOUND")
    assert (other_project_run.status_code, other_project_run.json()["code"]) == (404, "NOT_FOUND")
    assert bad_format.status_code == 422
    assert len(recording_job_queue.jobs) == queued_before


async def test_a_member_of_two_projects_cannot_export_one_project_source_through_the_other(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    first_world = await seed_export_world(client, container, recording_mailer)
    second_world = await seed_export_world(client, container, recording_mailer)
    second_plan_id = await create_plan_id(client, second_world.project.key, "Release 4.0")
    await add_member(container, second_world.project, first_world.runner.account.user_id, ProjectRole.QC)
    use_session(client, first_world.runner.account.session_token)
    queued_before = len(recording_job_queue.jobs)

    foreign_run = await request_export(client, first_world.project.key, f"runs/{second_world.run_id}", "md")
    foreign_plan = await request_export(client, first_world.project.key, f"plans/{second_plan_id}", "md")
    foreign_story = await request_export(
        client, first_world.project.key, f"stories/{second_world.story.jira_key}", "md"
    )

    assert (foreign_run.status_code, foreign_run.json()["code"]) == (404, "NOT_FOUND")
    assert (foreign_plan.status_code, foreign_plan.json()["code"]) == (404, "NOT_FOUND")
    assert (foreign_story.status_code, foreign_story.json()["code"]) == (404, "NOT_FOUND")
    assert len(recording_job_queue.jobs) == queued_before
    own_project_run = await request_export(client, second_world.project.key, f"runs/{second_world.run_id}", "md")
    assert own_project_run.status_code == 202, own_project_run.text


async def test_a_viewer_can_export_a_report(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    await sign_up_member(client, container, recording_mailer, world.project, ProjectRole.VIEWER)

    response = await request_export(client, world.project.key, f"runs/{world.run_id}", "pdf")

    assert response.status_code == 202, response.text


async def test_the_job_writes_nothing_when_the_requester_lost_access(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, recording_job_queue: RecordingJobQueue
) -> None:
    world = await seed_export_world(client, container, recording_mailer)
    removed_file = (await request_export(client, world.project.key, f"runs/{world.run_id}", "md")).json()["fileId"]
    deactivated_file = (await request_export(client, world.project.key, f"runs/{world.run_id}", "md")).json()["fileId"]
    await remove_member(container, world.project, world.runner.account.user_id)

    await run_export_job(container, find_export_job(recording_job_queue, removed_file))
    await deactivate_user(container, world.runner.account.user_id)
    await run_export_job(container, find_export_job(recording_job_queue, deactivated_file))
    await container.job_handlers[QueueName.REPORTS][JobName.REPORT_EXPORT].handle({"fileId": "not-a-uuid"})

    assert world.writer.files == {}
    assert (await find_stored_file(container, removed_file)).status == StoredFileStatus.PENDING
    assert (await find_stored_file(container, deactivated_file)).status == StoredFileStatus.PENDING

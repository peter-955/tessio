from dataclasses import dataclass
from uuid import UUID

from httpx import AsyncClient, Response
from sqlalchemy import select, update

from app.container import Container
from app.modules.files.infrastructure import StoredFileTable
from app.modules.users.infrastructure import UserTable
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.projects.user_steps import use_session
from tests.api.reports.in_memory_report_file_writer import InMemoryReportFileWriter
from tests.api.reports.recording_pdf_renderer import RecordingPdfRenderer
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
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue

SECRET_VALUE = "hunter2-secret"
FAILED_ACTUAL_RESULT = f"Card {SECRET_VALUE} was refused"
FAILED_ERROR = "<b>500</b> | boom"
RUN_SUMMARY = f"Checkout broke with {SECRET_VALUE}"


@dataclass(frozen=True)
class ExportWorld:
    project: SeededProject
    runner: Runner
    story: SeededRunnableStory
    run_id: str
    writer: InMemoryReportFileWriter
    pdf_renderer: RecordingPdfRenderer


async def seed_export_world(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
) -> ExportWorld:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.QC)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    await record_case(client, runner.token, run_id, story.case_ids[0], "passed")
    await record_case(
        client,
        runner.token,
        run_id,
        story.case_ids[1],
        "failed",
        [{"order": 1, "status": "failed", "actual_result": FAILED_ACTUAL_RESULT, "error": FAILED_ERROR}],
    )
    finished = await finish(client, runner.token, run_id, RUN_SUMMARY)
    assert finished.status_code == 200, finished.text
    await seed_secret(container, project, "CARD_TOKEN", SECRET_VALUE)
    writer = InMemoryReportFileWriter()
    pdf_renderer = RecordingPdfRenderer()
    container.__dict__["report_file_writer"] = writer
    container.__dict__["pdf_renderer"] = pdf_renderer
    use_session(client, runner.account.session_token)
    return ExportWorld(
        project=project, runner=runner, story=story, run_id=run_id, writer=writer, pdf_renderer=pdf_renderer
    )


def export_path(project_key: str, source_path: str) -> str:
    return f"/api/projects/{project_key}/{source_path}/export"


async def request_export(client: AsyncClient, project_key: str, source_path: str, report_format: str) -> Response:
    return await client.post(export_path(project_key, source_path), json={"format": report_format})


def find_export_job(recording_job_queue: RecordingJobQueue, file_id: str) -> RecordedJob:
    jobs = [job for job in recording_job_queue.jobs if job.job_id == file_id]
    assert len(jobs) == 1
    return jobs[0]


async def run_export_job(container: Container, job: RecordedJob) -> None:
    await container.job_handlers[QueueName.REPORTS][JobName.REPORT_EXPORT].handle(job.data)


async def find_stored_file(container: Container, file_id: str) -> StoredFileTable:
    async with container.database.begin():
        row = await container.database.get_current_session().scalar(
            select(StoredFileTable).where(StoredFileTable.id == UUID(file_id))
        )
    assert row is not None
    return row


async def deactivate_user(container: Container, user_id: UUID) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(UserTable).where(UserTable.id == user_id).values(status="deactivated")
        )


def read_single_file(writer: InMemoryReportFileWriter) -> tuple[str, bytes, str]:
    assert len(writer.files) == 1
    ((key, (content, content_type)),) = writer.files.items()
    return key, content, content_type

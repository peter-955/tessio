from dataclasses import dataclass
from pathlib import Path

from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import Runner, SeededRunnableStory, seed_runnable_story, sign_up_runner
from tests.api.test_data.project_steps import SeededProject, seed_project
from tests.conftest import RecordingMailer

JUNIT_FIXTURES = Path(__file__).resolve().parents[3] / "fixtures" / "junit"


@dataclass(frozen=True)
class ImportWorld:
    project: SeededProject
    runner: Runner
    story: SeededRunnableStory


async def seed_import_world(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    case_count: int = 4,
    role: ProjectRole = ProjectRole.QC,
) -> ImportWorld:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, role)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count, 2)
    use_session(client, runner.account.session_token)
    return ImportWorld(project=project, runner=runner, story=story)


def read_fixture(name: str) -> bytes:
    return (JUNIT_FIXTURES / name).read_bytes()


async def import_junit(
    client: AsyncClient,
    project_key: str,
    content: bytes,
    environment: str = "Staging",
    suite: str | None = None,
    headers: dict[str, str] | None = None,
) -> Response:
    form = {"environment": environment} if suite is None else {"environment": environment, "suite": suite}
    return await client.post(
        f"/api/projects/{project_key}/runs/import",
        data=form,
        files={"file": ("results.xml", content, "application/xml")},
        headers=headers,
    )

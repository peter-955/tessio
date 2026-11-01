import asyncio
from datetime import UTC, datetime
from uuid import uuid7

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.runs import Run, RunExecutor, RunStatus
from app.modules.runs.errors import RunAlreadyRunningError
from tests.api.runs.manual.manual_run_steps import ManualRunProject, seed_manual_run_project, start_manual_run
from tests.conftest import RecordingMailer


def build_running_run(seeded: ManualRunProject) -> Run:
    now = datetime.now(UTC)
    return Run(
        id=uuid7(),
        project_id=seeded.project.id,
        story_id=seeded.story_id,
        environment_id=seeded.environment_id,
        executor=RunExecutor.MANUAL,
        status=RunStatus.RUNNING,
        abort_reason=None,
        parent_run_id=None,
        started_by=seeded.qc.user_id,
        started_via_token_id=None,
        summary=None,
        report=None,
        started_at=now,
        last_activity_at=now,
        finished_at=None,
        created_at=now,
    )


async def test_concurrent_starts_for_one_story_open_one_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    responses = await asyncio.gather(start_manual_run(client, seeded), start_manual_run(client, seeded))

    assert sorted(response.status_code for response in responses) == [201, 409]
    refused = next(response for response in responses if response.status_code == 409)
    assert refused.json()["code"] == "RUN_ALREADY_RUNNING"


async def test_a_second_running_run_that_reaches_the_database_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    async with container.database.begin():
        await container.run_repository.add(build_running_run(seeded))

    with pytest.raises(RunAlreadyRunningError):
        async with container.database.begin():
            await container.run_repository.add(build_running_run(seeded))

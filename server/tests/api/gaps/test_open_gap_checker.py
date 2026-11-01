import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.gaps import OpenGapsBlockRunError
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import answer_gap, raise_gap_id, seed_story
from tests.api.test_data.project_steps import seed_project, sign_up_member
from tests.conftest import RecordingMailer


async def test_checker_counts_only_open_gaps_of_the_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    other_story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await raise_gap_id(client, project.key, story)
    await raise_gap_id(client, project.key, story)
    resolved_id = await raise_gap_id(client, project.key, story)
    await raise_gap_id(client, project.key, other_story)
    assert (await answer_gap(client, project.key, resolved_id)).status_code == 200

    count = await container.open_gap_checker.count_open_gaps(story.id)

    assert count == 2


async def test_open_gaps_block_runs(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await raise_gap_id(client, project.key, story)
    await raise_gap_id(client, project.key, story)

    with pytest.raises(OpenGapsBlockRunError) as raised:
        await container.open_gap_checker.ensure_no_open_gaps(story.id)

    assert raised.value.code == "OPEN_GAPS_BLOCK_RUN"
    assert raised.value.message == "2 open gaps block runs on this story."


async def test_resolved_gaps_do_not_block_runs(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    gap_id = await raise_gap_id(client, project.key, story)
    assert (await answer_gap(client, project.key, gap_id)).status_code == 200

    await container.open_gap_checker.ensure_no_open_gaps(story.id)

    assert await container.open_gap_checker.count_open_gaps(story.id) == 0


async def test_checker_joins_the_callers_transaction(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    story = await seed_story(container, project)
    await sign_up_member(client, container, recording_mailer, project, ProjectRole.QC)
    await raise_gap_id(client, project.key, story)

    async with container.database.begin():
        count = await container.open_gap_checker.count_open_gaps(story.id)

    assert count == 1

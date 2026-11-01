from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.container import Container
from app.modules.failures import FailureStatus
from app.modules.failures.infrastructure import FailureTable
from app.modules.runs import RunReport, RunStatus
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.manual.manual_run_steps import build_step, find_run_row, finish_manual_run, record_case
from tests.api.runs.run_steps import build_steps, finish, record_case_id, start_run_id
from tests.api.story_context.story_context_steps import (
    ContextProject,
    ReadyCase,
    TokenHolder,
    add_token_holder,
    create_ready_case,
    find_ready_case,
    set_up_context_project,
)
from tests.api.test_cases.case_steps import build_step as build_case_step
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json


@dataclass(frozen=True)
class WiredStory:
    context_project: ContextProject
    holder: TokenHolder
    failing_case: ReadyCase
    passing_case: ReadyCase


RunPath = Callable[[AsyncClient, WiredStory], Awaitable[UUID]]


async def set_up_wired_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> WiredStory:
    context_project = await set_up_context_project(client, container, recording_mailer)
    first_criterion_id, second_criterion_id, _ = context_project.story.criterion_ids
    steps = [build_case_step("Open the checkout", "The checkout opens")]
    failing_case = await create_ready_case(
        client, container, context_project, steps, criterionIds=[str(first_criterion_id)]
    )
    passing_case = await create_ready_case(
        client, container, context_project, steps, criterionIds=[str(second_criterion_id)]
    )
    ready_failing_case = await find_ready_case(client, context_project, failing_case.code)
    ready_passing_case = await find_ready_case(client, context_project, passing_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    return WiredStory(
        context_project=context_project,
        holder=holder,
        failing_case=ready_failing_case,
        passing_case=ready_passing_case,
    )


async def run_over_mcp(client: AsyncClient, wired_story: WiredStory) -> UUID:
    token = wired_story.holder.token
    run_id = await start_run_id(client, token, wired_story.context_project.story.jira_key)
    await record_case_id(client, token, run_id, wired_story.failing_case.id, "failed", build_steps(["failed"]))
    await record_case_id(client, token, run_id, wired_story.passing_case.id, "passed")
    finished = read_tool_json(await finish(client, token, run_id))
    assert finished["status"] == RunStatus.FAILED.value
    return UUID(run_id)


async def run_over_rest(client: AsyncClient, wired_story: WiredStory) -> UUID:
    use_session(client, wired_story.holder.account.session_token)
    project_key = wired_story.context_project.key
    started = await client.post(
        f"/api/projects/{project_key}/runs", json={"storyKey": wired_story.context_project.story.jira_key}
    )
    assert started.status_code == 201, started.text
    run_id: str = started.json()["id"]
    for case, status in ((wired_story.failing_case, "failed"), (wired_story.passing_case, "passed")):
        recorded = await record_case(client, project_key, run_id, case.id, steps=[build_step(1, status)])
        assert recorded.status_code == 200, recorded.text
    finished = await finish_manual_run(client, project_key, run_id)
    assert finished.status_code == 200, finished.text
    return UUID(run_id)


async def list_project_failures(container: Container, project_id: UUID) -> list[FailureTable]:
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(FailureTable).where(FailureTable.project_id == project_id)
        )
        return list(rows)


@pytest.mark.parametrize("run_path", [run_over_mcp, run_over_rest], ids=["mcp", "rest"])
async def test_a_failed_case_opens_a_failure_and_the_report_lists_criterion_impacts(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, run_path: RunPath
) -> None:
    wired_story = await set_up_wired_story(client, container, recording_mailer)

    run_id = await run_path(client, wired_story)

    failures = await list_project_failures(container, wired_story.context_project.project.id)
    assert [(failure.test_case_id, failure.status) for failure in failures] == [
        (wired_story.failing_case.id, FailureStatus.OPEN)
    ]
    run_row = await find_run_row(container, run_id)
    assert run_row.status == RunStatus.FAILED
    report = RunReport.model_validate(run_row.report)
    impacts_by_code = {impact.code: impact for impact in report.criterion_impacts}
    assert set(impacts_by_code) == {"AC1", "AC2", "AC3"}
    assert impacts_by_code["AC1"].run_case_codes == [wired_story.failing_case.code]
    assert impacts_by_code["AC1"].failed_case_codes == [wired_story.failing_case.code]
    assert impacts_by_code["AC2"].run_case_codes == [wired_story.passing_case.code]
    assert impacts_by_code["AC2"].failed_case_codes == []
    assert impacts_by_code["AC3"].run_case_codes == []

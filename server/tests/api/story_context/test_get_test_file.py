from uuid import UUID

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.runs.typing.enums import RunStatus
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import read_tool_error
from tests.api.story_context.story_context_steps import (
    ContextProject,
    CreatedCase,
    TokenHolder,
    add_token_holder,
    attach_file,
    build_file_url,
    build_login_steps,
    count_run_files,
    create_ready_case,
    find_ready_case,
    find_run_files,
    seed_story_run,
    set_up_context_project,
)
from tests.api.test_cases.case_steps import build_step
from tests.api.test_data.project_steps import archive_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def set_up_file_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[ContextProject, CreatedCase]:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(client, container, context_project, build_login_steps(), ("invoice",))
    return context_project, created_case


async def test_get_test_file_returns_a_signed_link_and_records_it_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])
    arguments: dict[str, object] = {"run_id": str(run_id), "key": "invoice"}

    first = await call_tool(client, holder.token, "get_test_file", arguments)
    second = await call_tool(client, holder.token, "get_test_file", arguments)

    expected = {
        "file_name": "invoice.pdf",
        "url": build_file_url(context_project.project, created_case.file_ids["invoice"], "invoice.pdf"),
    }
    assert read_tool_json(first) == expected
    assert read_tool_json(second) == expected
    run_files = await find_run_files(container, run_id)
    assert len(run_files) == 1
    assert run_files[0].test_case_id == ready_case.id
    assert run_files[0].key == "invoice"
    assert run_files[0].requested_by == holder.user_id


async def test_get_test_file_keeps_the_file_version_fixed_by_the_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])
    await attach_file(client, container, context_project, created_case.code, "invoice", "invoice-v2.pdf")

    response = await call_tool(client, holder.token, "get_test_file", {"run_id": str(run_id), "key": " invoice "})

    assert read_tool_json(response) == {
        "file_name": "invoice.pdf",
        "url": build_file_url(context_project.project, created_case.file_ids["invoice"], "invoice.pdf"),
    }


async def test_get_test_file_refuses_unknown_and_ambiguous_keys(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, first_case = await set_up_file_case(client, container, recording_mailer)
    second_case = await create_ready_case(
        client, container, context_project, [build_step("Attach {{file.invoice}}")], ("invoice",)
    )
    first_ready_case = await find_ready_case(client, context_project, first_case.code)
    second_ready_case = await find_ready_case(client, context_project, second_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.DEV)
    run_id = await seed_story_run(container, context_project, holder.user_id, [first_ready_case, second_ready_case])

    unknown = await call_tool(client, holder.token, "get_test_file", {"run_id": str(run_id), "key": "contract"})
    ambiguous = await call_tool(client, holder.token, "get_test_file", {"run_id": str(run_id), "key": "invoice"})
    chosen = await call_tool(
        client,
        holder.token,
        "get_test_file",
        {"run_id": str(run_id), "key": "invoice", "case_id": str(second_ready_case.id)},
    )

    assert read_tool_error(unknown) == "NOT_FOUND: No test file with this key in this run."
    assert read_tool_error(ambiguous).startswith("INVALID_REQUEST: ")
    assert read_tool_json(chosen) == {
        "file_name": "invoice.pdf",
        "url": build_file_url(context_project.project, second_case.file_ids["invoice"], "invoice.pdf"),
    }
    run_files = await find_run_files(container, run_id)
    assert [run_file.test_case_id for run_file in run_files] == [second_ready_case.id]


async def assert_refused_without_run_files(
    client: AsyncClient, container: Container, holder: TokenHolder, run_id: UUID, expected_code: str
) -> None:
    response = await call_tool(client, holder.token, "get_test_file", {"run_id": str(run_id), "key": "invoice"})
    assert read_tool_error(response).startswith(f"{expected_code}: ")
    assert await count_run_files(container, run_id) == 0


async def test_get_test_file_refuses_a_run_started_by_someone_else(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, context_project.author.user_id, [ready_case])

    await assert_refused_without_run_files(client, container, holder, run_id, "RUN_NOT_OWNED")


async def test_get_test_file_refuses_a_finished_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case], RunStatus.ABORTED)

    await assert_refused_without_run_files(client, container, holder, run_id, "RUN_NOT_RUNNING")


@pytest.mark.parametrize("role", [ProjectRole.VIEWER, ProjectRole.PM, ProjectRole.BA])
async def test_get_test_file_is_refused_for_roles_that_cannot_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, role)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    await assert_refused_without_run_files(client, container, holder, run_id, "PERMISSION_DENIED")


async def test_get_test_file_is_refused_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, created_case = await set_up_file_case(client, container, recording_mailer)
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])
    await archive_project(container, context_project.project)

    await assert_refused_without_run_files(client, container, holder, run_id, "PROJECT_ARCHIVED")

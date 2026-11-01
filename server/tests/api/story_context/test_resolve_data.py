from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient
from pydantic import JsonValue

from app.container import Container
from app.modules.audit import AuditAction
from app.modules.runs.typing.enums import RunStatus
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import find_token
from tests.api.gaps.gap_steps import read_tool_error
from tests.api.story_context.story_context_steps import (
    API_KEY,
    PROJECT_PASSWORD,
    STAGING_PASSWORD,
    ContextProject,
    ReadyCase,
    TokenHolder,
    add_token_holder,
    build_login_steps,
    create_ready_case,
    find_audit_rows,
    find_ready_case,
    seed_environment,
    seed_run,
    seed_story_run,
    set_up_context_project,
)
from tests.api.test_cases.case_steps import build_step, seed_story
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json

REQUESTED_KEYS = ["user_password", "api_key", "user_email", "coupon", "user_password"]


def build_api_steps() -> list[JsonValue]:
    return [build_step("Call the orders API with {{data.api_key}}", "The orders are listed")]


async def set_up_ready_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[ContextProject, ReadyCase]:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(
        client, container, context_project, [*build_login_steps(), *build_api_steps()], ("invoice",)
    )
    return context_project, await find_ready_case(client, context_project, created_case.code)


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.ADMIN])
async def test_resolve_data_returns_secrets_of_the_run_environment_and_audits_each_key(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, role)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    response = await call_tool(client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": REQUESTED_KEYS})

    assert read_tool_json(response) == {
        "values": {"user_password": STAGING_PASSWORD, "api_key": API_KEY},
        "unknown_keys": ["user_email", "coupon"],
    }
    api_token = await find_token(container, holder.token)
    audit_rows = await find_audit_rows(container, run_id)
    assert [row.action for row in audit_rows] == [AuditAction.SECRET_RESOLVE, AuditAction.SECRET_RESOLVE]
    assert {row.target_id for row in audit_rows} == {
        context_project.data_item_ids["user_password@staging"],
        context_project.data_item_ids["api_key"],
    }
    assert all(row.api_token_id == api_token.id for row in audit_rows)
    assert all(row.actor_id == holder.user_id for row in audit_rows)
    assert all(row.project_id == context_project.project.id for row in audit_rows)


async def test_resolve_data_uses_the_project_value_without_an_environment_override(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_run(
        container,
        context_project.project,
        context_project.story.id,
        context_project.production_id,
        holder.user_id,
        [(ready_case.id, ready_case.version_id)],
    )

    response = await call_tool(client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": ["user_password"]})

    assert read_tool_json(response) == {"values": {"user_password": PROJECT_PASSWORD}}
    audit_rows = await find_audit_rows(container, run_id)
    assert [row.target_id for row in audit_rows] == [context_project.data_item_ids["user_password"]]


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV])
async def test_resolve_data_treats_secrets_no_run_case_uses_as_unknown_without_audit(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(client, container, context_project, build_login_steps(), ("invoice",))
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, role)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    response = await call_tool(
        client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": ["api_key", "user_password"]}
    )

    assert read_tool_json(response) == {"values": {"user_password": STAGING_PASSWORD}, "unknown_keys": ["api_key"]}
    audit_rows = await find_audit_rows(container, run_id)
    assert [row.target_id for row in audit_rows] == [context_project.data_item_ids["user_password@staging"]]


async def test_resolve_data_refuses_every_secret_when_no_run_case_uses_data(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(
        client, container, context_project, [build_step("Open the home page", "The home page opens")]
    )
    ready_case = await find_ready_case(client, context_project, created_case.code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.DEV)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    response = await call_tool(
        client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": ["api_key", "user_password"]}
    )

    assert read_tool_json(response) == {"unknown_keys": ["api_key", "user_password"]}
    assert await find_audit_rows(container, run_id) == []


async def test_resolve_data_allows_keys_used_by_any_case_of_the_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    login_case = await create_ready_case(client, container, context_project, build_login_steps(), ("invoice",))
    api_case = await create_ready_case(client, container, context_project, build_api_steps())
    ready_cases = [
        await find_ready_case(client, context_project, login_case.code),
        await find_ready_case(client, context_project, api_case.code),
    ]
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, ready_cases)

    response = await call_tool(
        client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": ["api_key", "user_password"]}
    )

    assert read_tool_json(response) == {"values": {"api_key": API_KEY, "user_password": STAGING_PASSWORD}}


async def assert_refused_without_audit(
    client: AsyncClient, container: Container, holder: TokenHolder, run_id: UUID, expected_code: str
) -> None:
    response = await call_tool(client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": REQUESTED_KEYS})
    assert read_tool_error(response).startswith(f"{expected_code}: ")
    assert await find_audit_rows(container, run_id) == []


async def test_resolve_data_refuses_a_run_started_by_someone_else(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, context_project.author.user_id, [ready_case])

    await assert_refused_without_audit(client, container, holder, run_id, "RUN_NOT_OWNED")


async def test_resolve_data_refuses_a_finished_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case], RunStatus.PASSED)

    await assert_refused_without_audit(client, container, holder, run_id, "RUN_NOT_RUNNING")


async def test_resolve_data_refuses_unknown_runs_and_runs_of_other_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, _ = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    other_project = await seed_project(container)
    other_story = await seed_story(container, other_project, f"{other_project.key}-3", ["Other rule"])
    other_environment_id = await seed_environment(container, other_project)
    foreign_run_id = await seed_run(container, other_project, other_story.id, other_environment_id, holder.user_id, [])

    await assert_refused_without_audit(client, container, holder, uuid7(), "NOT_FOUND")
    await assert_refused_without_audit(client, container, holder, foreign_run_id, "NOT_FOUND")


@pytest.mark.parametrize("role", [ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER])
async def test_resolve_data_is_refused_for_roles_without_secret_use(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, role)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    await assert_refused_without_audit(client, container, holder, run_id, "PERMISSION_DENIED")


async def test_resolve_data_is_refused_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])
    await archive_project(container, context_project.project)

    await assert_refused_without_audit(client, container, holder, run_id, "PROJECT_ARCHIVED")


async def test_resolve_data_refuses_more_than_fifty_keys(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_ready_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])
    keys = [f"key_{index}" for index in range(51)]

    response = await call_tool(client, holder.token, "resolve_data", {"run_id": str(run_id), "keys": keys})

    assert response.json()["result"]["isError"] is True
    assert await find_audit_rows(container, run_id) == []

from uuid import UUID

import pytest
from httpx import AsyncClient, Response

from app.container import Container
from app.modules.audit import AuditAction
from app.modules.runs.typing.enums import RunStatus
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.story_context.story_context_steps import (
    STAGING_PASSWORD,
    ContextProject,
    ReadyCase,
    TokenHolder,
    add_token_holder,
    build_login_steps,
    create_ready_case,
    find_audit_rows,
    find_ready_case,
    seed_story_run,
    set_up_context_project,
)
from tests.conftest import RecordingMailer


async def set_up_login_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[ContextProject, ReadyCase]:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(client, container, context_project, build_login_steps(), ("invoice",))
    return context_project, await find_ready_case(client, context_project, created_case.code)


async def post_resolve_data(
    client: AsyncClient, context_project: ContextProject, holder: TokenHolder, run_id: UUID, keys: list[str]
) -> Response:
    use_session(client, holder.account.session_token)
    return await client.post(f"/api/projects/{context_project.key}/runs/{run_id}/resolve-data", json={"keys": keys})


async def test_resolve_data_route_returns_the_secret_for_the_starter_and_audits_it(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_login_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    response = await post_resolve_data(client, context_project, holder, run_id, ["user_password", "coupon"])

    assert response.status_code == 200, response.text
    assert response.json() == {"values": {"user_password": STAGING_PASSWORD}, "unknownKeys": ["coupon"]}
    audit_rows = await find_audit_rows(container, run_id)
    assert [row.action for row in audit_rows] == [AuditAction.SECRET_RESOLVE]
    assert audit_rows[0].target_id == context_project.data_item_ids["user_password@staging"]
    assert audit_rows[0].actor_id == holder.user_id
    assert audit_rows[0].api_token_id is None


@pytest.mark.parametrize(
    ("run_status", "is_own_run", "expected_status", "expected_code"),
    [
        (RunStatus.RUNNING, False, 403, "RUN_NOT_OWNED"),
        (RunStatus.PASSED, True, 409, "RUN_NOT_RUNNING"),
    ],
)
async def test_resolve_data_route_refuses_other_runs_without_audit(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    run_status: RunStatus,
    is_own_run: bool,
    expected_status: int,
    expected_code: str,
) -> None:
    context_project, ready_case = await set_up_login_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    starter_id = holder.user_id if is_own_run else context_project.author.user_id
    run_id = await seed_story_run(container, context_project, starter_id, [ready_case], run_status)

    response = await post_resolve_data(client, context_project, holder, run_id, ["user_password"])

    assert response.status_code == expected_status, response.text
    assert response.json()["code"] == expected_code
    assert await find_audit_rows(container, run_id) == []


async def test_resolve_data_route_is_refused_for_a_viewer(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_login_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.VIEWER)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    response = await post_resolve_data(client, context_project, holder, run_id, ["user_password"])

    assert response.status_code == 403, response.text
    assert await find_audit_rows(container, run_id) == []


async def test_resolve_data_route_refuses_empty_and_too_many_keys(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_login_case(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    run_id = await seed_story_run(container, context_project, holder.user_id, [ready_case])

    empty = await post_resolve_data(client, context_project, holder, run_id, [])
    too_many = await post_resolve_data(client, context_project, holder, run_id, [f"key_{index}" for index in range(51)])

    assert empty.status_code == 422
    assert too_many.status_code == 422

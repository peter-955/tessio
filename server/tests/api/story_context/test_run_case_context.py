from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.stories.infrastructure import AcceptanceCriterionTable
from tests.api.projects.user_steps import use_session
from tests.api.story_context.story_context_steps import (
    PROJECT_EMAIL,
    STAGING_EMAIL,
    STAGING_PASSWORD,
    ContextProject,
    ReadyCase,
    build_login_steps,
    create_ready_case,
    find_ready_case,
    seed_run,
    seed_story_run,
    set_up_context_project,
)
from tests.api.test_cases.case_steps import build_step
from tests.conftest import RecordingMailer


async def set_up_described_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[ContextProject, ReadyCase]:
    context_project = await set_up_context_project(client, container, recording_mailer)
    criterion_ids = context_project.story.criterion_ids
    created_case = await create_ready_case(
        client,
        container,
        context_project,
        build_login_steps(),
        ("invoice",),
        businessValue="Shoppers pay without retyping their card",
        preconditions="Signed out as {{data.user_email}}",
        criterionIds=[str(criterion_ids[0]), str(criterion_ids[2])],
    )
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(AcceptanceCriterionTable)
            .where(AcceptanceCriterionTable.id == criterion_ids[2])
            .values(removed_at=datetime.now(UTC))
        )
    return context_project, await find_ready_case(client, context_project, created_case.code)


async def test_run_detail_returns_what_a_tester_needs_to_follow_each_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_described_case(client, container, recording_mailer)
    run_id = await seed_story_run(container, context_project, context_project.author.user_id, [ready_case])
    use_session(client, context_project.author.session_token)

    response = await client.get(f"/api/projects/{context_project.key}/runs/{run_id}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["environmentBaseUrl"] == "https://staging.shop.test"
    assert body["data"] == [
        {"key": "user_email", "kind": "variable", "value": STAGING_EMAIL},
        {"key": "user_password", "kind": "secret", "value": None},
    ]
    [run_case] = body["cases"]
    assert run_case["businessValue"] == "Shoppers pay without retyping their card"
    assert run_case["preconditions"] == "Signed out as {{data.user_email}}"
    assert run_case["criteria"] == [{"code": "AC1", "text": "Pay by card"}]
    assert run_case["files"] == [{"key": "invoice", "fileName": "invoice.pdf"}]
    assert STAGING_PASSWORD not in response.text


async def test_run_detail_data_falls_back_to_the_project_value_and_skips_unused_keys(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project, ready_case = await set_up_described_case(client, container, recording_mailer)
    run_id = await seed_run(
        container,
        context_project.project,
        context_project.story.id,
        context_project.production_id,
        context_project.author.user_id,
        [(ready_case.id, ready_case.version_id)],
    )
    use_session(client, context_project.author.session_token)

    response = await client.get(f"/api/projects/{context_project.key}/runs/{run_id}")

    assert response.json()["environmentBaseUrl"] == "https://shop.test"
    assert response.json()["data"] == [
        {"key": "user_email", "kind": "variable", "value": PROJECT_EMAIL},
        {"key": "user_password", "kind": "secret", "value": None},
    ]


async def test_run_detail_has_no_data_when_no_case_uses_any(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(
        client, container, context_project, [build_step("Open the home page", "The home page opens")]
    )
    ready_case = await find_ready_case(client, context_project, created_case.code)
    run_id = await seed_story_run(container, context_project, context_project.author.user_id, [ready_case])
    use_session(client, context_project.author.session_token)

    response = await client.get(f"/api/projects/{context_project.key}/runs/{run_id}")

    body = response.json()
    assert body["data"] == []
    assert body["cases"][0]["businessValue"] is None
    assert body["cases"][0]["preconditions"] is None
    assert body["cases"][0]["criteria"] == []
    assert body["cases"][0]["files"] == []

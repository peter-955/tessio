import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import read_tool_error
from tests.api.story_context.story_context_steps import (
    PROJECT_EMAIL,
    PROJECT_PASSWORD,
    STAGING_EMAIL,
    STAGING_PASSWORD,
    ContextProject,
    add_token_holder,
    build_login_steps,
    create_ready_case,
    delete_data_item,
    find_ready_case,
    set_up_context_project,
)
from tests.api.test_cases.case_steps import (
    build_step,
    change_status,
    create_case_code,
    remove_criterion,
    seed_story,
    update_case,
)
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def set_up_story_cases(client: AsyncClient, container: Container, context_project: ContextProject) -> str:
    first_criterion_id, _, removed_criterion_id = context_project.story.criterion_ids
    created_case = await create_ready_case(
        client,
        container,
        context_project,
        build_login_steps(),
        ("invoice",),
        priority="high",
        preconditions="The cart holds {{data.coupon}}",
        criterionIds=[str(first_criterion_id), str(removed_criterion_id)],
    )
    code = created_case.code
    ready_case = await find_ready_case(client, context_project, code)
    edited = await update_case(
        client, context_project.key, code, ready_case.version_number, title="Pay by card and get the invoice"
    )
    assert edited.status_code == 200, edited.text
    story_key = context_project.story.jira_key
    await create_case_code(client, context_project.key, story_key, title="Draft case")
    in_review_code = await create_case_code(
        client, context_project.key, story_key, title="Review case", steps=[build_step("Open the cart")]
    )
    await change_status(client, context_project.key, in_review_code, "in_review")
    deprecated_code = await create_case_code(client, context_project.key, story_key, title="Old case")
    await change_status(client, context_project.key, deprecated_code, "deprecated")
    await remove_criterion(container, removed_criterion_id)
    await delete_data_item(container, context_project.data_item_ids["coupon"])
    return code


async def test_get_story_context_returns_the_compact_story_shape(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    code = await set_up_story_cases(client, container, context_project)
    ready_case = await find_ready_case(client, context_project, code)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)

    response = await call_tool(
        client, holder.token, "get_story_context", {"story_key": f" {context_project.story.jira_key.lower()} "}
    )

    content = read_tool_json(response)
    cases = content["cases"]
    assert isinstance(cases, list)
    case = cases[0]
    assert isinstance(case, dict)
    data_keys = case.pop("data_keys")
    assert isinstance(data_keys, list)
    assert sorted(data_keys) == ["coupon", "user_email", "user_password"]
    story_key = context_project.story.jira_key
    assert content == {
        "story": {
            "key": story_key,
            "title": f"Story {story_key}",
            "test_status": "not_started",
            "jira_status": "In Progress",
        },
        "criteria": [{"code": "AC1", "text": "Pay by card"}, {"code": "AC2", "text": "Get a receipt"}],
        "cases": [
            {
                "id": str(ready_case.id),
                "code": code,
                "title": "Pay by card and get the invoice",
                "priority": "high",
                "version": ready_case.version_number,
                "criteria": ["AC1"],
                "preconditions": "The cart holds {{data.coupon}}",
                "steps": [
                    {
                        "order": 1,
                        "action": "Sign in as {{data.user_email}} with {{data.user_password}}",
                        "expected": "The account page opens",
                    },
                    {"order": 2, "action": "Upload {{file.invoice}}"},
                ],
                "file_keys": ["invoice"],
            }
        ],
        "other_case_count": 2,
        "data": [
            {
                "key": "user_email",
                "kind": "variable",
                "value": PROJECT_EMAIL,
                "by_environment": {"Staging": STAGING_EMAIL},
            },
            {"key": "user_password", "kind": "secret", "value": "{{data.user_password}}"},
        ],
        "missing_data_keys": ["coupon"],
        "files": [{"case": code, "key": "invoice", "file_name": "invoice.pdf"}],
        "environments": [
            {"name": "Production", "base_url": "https://shop.test", "health_check_url": "https://shop.test/health"},
            {"name": "Staging", "base_url": "https://staging.shop.test", "is_default": True},
        ],
    }
    assert ready_case.version_number == 3


async def test_get_story_context_never_shows_secret_plaintext(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    await set_up_story_cases(client, container, context_project)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.ADMIN)

    response = await call_tool(client, holder.token, "get_story_context", {"story_key": context_project.story.jira_key})

    raw_text = response.text
    assert response.json()["result"].get("isError") is not True
    assert PROJECT_PASSWORD not in raw_text
    assert STAGING_PASSWORD not in raw_text
    assert "old@shop.test" not in raw_text
    assert "Legacy" not in raw_text


async def test_get_story_context_with_no_ready_cases_leaves_empty_fields_out(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.VIEWER)

    response = await call_tool(client, holder.token, "get_story_context", {"story_key": context_project.story.jira_key})

    content = read_tool_json(response)
    assert set(content) == {"story", "criteria", "other_case_count", "environments"}
    assert content["other_case_count"] == 0


@pytest.mark.parametrize(
    "role",
    [ProjectRole.ADMIN, ProjectRole.QC, ProjectRole.DEV, ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER],
)
async def test_get_story_context_works_for_every_role(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    created_case = await create_ready_case(client, container, context_project, [build_step("Open {{data.user_email}}")])
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, role)

    response = await call_tool(client, holder.token, "get_story_context", {"story_key": context_project.story.jira_key})

    content = read_tool_json(response)
    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["code"] for case in cases if isinstance(case, dict)] == [created_case.code]


async def test_get_story_context_works_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)
    await archive_project(container, context_project.project)

    response = await call_tool(client, holder.token, "get_story_context", {"story_key": context_project.story.jira_key})

    content = read_tool_json(response)
    story = content["story"]
    assert isinstance(story, dict)
    assert story["key"] == context_project.story.jira_key


async def test_get_story_context_refuses_unknown_and_foreign_stories(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    context_project = await set_up_context_project(client, container, recording_mailer)
    other_project = await seed_project(container)
    other_story = await seed_story(container, other_project, f"{other_project.key}-7", ["Other rule"])
    holder = await add_token_holder(client, container, recording_mailer, context_project.project, ProjectRole.QC)

    unknown = await call_tool(client, holder.token, "get_story_context", {"story_key": "NOPE-404"})
    foreign = await call_tool(client, holder.token, "get_story_context", {"story_key": other_story.jira_key})
    without_token = await call_tool(client, None, "get_story_context", {"story_key": context_project.story.jira_key})

    assert read_tool_error(unknown) == "NOT_FOUND: Story not found."
    assert read_tool_error(foreign).startswith("NOT_FOUND: ")
    assert read_tool_error(without_token).startswith("INVALID_API_TOKEN: ")

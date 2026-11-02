import pytest
from httpx import AsyncClient

from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import read_tool_error
from tests.api.test_cases.case_steps import CaseProject, create_case_code, get_case, set_up_case_project
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import archive_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def build_draft_case(story_key: str, title: str, **fields: object) -> dict[str, object]:
    return {
        "story_key": story_key,
        "title": title,
        "steps": [{"action": "Open the cart", "expected": "The cart is shown"}, {"action": "Pay"}],
        "source": f"Sheet {story_key}, row 2",
        **fields,
    }


async def set_up_token(
    client: AsyncClient,
    container: CasesContainer,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
) -> tuple[CaseProject, str]:
    case_project = await set_up_case_project(client, container, recording_mailer, role=role)
    token = await create_token(client, case_project.key)
    return case_project, token


async def count_cases(client: AsyncClient, case_project: CaseProject) -> int:
    response = await client.get(f"/api/projects/{case_project.key}/test-cases")
    assert response.status_code == 200, response.text
    return len(response.json())


async def test_check_draft_cases_reports_only_the_cases_with_an_issue_and_creates_nothing(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    story_key = case_project.story.jira_key
    await create_case_code(client, case_project.key, story_key, title="Existing case")
    cases = [
        build_draft_case(story_key.lower(), "Pay by card", criterion_codes=["AC1", "ac-2"]),
        build_draft_case("NOPE-1", "Ghost case"),
        build_draft_case(story_key, "Long case", steps=[{"action": f"Step {n}"} for n in range(101)]),
        build_draft_case(story_key, "T" * 201),
        build_draft_case(story_key, "EXISTING CASE"),
        build_draft_case(story_key, "pay by card", criterion_codes=["AC9", "Login"]),
    ]

    response = await call_tool(client, token, "check_draft_cases", {"cases": cases})

    assert read_tool_json(response) == {
        "case_count": 6,
        "creatable_count": 3,
        "issues": [
            {
                "index": 1,
                "source": "Sheet NOPE-1, row 2",
                "problem": "story_not_found",
                "is_duplicate": False,
                "unknown_criterion_codes": [],
            },
            {
                "index": 2,
                "source": f"Sheet {story_key}, row 2",
                "problem": "too_many_steps",
                "is_duplicate": False,
                "unknown_criterion_codes": [],
            },
            {
                "index": 3,
                "source": f"Sheet {story_key}, row 2",
                "problem": "text_too_long",
                "is_duplicate": False,
                "unknown_criterion_codes": [],
            },
            {
                "index": 4,
                "source": f"Sheet {story_key}, row 2",
                "problem": None,
                "is_duplicate": True,
                "unknown_criterion_codes": [],
            },
            {
                "index": 5,
                "source": f"Sheet {story_key}, row 2",
                "problem": None,
                "is_duplicate": True,
                "unknown_criterion_codes": ["AC9", "LOGIN"],
            },
        ],
    }
    assert await count_cases(client, case_project) == 1


async def test_create_draft_cases_creates_drafts_in_input_order(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    story_key = case_project.story.jira_key
    cases = [
        build_draft_case(
            story_key.lower(),
            "Pay by card",
            priority="high",
            preconditions="Signed in",
            business_value="Customers can pay",
            criterion_codes=["AC 1", "AC9"],
        ),
        build_draft_case(story_key, "Get a receipt", steps=[{"action": "Open orders", "expected": " "}]),
    ]
    events_before = len(recording_live_event_publisher.events)

    response = await call_tool(client, token, "create_draft_cases", {"cases": cases})

    assert read_tool_json(response) == {"codes": ["TC-1", "TC-2"]}
    first = (await get_case(client, case_project.key, "TC-1")).json()
    assert first["status"] == "draft"
    assert first["priority"] == "high"
    assert first["currentVersion"]["preconditions"] == "Signed in"
    assert first["currentVersion"]["businessValue"] == "Customers can pay"
    assert first["currentVersion"]["steps"] == [
        {"order": 1, "action": "Open the cart", "expected": "The cart is shown", "sharedStepKey": None},
        {"order": 2, "action": "Pay", "expected": None, "sharedStepKey": None},
    ]
    assert [criterion["code"] for criterion in first["criteria"]] == ["AC1"]
    second = (await get_case(client, case_project.key, "TC-2")).json()
    assert second["priority"] == "medium"
    assert second["currentVersion"]["steps"] == [
        {"order": 1, "action": "Open orders", "expected": None, "sharedStepKey": None}
    ]
    new_events = recording_live_event_publisher.events[events_before:]
    assert [event.ids["code"] for event in new_events] == ["TC-1", "TC-2"]


async def test_create_draft_cases_allows_duplicates(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    story_key = case_project.story.jira_key
    await create_case_code(client, case_project.key, story_key, title="Pay by card")

    response = await call_tool(
        client, token, "create_draft_cases", {"cases": [build_draft_case(story_key, "Pay by card")]}
    )

    assert read_tool_json(response) == {"codes": ["TC-2"]}


async def test_create_draft_cases_creates_nothing_when_one_case_has_a_problem(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    story_key = case_project.story.jira_key
    cases = [
        build_draft_case(story_key, "Pay by card"),
        build_draft_case("NOPE-1", "Ghost case"),
        build_draft_case(story_key, "T" * 201),
    ]

    response = await call_tool(client, token, "create_draft_cases", {"cases": cases})

    assert read_tool_error(response) == (
        "INVALID_REQUEST: Cases 1, 2 have a problem. Nothing was created; "
        "send only cases that check_draft_cases accepts."
    )
    assert await count_cases(client, case_project) == 0


@pytest.mark.parametrize("tool", ["check_draft_cases", "create_draft_cases"])
@pytest.mark.parametrize("role", [ProjectRole.DEV, ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER])
async def test_draft_case_tools_are_refused_without_test_case_edit(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    tool: str,
    role: ProjectRole,
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer, role)

    response = await call_tool(
        client, token, tool, {"cases": [build_draft_case(case_project.story.jira_key, "Pay by card")]}
    )

    assert read_tool_error(response).startswith("PERMISSION_DENIED: ")


async def test_project_admins_can_create_draft_cases(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer, ProjectRole.ADMIN)

    response = await call_tool(
        client, token, "create_draft_cases", {"cases": [build_draft_case(case_project.story.jira_key, "Pay")]}
    )

    assert read_tool_json(response) == {"codes": ["TC-1"]}


@pytest.mark.parametrize("tool", ["check_draft_cases", "create_draft_cases"])
async def test_draft_case_tools_are_refused_on_archived_projects(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, tool: str
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    await archive_project(test_cases_container, case_project.project)

    response = await call_tool(
        client, token, tool, {"cases": [build_draft_case(case_project.story.jira_key, "Pay by card")]}
    )

    assert read_tool_error(response).startswith("PROJECT_ARCHIVED: ")


@pytest.mark.parametrize("tool", ["check_draft_cases", "create_draft_cases"])
async def test_draft_case_tools_need_a_token(client: AsyncClient, tool: str) -> None:
    response = await call_tool(client, None, tool, {"cases": [build_draft_case("SHOP-1", "Pay by card")]})

    assert read_tool_error(response).startswith("INVALID_API_TOKEN: ")


@pytest.mark.parametrize("case_count", [0, 101])
async def test_draft_case_tools_take_one_to_a_hundred_cases(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer, case_count: int
) -> None:
    case_project, token = await set_up_token(client, test_cases_container, recording_mailer)
    cases = [build_draft_case(case_project.story.jira_key, f"Case {index}") for index in range(case_count)]

    response = await call_tool(client, token, "create_draft_cases", {"cases": cases})

    assert response.json()["result"]["isError"] is True
    assert await count_cases(client, case_project) == 0


@pytest.mark.parametrize(
    "case",
    [
        {"story_key": "SHOP-1", "title": "No steps", "steps": [], "source": "row 2"},
        {"story_key": "SHOP-1", "title": "No source", "steps": [{"action": "Pay"}]},
        {"story_key": "SHOP-1", "title": " ", "steps": [{"action": "Pay"}], "source": "row 2"},
    ],
)
async def test_draft_case_tools_refuse_a_case_without_steps_source_or_title(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    case: dict[str, object],
) -> None:
    _, token = await set_up_token(client, test_cases_container, recording_mailer)

    response = await call_tool(client, token, "check_draft_cases", {"cases": [case]})

    assert response.json()["result"]["isError"] is True

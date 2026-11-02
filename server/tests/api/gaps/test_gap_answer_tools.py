from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient
from sqlalchemy import insert, update

from app.container import Container
from app.modules.test_cases.infrastructure import TestCaseTable as CaseTable
from app.modules.test_cases.infrastructure import TestCaseVersionTable as CaseVersionTable
from app.modules.test_cases.typing.enums import TestCasePriority as CasePriority
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.gaps.gap_steps import (
    SeededStory,
    add_active_member,
    answer_gap,
    find_gap_row,
    list_notified_user_ids,
    raise_gap_id,
    read_tool_error,
    reassign_gap,
    seed_story,
    seed_test_case,
    sign_up_account,
)
from tests.api.projects.user_steps import SignedUpAccount, use_session
from tests.api.test_data.project_steps import SeededProject, add_member, archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


@dataclass(frozen=True)
class AnswererWorld:
    project: SeededProject
    story: SeededStory
    answerer: SignedUpAccount
    token: str


async def seed_world(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole = ProjectRole.BA
) -> AnswererWorld:
    project = await seed_project(container)
    story = await seed_story(container, project, criterion_codes=("AC1",))
    answerer = await sign_up_account(client, container, recording_mailer, project, role, "Bea Answerer")
    token = await create_token(client, project.key)
    return AnswererWorld(project=project, story=story, answerer=answerer, token=token)


async def give_case_a_version(container: Container, test_case_id: UUID, created_by: UUID) -> None:
    version_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        await session.execute(
            insert(CaseVersionTable).values(
                id=version_id,
                test_case_id=test_case_id,
                number=2,
                title="Pay with a saved card",
                priority=CasePriority.HIGH,
                business_value=None,
                preconditions="A saved card exists",
                steps=[
                    {"order": 1, "action": "Open checkout", "expected": None},
                    {"order": 2, "action": "Pay", "expected": "Paid"},
                ],
                criterion_ids=[],
                data_keys=[],
                file_version_ids=[],
                created_by=created_by,
                created_at=datetime.now(UTC),
            )
        )
        await session.execute(
            update(CaseTable).where(CaseTable.id == test_case_id).values(current_version_id=version_id)
        )


async def call_get_my_gaps(client: AsyncClient, token: str, **arguments: object) -> dict[str, object]:
    return read_tool_json(await call_tool(client, token, "get_my_gaps", arguments))


def list_gaps(content: dict[str, object]) -> list[dict[str, object]]:
    gaps = content["gaps"]
    assert isinstance(gaps, list)
    return gaps


async def test_get_my_gaps_lists_my_gaps_and_my_role_queue_high_severity_first(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    other_analyst_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.BA, "Ben Other")
    viewer_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.VIEWER, "Vic Viewer")
    case_id = await seed_test_case(container, world.project, world.story.id, 3, world.answerer.user_id)
    await give_case_a_version(container, case_id, world.answerer.user_id)
    use_session(client, world.answerer.session_token)
    mine_id = await raise_gap_id(
        client,
        world.project.key,
        world.story,
        severity="low",
        targetType="criterion",
        targetRef="AC1",
        question="Which page counts?",
        assigneeId=str(world.answerer.user_id),
    )
    queue_id = await raise_gap_id(
        client,
        world.project.key,
        world.story,
        type="missing_step",
        severity="high",
        targetType="test_case",
        targetRef="tc-3",
        question="What is clicked?",
        assigneeId=str(other_analyst_id),
    )
    assert (await reassign_gap(client, world.project.key, queue_id, assigneeRole="ba")).status_code == 200
    await raise_gap_id(client, world.project.key, world.story, assigneeId=str(other_analyst_id))
    qc_queue_id = await raise_gap_id(client, world.project.key, world.story)
    assert (await reassign_gap(client, world.project.key, qc_queue_id, assigneeRole="qc")).status_code == 200
    resolved_id = await raise_gap_id(client, world.project.key, world.story, assigneeId=str(world.answerer.user_id))
    assert (await answer_gap(client, world.project.key, resolved_id)).status_code == 200

    content = await call_get_my_gaps(client, world.token)

    assert content["gap_count"] == 2
    assert list_gaps(content) == [
        {
            "id": queue_id,
            "story_key": world.story.jira_key,
            "type": "missing_step",
            "severity": "high",
            "question": "What is clicked?",
            "is_assigned_to_me": False,
            "raised_by_name": "Bea Answerer",
            "target": {
                "type": "test_case",
                "ref": "TC-3",
                "case": {
                    "title": "Pay with a saved card",
                    "version": 2,
                    "preconditions": "A saved card exists",
                    "steps": [
                        {"order": 1, "action": "Open checkout"},
                        {"order": 2, "action": "Pay", "expected": "Paid"},
                    ],
                },
            },
        },
        {
            "id": mine_id,
            "story_key": world.story.jira_key,
            "type": "missing_ac",
            "severity": "low",
            "question": "Which page counts?",
            "is_assigned_to_me": True,
            "raised_by_name": "Bea Answerer",
            "target": {"type": "criterion", "ref": "AC1", "text": "Criterion AC1"},
        },
    ]
    assert content["stories"] == [
        {"key": world.story.jira_key, "title": f"Story {world.story.jira_key}", "open_gap_count": 4, "is_ready": False}
    ]
    assignees = content["assignees"]
    assert isinstance(assignees, list)
    assert {assignee["user_id"] for assignee in assignees} == {str(world.answerer.user_id), str(other_analyst_id)}
    assert str(viewer_id) not in {assignee["user_id"] for assignee in assignees}
    assert "test_data_url" not in content


async def test_get_my_gaps_links_the_test_data_page_for_a_missing_data_gap(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer, ProjectRole.QC)
    use_session(client, world.answerer.session_token)
    await raise_gap_id(
        client,
        world.project.key,
        world.story,
        type="missing_test_data",
        question="Which card number works on staging?",
        assigneeId=str(world.answerer.user_id),
    )

    content = await call_get_my_gaps(client, world.token)

    assert content["test_data_url"] == f"https://tessio.test/projects/{world.project.key}/test-data"


async def test_get_my_gaps_can_keep_to_one_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    other_story = await seed_story(container, world.project)
    use_session(client, world.answerer.session_token)
    story_gap_id = await raise_gap_id(client, world.project.key, world.story, assigneeId=str(world.answerer.user_id))
    await raise_gap_id(client, world.project.key, other_story, assigneeId=str(world.answerer.user_id))

    everything = await call_get_my_gaps(client, world.token)
    one_story = await call_get_my_gaps(client, world.token, story_key=world.story.jira_key.lower())
    unknown = await call_tool(client, world.token, "get_my_gaps", {"story_key": "NOPE-1"})

    assert everything["gap_count"] == 2
    assert [gap["id"] for gap in list_gaps(one_story)] == [story_gap_id]
    assert read_tool_error(unknown) == "NOT_FOUND: Story not found."


async def test_get_my_gaps_matches_the_role_queue_of_the_callers_role_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer, ProjectRole.DEV)
    use_session(client, world.answerer.session_token)
    dev_queue_id = await raise_gap_id(client, world.project.key, world.story)
    ba_queue_id = await raise_gap_id(client, world.project.key, world.story)
    assert (await reassign_gap(client, world.project.key, dev_queue_id, assigneeRole="dev")).status_code == 200
    assert (await reassign_gap(client, world.project.key, ba_queue_id, assigneeRole="ba")).status_code == 200

    content = await call_get_my_gaps(client, world.token)

    assert [gap["id"] for gap in list_gaps(content)] == [dev_queue_id]


async def test_get_my_gaps_offers_answers_to_similar_questions_same_story_first(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    other_story = await seed_story(container, world.project)
    use_session(client, world.answerer.session_token)
    answered = [
        (world.story, "Is checkout open at night?", "Yes, always."),
        (other_story, "Which currencies can refunds use at checkout?", "Refunds accept EUR currencies at checkout."),
        (other_story, "Do refunds need checkout approval?", "No."),
        (other_story, "Is checkout fast?", "Under two seconds."),
        (other_story, "What is the page title?", "Home"),
    ]
    for story, question, answer in answered:
        gap_id = await raise_gap_id(client, world.project.key, story, question=question)
        assert (await answer_gap(client, world.project.key, gap_id, answer)).status_code == 200
    open_id = await raise_gap_id(
        client, world.project.key, other_story, question="Which currencies does checkout accept?"
    )
    assert (await reassign_gap(client, world.project.key, open_id, assigneeRole="qc")).status_code == 200
    other_world = await seed_world(client, container, recording_mailer)
    use_session(client, other_world.answerer.session_token)
    elsewhere_id = await raise_gap_id(
        client, other_world.project.key, other_world.story, question="Which currencies does checkout accept?"
    )
    assert (await answer_gap(client, other_world.project.key, elsewhere_id, "Only EUR.")).status_code == 200
    use_session(client, world.answerer.session_token)
    await raise_gap_id(
        client,
        world.project.key,
        world.story,
        question="Which currencies does checkout accept for refunds?",
        assigneeId=str(world.answerer.user_id),
    )

    content = await call_get_my_gaps(client, world.token)

    [gap] = list_gaps(content)
    assert gap["similar_answers"] == [
        {"story_key": world.story.jira_key, "question": "Is checkout open at night?", "answer": "Yes, always."},
        {
            "story_key": other_story.jira_key,
            "question": "Which currencies can refunds use at checkout?",
            "answer": "Refunds accept EUR currencies at checkout.",
        },
        {"story_key": other_story.jira_key, "question": "Do refunds need checkout approval?", "answer": "No."},
    ]


async def test_get_my_gaps_offers_no_answer_when_only_common_words_match(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story, question="What is the page title?")
    assert (await answer_gap(client, world.project.key, gap_id, "Home")).status_code == 200
    await raise_gap_id(
        client,
        world.project.key,
        world.story,
        question="What is the refund limit?",
        assigneeId=str(world.answerer.user_id),
    )

    content = await call_get_my_gaps(client, world.token)

    [gap] = list_gaps(content)
    assert "similar_answers" not in gap


async def test_answer_gap_resolves_the_gap_via_claude_and_reports_readiness(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    first_id = await raise_gap_id(client, world.project.key, world.story)
    second_id = await raise_gap_id(client, world.project.key, world.story)

    first = await call_tool(client, world.token, "answer_gap", {"gap_id": first_id, "answer": "  EUR only.  "})
    second = await call_tool(client, world.token, "answer_gap", {"gap_id": second_id, "answer": "Yes."})

    assert read_tool_json(first) == {"status": "resolved", "open_gap_count": 1, "is_ready": False}
    assert read_tool_json(second) == {"status": "resolved", "open_gap_count": 0, "is_ready": True}
    gap = (await client.get(f"/api/projects/{world.project.key}/gaps/{first_id}")).json()
    assert gap["status"] == "resolved"
    assert gap["answer"] == "EUR only."
    assert gap["answeredBy"] == str(world.answerer.user_id)
    assert gap["isAnsweredViaClaude"] is True
    assert (await find_gap_row(container, first_id)).answered_via_token_id is not None
    changed_ids = [
        event.ids["gapId"]
        for event in recording_live_event_publisher.events
        if event.type is LiveEventType.GAP_CHANGED and event.ids["gapId"] in {first_id, second_id}
    ]
    assert changed_ids.count(first_id) == 2
    assert changed_ids.count(second_id) == 2


async def test_an_answer_in_the_app_is_not_via_claude(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story)

    response = await answer_gap(client, world.project.key, gap_id)

    assert response.json()["isAnsweredViaClaude"] is False
    assert (await find_gap_row(container, gap_id)).answered_via_token_id is None


async def test_answer_gap_refuses_a_resolved_gap_and_an_empty_answer(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story)
    assert (await answer_gap(client, world.project.key, gap_id)).status_code == 200

    resolved = await call_tool(client, world.token, "answer_gap", {"gap_id": gap_id, "answer": "Again."})
    empty = await call_tool(client, world.token, "answer_gap", {"gap_id": gap_id, "answer": "   "})

    assert read_tool_error(resolved) == "GAP_NOT_OPEN: This gap is already resolved."
    assert empty.json()["result"]["isError"] is True


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [("answer_gap", {"answer": "EUR only."}), ("reassign_gap", {"assignee_role": "qc"})],
)
async def test_a_gap_of_another_project_is_not_found(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    other_world = await seed_world(client, container, recording_mailer)
    use_session(client, other_world.answerer.session_token)
    other_gap_id = await raise_gap_id(client, other_world.project.key, other_world.story)
    world = await seed_world(client, container, recording_mailer)
    await add_member(container, other_world.project, world.answerer.user_id, ProjectRole.BA)

    response = await call_tool(client, world.token, tool_name, {"gap_id": other_gap_id, **arguments})

    assert read_tool_error(response) == "NOT_FOUND: Gap not found."
    assert (await find_gap_row(container, other_gap_id)).status == "open"


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("get_my_gaps", {}),
        ("answer_gap", {"answer": "EUR only."}),
        ("reassign_gap", {"assignee_role": "qc"}),
    ],
)
async def test_viewer_tokens_are_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    tool_name: str,
    arguments: dict[str, object],
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story)
    await sign_up_account(client, container, recording_mailer, world.project, ProjectRole.VIEWER)
    viewer_token = await create_token(client, world.project.key)
    tool_arguments = arguments if tool_name == "get_my_gaps" else {"gap_id": gap_id, **arguments}

    response = await call_tool(client, viewer_token, tool_name, tool_arguments)

    assert read_tool_error(response).startswith("PERMISSION_DENIED: ")
    assert (await find_gap_row(container, gap_id)).status == "open"


@pytest.mark.parametrize("tool_name", ["get_my_gaps", "answer_gap", "reassign_gap"])
async def test_tools_are_refused_on_archived_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, tool_name: str
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story)
    await archive_project(container, world.project)
    arguments_by_tool: dict[str, dict[str, object]] = {
        "get_my_gaps": {},
        "answer_gap": {"gap_id": gap_id, "answer": "EUR only."},
        "reassign_gap": {"gap_id": gap_id, "assignee_role": "qc"},
    }
    arguments = arguments_by_tool[tool_name]

    response = await call_tool(client, world.token, tool_name, arguments)

    assert read_tool_error(response).startswith("PROJECT_ARCHIVED: ")


async def test_reassign_gap_moves_the_gap_to_a_role_queue_and_notifies_it(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    first_qc_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.QC, "Quinn One")
    second_qc_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.QC, "Quinn Two")
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story, assigneeId=str(world.answerer.user_id))

    response = await call_tool(client, world.token, "reassign_gap", {"gap_id": gap_id, "assignee_role": "qc"})

    assert read_tool_json(response) == {"assignee_role": "qc"}
    row = await find_gap_row(container, gap_id)
    assert (row.assignee_id, row.assignee_role) == (None, ProjectRole.QC)
    assert set(await list_notified_user_ids(container, world.project, gap_id)) >= {first_qc_id, second_qc_id}
    assert any(
        event.type is LiveEventType.GAP_CHANGED and event.ids["gapId"] == gap_id
        for event in recording_live_event_publisher.events
    )
    assert (await call_get_my_gaps(client, world.token))["gap_count"] == 0


async def test_reassign_gap_moves_the_gap_to_a_member(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    developer_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.DEV, "Dana Dev")
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story, assigneeId=str(world.answerer.user_id))

    response = await call_tool(
        client, world.token, "reassign_gap", {"gap_id": gap_id, "assignee_user_id": str(developer_id)}
    )

    assert read_tool_json(response) == {"assignee_name": "Dana Dev"}
    assert (await find_gap_row(container, gap_id)).assignee_id == developer_id
    assert await list_notified_user_ids(container, world.project, gap_id) == [developer_id]


@pytest.mark.parametrize(
    ("arguments", "error"),
    [
        ({}, "INVALID_REQUEST: Give exactly one of assignee_user_id or assignee_role."),
        (
            {"assignee_role": "qc", "assignee_user_id": "00000000-0000-7000-8000-000000000000"},
            "INVALID_REQUEST: Give exactly one of assignee_user_id or assignee_role.",
        ),
        ({"assignee_role": "viewer"}, "INVALID_REQUEST: Viewers cannot answer gaps."),
    ],
)
async def test_reassign_gap_needs_one_assignee_who_can_answer(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    arguments: dict[str, object],
    error: str,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story, assigneeId=str(world.answerer.user_id))

    response = await call_tool(client, world.token, "reassign_gap", {"gap_id": gap_id, **arguments})

    assert read_tool_error(response) == error
    assert (await find_gap_row(container, gap_id)).assignee_id == world.answerer.user_id


async def test_reassign_gap_refuses_a_viewer_or_a_stranger_as_assignee(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    viewer_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.VIEWER, "Vic Viewer")
    use_session(client, world.answerer.session_token)
    gap_id = await raise_gap_id(client, world.project.key, world.story)

    to_viewer = await call_tool(
        client, world.token, "reassign_gap", {"gap_id": gap_id, "assignee_user_id": str(viewer_id)}
    )
    to_stranger = await call_tool(
        client, world.token, "reassign_gap", {"gap_id": gap_id, "assignee_user_id": str(uuid7())}
    )

    assert read_tool_error(to_viewer).startswith("ASSIGNEE_NOT_ACTIVE_MEMBER: ")
    assert read_tool_error(to_stranger).startswith("ASSIGNEE_NOT_ACTIVE_MEMBER: ")


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("get_my_gaps", {}),
        ("answer_gap", {"gap_id": str(uuid7()), "answer": "EUR only."}),
        ("reassign_gap", {"gap_id": str(uuid7()), "assignee_role": "qc"}),
    ],
)
async def test_the_tools_need_a_token(client: AsyncClient, tool_name: str, arguments: dict[str, object]) -> None:
    response = await call_tool(client, None, tool_name, arguments)

    assert read_tool_error(response).startswith("INVALID_API_TOKEN: ")

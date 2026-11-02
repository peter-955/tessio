from httpx import AsyncClient, Response

from app.modules.files import StoredFileKind, StoredFileStatus
from tests.api.test_cases.case_steps import (
    CaseProject,
    build_xlsx,
    create_case_code,
    get_case,
    seed_story,
    set_up_case_project,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import seed_import_file
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher

HEADER: list[str | None] = ["Title", "Priority", "Preconditions", "Step", "Expected result", "Covers AC"]


async def upload(
    test_cases_container: CasesContainer,
    case_project: CaseProject,
    file_name: str,
    content: bytes,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    size: int | None = None,
    kind: StoredFileKind = StoredFileKind.IMPORT,
) -> str:
    file_id = await seed_import_file(
        test_cases_container,
        test_cases_container.in_memory_object_storage,
        case_project.project,
        case_project.user_id,
        file_name,
        content,
        status,
        size,
        kind,
    )
    return str(file_id)


async def preview(client: AsyncClient, case_project: CaseProject, file_id: str) -> Response:
    return await client.post(f"/api/projects/{case_project.key}/test-case-imports/preview", json={"fileId": file_id})


async def commit(client: AsyncClient, case_project: CaseProject, file_id: str, indexes: list[int]) -> Response:
    return await client.post(
        f"/api/projects/{case_project.key}/test-case-imports/commit", json={"fileId": file_id, "indexes": indexes}
    )


def build_workbook(case_project: CaseProject, second_story_key: str) -> bytes:
    return build_xlsx(
        {
            case_project.story.jira_key: [
                HEADER,
                ["Pay by card", "High", "Signed in", "Open cart", "Cart is shown", "AC1, ac 3"],
                [None, None, None, "Pay", "Paid", None],
                [None, None, None, None, None, None],
                ["Pay by voucher", "urgent", None, None, None, "AC-2"],
            ],
            second_story_key: [
                [None, None],
                ["Name", "Action", "Expected"],
                [None, "Orphan step", None],
                ["Download receipt", "Open orders", "Receipt shown"],
            ],
            "UNKNOWN-9": [HEADER, ["Ghost case", None, None, "Look", None, None]],
            "Notes": [["Some notes"], ["more"]],
        }
    )


async def set_up_import(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> tuple[CaseProject, str, str]:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    second_story = await seed_story(test_cases_container, case_project.project, f"{case_project.key}-2")
    file_id = await upload(
        test_cases_container, case_project, "cases.xlsx", build_workbook(case_project, second_story.jira_key)
    )
    return case_project, second_story.jira_key, file_id


async def test_preview_reads_every_tab_as_a_story(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, second_story_key, file_id = await set_up_import(client, test_cases_container, recording_mailer)
    first_tab = case_project.story.jira_key

    response = await preview(client, case_project, file_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["format"] == "xlsx"
    assert body["items"] == [
        {
            "index": 0,
            "location": f"{first_tab} row 2",
            "storyKey": first_tab,
            "title": "Pay by card",
            "priority": "high",
            "stepCount": 2,
            "criterionCodes": ["AC1", "AC3"],
            "unknownCriterionCodes": ["AC3"],
            "isDuplicate": False,
            "problem": None,
        },
        {
            "index": 1,
            "location": f"{first_tab} row 5",
            "storyKey": first_tab,
            "title": "Pay by voucher",
            "priority": "medium",
            "stepCount": 0,
            "criterionCodes": ["AC2"],
            "unknownCriterionCodes": [],
            "isDuplicate": False,
            "problem": None,
        },
        {
            "index": 2,
            "location": f"{second_story_key} row 4",
            "storyKey": second_story_key,
            "title": "Download receipt",
            "priority": "medium",
            "stepCount": 1,
            "criterionCodes": [],
            "unknownCriterionCodes": [],
            "isDuplicate": False,
            "problem": None,
        },
        {
            "index": 3,
            "location": "UNKNOWN-9 row 2",
            "storyKey": "UNKNOWN-9",
            "title": "Ghost case",
            "priority": "medium",
            "stepCount": 1,
            "criterionCodes": [],
            "unknownCriterionCodes": [],
            "isDuplicate": False,
            "problem": "story_not_found",
        },
    ]
    assert body["skipped"] == [
        {"location": f"{second_story_key} row 3", "reason": "step_without_case"},
        {"location": "Notes", "reason": "sheet_without_header"},
    ]


async def test_commit_creates_the_chosen_cases_as_drafts(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project, second_story_key, file_id = await set_up_import(client, test_cases_container, recording_mailer)
    events_before = len(recording_live_event_publisher.events)

    response = await commit(client, case_project, file_id, [0, 2, 0])

    assert response.status_code == 201, response.text
    assert response.json() == {
        "created": [
            {"code": "TC-1", "storyKey": case_project.story.jira_key, "title": "Pay by card"},
            {"code": "TC-2", "storyKey": second_story_key, "title": "Download receipt"},
        ]
    }
    first = (await get_case(client, case_project.key, "TC-1")).json()
    assert first["status"] == "draft"
    assert first["priority"] == "high"
    assert first["currentVersion"]["preconditions"] == "Signed in"
    assert first["currentVersion"]["steps"] == [
        {"order": 1, "action": "Open cart", "expected": "Cart is shown", "sharedStepKey": None},
        {"order": 2, "action": "Pay", "expected": "Paid", "sharedStepKey": None},
    ]
    assert [criterion["code"] for criterion in first["criteria"]] == ["AC1"]
    new_events = recording_live_event_publisher.events[events_before:]
    assert [event.ids["code"] for event in new_events] == ["TC-1", "TC-2"]


async def test_preview_flags_duplicate_titles(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, _, file_id = await set_up_import(client, test_cases_container, recording_mailer)
    await create_case_code(client, case_project.key, case_project.story.jira_key, title="PAY BY CARD")

    items = (await preview(client, case_project, file_id)).json()["items"]

    assert [item["isDuplicate"] for item in items] == [True, False, False, False]
    assert (await commit(client, case_project, file_id, [0])).status_code == 201


async def test_csv_uses_the_story_column_and_a_semicolon_delimiter(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    story_key = case_project.story.jira_key
    content = (
        "Story key;Test case;Steps;Expected results;Acceptance criteria\n"
        f"{story_key.lower()};Pay by card;Open cart;Cart shown;AC2\n"
        ";;Pay;Paid;\n"
        ";Missing story;Look;;\n"
    ).encode()
    file_id = await upload(test_cases_container, case_project, "cases.csv", content)

    body = (await preview(client, case_project, file_id)).json()

    assert body["format"] == "csv"
    assert [(item["location"], item["storyKey"], item["stepCount"], item["problem"]) for item in body["items"]] == [
        ("row 2", story_key, 2, None),
        ("row 4", None, 1, "story_key_missing"),
    ]
    assert body["items"][0]["criterionCodes"] == ["AC2"]
    assert (await commit(client, case_project, file_id, [0])).status_code == 201


async def test_preview_rejects_unreadable_files(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    broken_xlsx = await upload(test_cases_container, case_project, "cases.xlsx", b"not a zip file")
    headerless_csv = await upload(test_cases_container, case_project, "cases.csv", b"a,b\n1,2\n")
    wrong_extension = await upload(test_cases_container, case_project, "cases.json", b"{}")

    responses = [
        await preview(client, case_project, file_id) for file_id in (broken_xlsx, headerless_csv, wrong_extension)
    ]

    assert [response.status_code for response in responses] == [422, 422, 422]
    assert {response.json()["code"] for response in responses} == {"IMPORT_INVALID_FILE"}


async def test_preview_refuses_missing_pending_and_large_files(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    content = build_xlsx({case_project.story.jira_key: [HEADER]})
    test_file = await upload(test_cases_container, case_project, "cases.xlsx", content, kind=StoredFileKind.TEST_FILE)
    pending = await upload(test_cases_container, case_project, "cases.xlsx", content, StoredFileStatus.PENDING)
    too_large = await upload(test_cases_container, case_project, "cases.xlsx", content, size=5 * 1024 * 1024 + 1)

    responses = [await preview(client, case_project, file_id) for file_id in (test_file, pending, too_large)]

    assert [response.status_code for response in responses] == [404, 409, 413]
    codes = [response.json()["code"] for response in responses]
    assert codes == ["NOT_FOUND", "UPLOAD_NOT_COMPLETED", "FILE_TOO_LARGE"]
    assert responses[2].json()["message"] == "Import files can be at most 5 MB."


async def test_commit_refuses_out_of_range_and_problem_indexes(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project, _, file_id = await set_up_import(client, test_cases_container, recording_mailer)

    out_of_range = await commit(client, case_project, file_id, [0, 99])
    with_problem = await commit(client, case_project, file_id, [3])
    negative = await commit(client, case_project, file_id, [-1])

    assert [out_of_range.status_code, with_problem.status_code, negative.status_code] == [422, 422, 422]
    assert out_of_range.json() == {"code": "INVALID_REQUEST", "message": "A chosen case cannot be imported."}
    assert (await client.get(f"/api/projects/{case_project.key}/test-cases")).json() == []

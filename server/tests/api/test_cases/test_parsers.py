from datetime import UTC, datetime
from io import BytesIO
from uuid import uuid7
from zipfile import ZipFile

import pytest

from app.modules.test_cases.domains.case_criterion.entity import CaseCriterion
from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion as CaseVersion
from app.modules.test_cases.domains.test_step.entity import TestStep as CaseStep
from app.modules.test_cases.errors import (
    CaseNotReadyError,
    CriterionNotLinkableError,
    ImportInvalidFileError,
    UnknownReferenceError,
)
from app.modules.test_cases.errors import (
    TestCaseNotFoundError as CaseNotFoundError,
)
from app.modules.test_cases.typing.enums import CaseImportFormat, CaseImportProblem, CaseImportSkipReason
from app.modules.test_cases.typing.enums import TestCasePriority as CasePriority
from app.modules.test_cases.utils.case_code import parse_case_code
from app.modules.test_cases.utils.case_import_parser import parse_case_import
from app.modules.test_cases.utils.case_import_preview import build_preview_items
from app.modules.test_cases.utils.criterion_links import require_linkable
from app.modules.test_cases.utils.readiness import find_unknown_references, require_ready
from app.modules.test_cases.utils.references import parse_references
from tests.api.test_cases.case_steps import build_xlsx


def build_version(preconditions: str | None, steps: list[CaseStep]) -> CaseVersion:
    return CaseVersion(
        id=uuid7(),
        test_case_id=uuid7(),
        number=1,
        title="Case",
        priority=CasePriority.MEDIUM,
        business_value=None,
        preconditions=preconditions,
        steps=steps,
        criterion_ids=[],
        data_keys=[],
        file_version_ids=[],
        created_by=uuid7(),
        created_at=datetime.now(UTC),
    )


def build_imported_case(**fields: object) -> ImportedCase:
    values: dict[str, object] = {
        "location": "row 2",
        "story_key": "SHOP-1",
        "title": "Pay",
        "priority": CasePriority.MEDIUM,
        "business_value": None,
        "preconditions": None,
        "steps": [],
        "criterion_codes": [],
    }
    return ImportedCase.model_validate(values | fields)


def test_parse_references_scans_preconditions_actions_and_expected_results() -> None:
    references = parse_references(
        "Signed in as {{ data.user.name }} and {{data.user.name}}",
        [
            CaseStep(order=1, action="Open {{data.base_url}}", expected="Shows {{file.invoice-v2.pdf}}"),
            CaseStep(order=2, action="{{file.cv}} {{ other.x }} {{data.}} {{data.1abc}}", expected=None),
        ],
    )

    assert references.data_keys == frozenset({"user.name", "base_url"})
    assert references.file_keys == frozenset({"invoice-v2.pdf", "cv"})


def test_parse_references_without_text_finds_nothing() -> None:
    references = parse_references(None, [])

    assert (references.data_keys, references.file_keys) == (frozenset(), frozenset())


def test_unknown_references_are_sorted_and_ready_needs_steps() -> None:
    step = CaseStep(order=1, action="{{data.z}} {{data.a}} {{data.known}}", expected=None)
    version = build_version("{{file.b}}", [step])

    assert find_unknown_references(version, frozenset({"known"}), frozenset()) == ["data.a", "data.z", "file.b"]
    with pytest.raises(UnknownReferenceError) as raised:
        require_ready(version, frozenset({"known"}), frozenset())
    assert raised.value.references == ["data.a", "data.z", "file.b"]
    assert raised.value.message == "Unknown references: {{data.a}}, {{data.z}}, {{file.b}}."
    with pytest.raises(CaseNotReadyError):
        require_ready(build_version(None, []), frozenset(), frozenset())
    require_ready(version, frozenset({"known", "a", "z"}), frozenset({"b"}))


@pytest.mark.parametrize(("code", "number"), [("TC-1", 1), ("tc-42", 42), (" TC-999999999 ", 999999999)])
def test_parse_case_code_reads_the_number(code: str, number: int) -> None:
    assert parse_case_code(code) == number


@pytest.mark.parametrize("code", ["TC-0", "TC-01", "TC-1000000000", "TC1", "1", "TC-1a", ""])
def test_parse_case_code_rejects_other_text(code: str) -> None:
    with pytest.raises(CaseNotFoundError):
        parse_case_code(code)


def test_require_linkable_dedupes_and_allows_removed_criteria_only_when_already_linked() -> None:
    story_id = uuid7()
    current = CaseCriterion(id=uuid7(), story_id=story_id, code="AC1", text="a", position=1, is_removed=False)
    removed = CaseCriterion(id=uuid7(), story_id=story_id, code="AC2", text="b", position=2, is_removed=True)

    assert require_linkable([removed.id, current.id, removed.id], [current, removed], {removed.id}) == [
        removed.id,
        current.id,
    ]
    with pytest.raises(CriterionNotLinkableError):
        require_linkable([removed.id], [current, removed], set())
    with pytest.raises(CriterionNotLinkableError):
        require_linkable([uuid7()], [current, removed], set())


def test_xlsx_rows_build_cases_with_steps_codes_and_priorities() -> None:
    content = build_xlsx(
        {
            " shop-1 ": [
                [None],
                ["  TITLE ", "Business value", "Precondition", "Action", "Expected", "AC", "Priority"],
                ["Pay", "Revenue", "Cart", "Open", "Shown", "covers AC 1, AC-02, ac1", "CRITICAL"],
                [None, None, None, "Pay", None, "AC4", None],
                [None, None, None, None, "only expected", None, None],
                ["Refund", None, None, None, None, None, "unknown"],
            ]
        }
    )

    parsed = parse_case_import("Cases.XLSX", content)

    assert parsed.format is CaseImportFormat.XLSX
    assert parsed.skipped == []
    assert [case.model_dump() for case in parsed.cases] == [
        {
            "location": "shop-1 row 3",
            "story_key": "SHOP-1",
            "title": "Pay",
            "priority": CasePriority.CRITICAL,
            "business_value": "Revenue",
            "preconditions": "Cart",
            "steps": [
                {"order": 1, "action": "Open", "expected": "Shown"},
                {"order": 2, "action": "Pay", "expected": None},
            ],
            "criterion_codes": ["AC1", "AC2", "AC4"],
        },
        {
            "location": "shop-1 row 6",
            "story_key": "SHOP-1",
            "title": "Refund",
            "priority": CasePriority.MEDIUM,
            "business_value": None,
            "preconditions": None,
            "steps": [],
            "criterion_codes": [],
        },
    ]


def test_xlsx_numbers_become_text_and_a_story_column_overrides_the_tab() -> None:
    content = build_xlsx({"Tab": [["Jira key", "Name", "Steps"], ["web-7", "Case 1", None]]})

    parsed = parse_case_import("cases.xlsx", content)

    assert [(case.story_key, case.title) for case in parsed.cases] == [("WEB-7", "Case 1")]


def test_csv_is_sniffed_and_falls_back_to_commas() -> None:
    tab_separated = b"title\tstep\tstory\nPay\tOpen\tSHOP-1\n"
    comma_separated = "﻿title,step\nPay,Open\n".encode()

    tab_parsed = parse_case_import("cases.csv", tab_separated)
    comma_parsed = parse_case_import("cases.csv", comma_separated)

    assert parse_case_import("cases.csv", tab_separated).format is CaseImportFormat.CSV
    assert [(case.story_key, case.steps[0].action) for case in tab_parsed.cases] == [("SHOP-1", "Open")]
    assert [(case.location, case.story_key) for case in comma_parsed.cases] == [("row 2", None)]


def test_csv_step_before_a_case_is_skipped() -> None:
    parsed = parse_case_import("cases.csv", b"Title,Step\n,Orphan\nPay,Open\n")

    assert parsed.skipped == [CaseImportSkip(location="row 2", reason=CaseImportSkipReason.STEP_WITHOUT_CASE)]
    assert [case.title for case in parsed.cases] == ["Pay"]


@pytest.mark.parametrize(
    ("file_name", "content"),
    [
        ("cases.txt", b"Title,Step\nPay,Open\n"),
        ("cases.csv", b"\xff\xfe\x00bad"),
        ("cases.csv", b"Title,Expected\nPay,Shown\n"),
        ("cases.csv", b""),
        ("cases.xlsx", b"PK\x03\x04 broken"),
        ("cases.xlsx", b"plain text"),
    ],
)
def test_unreadable_files_are_invalid(file_name: str, content: bytes) -> None:
    with pytest.raises(ImportInvalidFileError):
        parse_case_import(file_name, content)


def replace_workbook_part(content: bytes, part_name: str, part_content: bytes) -> bytes:
    buffer = BytesIO()
    with ZipFile(BytesIO(content)) as source, ZipFile(buffer, "w") as target:
        for item in source.infolist():
            target.writestr(item, part_content if item.filename == part_name else source.read(item.filename))
    return buffer.getvalue()


@pytest.mark.parametrize(
    ("part_name", "part_content"),
    [
        ("[Content_Types].xml", b"garbage"),
        ("xl/workbook.xml", b"<<<"),
        ("xl/worksheets/sheet1.xml", b"<not xml"),
    ],
)
def test_xlsx_with_corrupt_parts_is_invalid(part_name: str, part_content: bytes) -> None:
    content = replace_workbook_part(
        build_xlsx({"SHOP-1": [["Title", "Step"], ["Pay", "Open"]]}), part_name, part_content
    )

    with pytest.raises(ImportInvalidFileError):
        parse_case_import("cases.xlsx", content)


def test_nul_characters_are_removed_from_cells() -> None:
    parsed = parse_case_import("cases.csv", b"Title,Step\nPa\x00y,Op\x00en\n")

    assert [(case.title, case.steps[0].action) for case in parsed.cases] == [("Pay", "Open")]


def test_too_many_rows_or_cases_are_invalid() -> None:
    many_rows = "Title,Step\nPay,Open\n" + ",Next\n" * 5000
    many_cases = "Title,Step\n" + "".join(f"Case {number},Open\n" for number in range(501))

    with pytest.raises(ImportInvalidFileError):
        parse_case_import("cases.csv", many_rows.encode())
    with pytest.raises(ImportInvalidFileError):
        parse_case_import("cases.csv", many_cases.encode())


def test_preview_items_report_problems_in_order_and_unknown_codes() -> None:
    story = CaseStory(id=uuid7(), jira_key="SHOP-1", title="Shop")
    criteria = [
        CaseCriterion(id=uuid7(), story_id=story.id, code="AC1", text="a", position=1, is_removed=False),
        CaseCriterion(id=uuid7(), story_id=story.id, code="AC2", text="b", position=2, is_removed=True),
    ]
    long_text = "x" * 5001
    cases = [
        build_imported_case(story_key=None, steps=[CaseStep(order=1, action=long_text, expected=None)]),
        build_imported_case(story_key="NOPE-1"),
        build_imported_case(
            title="Many", steps=[CaseStep(order=index, action="a", expected=None) for index in range(1, 102)]
        ),
        build_imported_case(title="t" * 201),
        build_imported_case(title="Long", preconditions=long_text),
        build_imported_case(title="Pay", criterion_codes=["AC1", "AC2", "AC9"]),
        build_imported_case(title="pay"),
    ]

    items = build_preview_items(cases, {"SHOP-1": story}, {story.id: criteria}, set())

    assert [item.problem for item in items] == [
        CaseImportProblem.STORY_KEY_MISSING,
        CaseImportProblem.STORY_NOT_FOUND,
        CaseImportProblem.TOO_MANY_STEPS,
        CaseImportProblem.TEXT_TOO_LONG,
        CaseImportProblem.TEXT_TOO_LONG,
        None,
        None,
    ]
    assert items[5].unknown_criterion_codes == ["AC2", "AC9"]
    assert [item.is_duplicate for item in items] == [False, False, False, False, False, False, True]

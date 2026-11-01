from collections.abc import Iterable, Mapping, Sequence

from app.modules.test_cases.domains.case_import_skip.entity import CaseImportSkip
from app.modules.test_cases.domains.imported_case.entity import ImportedCase
from app.modules.test_cases.domains.parsed_case_sheet.entity import ParsedCaseSheet
from app.modules.test_cases.domains.test_step.entity import TestStep
from app.modules.test_cases.errors import ImportInvalidFileError
from app.modules.test_cases.typing.constants import (
    ACTION_COLUMN,
    BUSINESS_VALUE_COLUMN,
    CRITERIA_COLUMN,
    EXPECTED_COLUMN,
    PRECONDITIONS_COLUMN,
    PRIORITY_COLUMN,
    STORY_COLUMN,
    TITLE_COLUMN,
)
from app.modules.test_cases.typing.enums import CaseImportSkipReason
from app.modules.test_cases.utils.case_import_cells import (
    find_columns,
    is_empty_row,
    parse_criterion_codes,
    parse_priority,
    read_cell,
)


def build_location(sheet_name: str | None, row_number: int) -> str:
    return f"row {row_number}" if sheet_name is None else f"{sheet_name} row {row_number}"


def build_step(row: Sequence[object], columns: Mapping[str, int], order: int) -> TestStep | None:
    action = read_cell(row, columns, ACTION_COLUMN)
    if action is None:
        return None
    return TestStep(order=order, action=action, expected=read_cell(row, columns, EXPECTED_COLUMN))


def start_case(
    row: Sequence[object], columns: Mapping[str, int], title: str, location: str, default_story_key: str | None
) -> ImportedCase:
    story_key = read_cell(row, columns, STORY_COLUMN)
    first_step = build_step(row, columns, 1)
    return ImportedCase(
        location=location,
        story_key=default_story_key if story_key is None else story_key.upper(),
        title=title,
        priority=parse_priority(read_cell(row, columns, PRIORITY_COLUMN)),
        business_value=read_cell(row, columns, BUSINESS_VALUE_COLUMN),
        preconditions=read_cell(row, columns, PRECONDITIONS_COLUMN),
        steps=[] if first_step is None else [first_step],
        criterion_codes=parse_criterion_codes(read_cell(row, columns, CRITERIA_COLUMN)),
    )


def continue_case(case: ImportedCase, row: Sequence[object], columns: Mapping[str, int]) -> ImportedCase:
    step = build_step(row, columns, len(case.steps) + 1)
    codes = parse_criterion_codes(read_cell(row, columns, CRITERIA_COLUMN))
    return case.model_copy(
        update={
            "steps": case.steps if step is None else [*case.steps, step],
            "criterion_codes": list(dict.fromkeys([*case.criterion_codes, *codes])),
        }
    )


def parse_case_rows(
    rows: Iterable[Sequence[object]], sheet_name: str | None, default_story_key: str | None, max_rows: int
) -> ParsedCaseSheet | None:
    columns: dict[str, int] | None = None
    cases: list[ImportedCase] = []
    skipped: list[CaseImportSkip] = []
    row_count = 0
    for row_number, row in enumerate(rows, start=1):
        if is_empty_row(row):
            continue
        row_count += 1
        if row_count > max_rows:
            raise ImportInvalidFileError
        if columns is None:
            columns = find_columns(row)
            if TITLE_COLUMN not in columns or ACTION_COLUMN not in columns:
                return None
            continue
        location = build_location(sheet_name, row_number)
        title = read_cell(row, columns, TITLE_COLUMN)
        if title is not None:
            cases.append(start_case(row, columns, title, location, default_story_key))
        elif read_cell(row, columns, ACTION_COLUMN) is None:
            continue
        elif cases:
            cases[-1] = continue_case(cases[-1], row, columns)
        else:
            skipped.append(CaseImportSkip(location=location, reason=CaseImportSkipReason.STEP_WITHOUT_CASE))
    if columns is None:
        return None
    return ParsedCaseSheet(cases=cases, skipped=skipped, row_count=row_count)

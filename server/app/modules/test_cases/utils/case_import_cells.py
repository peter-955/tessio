import re
from collections.abc import Mapping, Sequence

from app.modules.test_cases.typing.constants import (
    CRITERION_CODE_PATTERN,
    IMPORT_COLUMN_ALIASES,
    IMPORTED_CRITERION_CODE_TEMPLATE,
    NUL_CHARACTER,
)
from app.modules.test_cases.typing.enums import TestCasePriority


def read_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace(NUL_CHARACTER, "").strip()
    return text or None


def read_cell(row: Sequence[object], columns: Mapping[str, int], column: str) -> str | None:
    index = columns.get(column)
    if index is None or index >= len(row):
        return None
    return read_text(row[index])


def is_empty_row(row: Sequence[object]) -> bool:
    return all(read_text(value) is None for value in row)


def find_columns(header: Sequence[object]) -> dict[str, int]:
    columns: dict[str, int] = {}
    for index, value in enumerate(header):
        name = (read_text(value) or "").lower()
        for column, aliases in IMPORT_COLUMN_ALIASES.items():
            if name in aliases and column not in columns:
                columns[column] = index
    return columns


def parse_priority(text: str | None) -> TestCasePriority:
    value = (text or "").lower()
    return TestCasePriority(value) if value in TestCasePriority else TestCasePriority.MEDIUM


def parse_criterion_codes(text: str | None) -> list[str]:
    if text is None:
        return []
    codes = [
        IMPORTED_CRITERION_CODE_TEMPLATE.format(number=int(number))
        for number in re.findall(CRITERION_CODE_PATTERN, text)
    ]
    return list(dict.fromkeys(codes))

import re

from app.modules.test_cases.errors import TestCaseNotFoundError
from app.modules.test_cases.typing.constants import CASE_CODE_PATTERN


def parse_case_code(code: str) -> int:
    match = re.fullmatch(CASE_CODE_PATTERN, code.strip())
    if match is None:
        raise TestCaseNotFoundError
    return int(match.group(1))


def find_case_number(text: str) -> int | None:
    match = re.fullmatch(CASE_CODE_PATTERN, text.strip())
    return None if match is None else int(match.group(1))

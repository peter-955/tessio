from app.modules.insights.typing.constants import TEST_CASE_CODE_PREFIX


def format_case_code(number: int) -> str:
    return f"{TEST_CASE_CODE_PREFIX}{number}"

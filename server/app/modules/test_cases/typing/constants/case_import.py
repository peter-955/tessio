from collections.abc import Mapping

MAX_CASE_IMPORT_BYTES = 5242880
MAX_IMPORTED_CASES = 500
MAX_IMPORT_ROWS = 5000
XLSX_FILE_EXTENSIONS = (".xlsx",)
CSV_FILE_EXTENSIONS = (".csv",)
CSV_DELIMITERS = ",;\t"
CSV_SNIFF_SAMPLE_LENGTH = 8192
NUL_CHARACTER = "\x00"
CRITERION_CODE_PATTERN = r"(?i)\bAC\s*-?\s*(\d+)\b"
IMPORTED_CRITERION_CODE_TEMPLATE = "AC{number}"
STORY_COLUMN = "story"
TITLE_COLUMN = "title"
PRIORITY_COLUMN = "priority"
BUSINESS_VALUE_COLUMN = "business_value"
PRECONDITIONS_COLUMN = "preconditions"
ACTION_COLUMN = "action"
EXPECTED_COLUMN = "expected"
CRITERIA_COLUMN = "criteria"
IMPORT_COLUMN_ALIASES: Mapping[str, frozenset[str]] = {
    STORY_COLUMN: frozenset({"story", "story key", "jira key"}),
    TITLE_COLUMN: frozenset({"title", "test case", "name"}),
    PRIORITY_COLUMN: frozenset({"priority"}),
    BUSINESS_VALUE_COLUMN: frozenset({"business value"}),
    PRECONDITIONS_COLUMN: frozenset({"preconditions", "precondition"}),
    ACTION_COLUMN: frozenset({"step", "steps", "action"}),
    EXPECTED_COLUMN: frozenset({"expected", "expected result", "expected results"}),
    CRITERIA_COLUMN: frozenset({"covers ac", "ac", "acceptance criteria"}),
}

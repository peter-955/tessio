from datetime import timedelta

MAX_RUN_LOG_ENTRIES = 3000
MAX_RUN_LOG_TEXT_LENGTH = 4000
MAX_RUN_LOG_INPUT_LENGTH = 8000
MAX_RUN_LOG_TOOL_LENGTH = 200
RUN_LOG_UPLOAD_WINDOW = timedelta(hours=24)
RECORD_CASE_RESULT_TOOL_SUFFIX = "record_case_result"
BROWSER_TOOL_MARKERS = ("claude-in-chrome", "Claude_Browser")
TRUNCATED_INPUT_KEY = "truncated"

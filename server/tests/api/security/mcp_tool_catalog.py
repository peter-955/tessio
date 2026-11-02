from uuid import uuid7

from app.shared.common import Entity

UNKNOWN_RUN_ID = str(uuid7())
UNKNOWN_CASE_ID = str(uuid7())
UNKNOWN_GAP_ID = str(uuid7())


class McpToolCall(Entity):
    name: str
    arguments: dict[str, object]
    is_write: bool


MCP_TOOL_CALLS = [
    McpToolCall(name="start_run", arguments={"story_key": "X-1"}, is_write=True),
    McpToolCall(
        name="record_case_result",
        arguments={
            "run_id": UNKNOWN_RUN_ID,
            "case_id": UNKNOWN_CASE_ID,
            "status": "passed",
            "duration_ms": 1,
            "steps": [{"order": 1, "status": "passed", "actual_result": "Shown"}],
            "iteration": 0,
        },
        is_write=True,
    ),
    McpToolCall(name="finish_run", arguments={"run_id": UNKNOWN_RUN_ID}, is_write=True),
    McpToolCall(name="get_failed_cases", arguments={"run_id": UNKNOWN_RUN_ID}, is_write=False),
    McpToolCall(name="get_story_context", arguments={"story_key": "X-1"}, is_write=False),
    McpToolCall(name="get_suite_context", arguments={"suite": "Regression"}, is_write=False),
    McpToolCall(name="resolve_data", arguments={"run_id": UNKNOWN_RUN_ID, "keys": ["BASE_URL"]}, is_write=True),
    McpToolCall(name="get_test_file", arguments={"run_id": UNKNOWN_RUN_ID, "key": "key"}, is_write=True),
    McpToolCall(
        name="raise_gaps",
        arguments={"story_key": "X-1", "gaps": [{"type": "missing_ac", "question": "Which currencies?"}]},
        is_write=True,
    ),
    McpToolCall(name="get_open_gaps", arguments={"story_key": "X-1"}, is_write=False),
    McpToolCall(name="get_my_gaps", arguments={}, is_write=True),
    McpToolCall(name="answer_gap", arguments={"gap_id": UNKNOWN_GAP_ID, "answer": "EUR only."}, is_write=True),
    McpToolCall(name="reassign_gap", arguments={"gap_id": UNKNOWN_GAP_ID, "assignee_role": "ba"}, is_write=True),
    McpToolCall(
        name="set_test_data",
        arguments={"key": "SHOP_URL", "value": "https://shop.test", "kind": "variable"},
        is_write=True,
    ),
]

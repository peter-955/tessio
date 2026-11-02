from collections.abc import Mapping
from uuid import UUID

from mcp_types import CallToolResult
from pydantic import JsonValue

from app.modules.story_context import (
    DataEntry,
    build_compact_tool_result,
    build_context_case_json,
    build_context_data_json,
    build_context_environment_json,
    compact_json,
)
from app.modules.suites.domains.suite_context.entity import SuiteContext
from app.modules.suites.domains.suite_context_story.entity import SuiteContextStory


def build_suite_context_tool_result(suite_context: SuiteContext) -> CallToolResult:
    cases = [case for story in suite_context.stories for case in story.cases]
    used_keys = sorted({key for case in cases for key in case.data_keys})
    entries_by_key: dict[str, list[DataEntry]] = {}
    for entry in suite_context.data_entries:
        entries_by_key.setdefault(entry.key, []).append(entry)
    content = compact_json(
        {
            "suite": compact_json(
                {
                    "id": str(suite_context.suite.id),
                    "name": suite_context.suite.name,
                    "description": suite_context.suite.description,
                }
            ),
            "case_count": len(cases),
            "stories": [build_story_json(story) for story in suite_context.stories],
            "skipped_cases": [
                {
                    "code": skipped.code,
                    "title": skipped.title,
                    "story_key": skipped.story_jira_key,
                    "reason": skipped.reason.value,
                }
                for skipped in suite_context.skipped_cases
            ],
            "data": [
                build_context_data_json(key, entries_by_key[key], suite_context.environments)
                for key in used_keys
                if key in entries_by_key
            ],
            "missing_data_keys": [key for key in used_keys if key not in entries_by_key],
            "files": [
                compact_json({"case": case.code, "key": file.key, "file_name": file.file_name})
                for case in cases
                for file in case.files
            ],
            "environments": [build_context_environment_json(environment) for environment in suite_context.environments],
        }
    )
    return build_compact_tool_result(content)


def build_story_json(story: SuiteContextStory) -> JsonValue:
    active_codes_by_id: Mapping[UUID, str] = {
        criterion.id: criterion.code for criterion in story.criteria if not criterion.is_removed
    }
    return compact_json(
        {
            "key": story.story.jira_key,
            "title": story.story.title,
            "test_status": story.story.test_status.value,
            "jira_status": story.story.jira_status,
            "criteria": [
                compact_json({"code": criterion.code, "text": criterion.text})
                for criterion in story.criteria
                if not criterion.is_removed
            ],
            "cases": [build_context_case_json(case, active_codes_by_id) for case in story.cases],
        }
    )

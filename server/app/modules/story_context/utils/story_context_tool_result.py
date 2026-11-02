import json
from collections.abc import Mapping
from uuid import UUID

from mcp_types import CallToolResult, TextContent
from pydantic import JsonValue

from app.modules.story_context.domains.context_case.entity import ContextCase
from app.modules.story_context.domains.context_environment.entity import ContextEnvironment
from app.modules.story_context.domains.data_entry.entity import DataEntry
from app.modules.story_context.domains.resolved_data.entity import ResolvedData
from app.modules.story_context.domains.story_context.entity import StoryContext
from app.modules.story_context.domains.test_file_link.entity import TestFileLink
from app.modules.story_context.utils.data_reference import build_data_reference
from app.modules.test_data import DataItemKind


def build_story_context_tool_result(story_context: StoryContext) -> CallToolResult:
    active_codes_by_id = {
        criterion.id: criterion.code for criterion in story_context.criteria if not criterion.is_removed
    }
    used_keys = sorted({key for case in story_context.cases for key in case.data_keys})
    entries_by_key: dict[str, list[DataEntry]] = {}
    for entry in story_context.data_entries:
        entries_by_key.setdefault(entry.key, []).append(entry)
    content = compact_json(
        {
            "story": compact_json(
                {
                    "key": story_context.story.jira_key,
                    "title": story_context.story.title,
                    "test_status": story_context.story.test_status.value,
                    "jira_status": story_context.story.jira_status,
                }
            ),
            "criteria": [
                compact_json({"code": criterion.code, "text": criterion.text})
                for criterion in story_context.criteria
                if not criterion.is_removed
            ],
            "cases": [build_context_case_json(case, active_codes_by_id) for case in story_context.cases],
            "other_case_count": story_context.other_case_count,
            "data": [
                build_context_data_json(key, entries_by_key[key], story_context.environments)
                for key in used_keys
                if key in entries_by_key
            ],
            "missing_data_keys": [key for key in used_keys if key not in entries_by_key],
            "files": [
                compact_json({"case": case.code, "key": file.key, "file_name": file.file_name})
                for case in story_context.cases
                for file in case.files
            ],
            "environments": [build_context_environment_json(environment) for environment in story_context.environments],
        }
    )
    return build_compact_tool_result(content)


def build_resolved_data_tool_result(resolved_data: ResolvedData) -> CallToolResult:
    content = compact_json({"values": dict(resolved_data.values), "unknown_keys": list(resolved_data.unknown_keys)})
    return build_compact_tool_result(content)


def build_test_file_tool_result(test_file_link: TestFileLink) -> CallToolResult:
    content: dict[str, JsonValue] = {"file_name": test_file_link.file_name, "url": test_file_link.url}
    return build_compact_tool_result(content)


def build_context_case_json(case: ContextCase, active_codes_by_id: Mapping[UUID, str]) -> JsonValue:
    return compact_json(
        {
            "id": str(case.id),
            "code": case.code,
            "title": case.title,
            "priority": case.priority.value,
            "version": case.version_number,
            "criteria": [
                active_codes_by_id[criterion_id]
                for criterion_id in case.criterion_ids
                if criterion_id in active_codes_by_id
            ],
            "business_value": case.business_value,
            "preconditions": case.preconditions,
            "steps": [
                compact_json({"order": step.order, "action": step.action, "expected": step.expected})
                for step in case.steps
            ],
            "data_keys": list(case.data_keys),
            "file_keys": [file.key for file in case.files],
            "labels": list(case.labels),
            "parameters": list(case.parameters),
            "data_rows": [dict(row) for row in case.data_rows],
        }
    )


def build_context_data_json(key: str, entries: list[DataEntry], environments: list[ContextEnvironment]) -> JsonValue:
    description = next((entry.description for entry in entries if entry.description), None)
    if any(entry.is_secret for entry in entries):
        return compact_json(
            {
                "key": key,
                "kind": DataItemKind.SECRET.value,
                "value": build_data_reference(key),
                "description": description,
            }
        )
    project_entry = next((entry for entry in entries if entry.environment_id is None), None)
    entries_by_environment_id = {entry.environment_id: entry for entry in entries if entry.environment_id is not None}
    by_environment: dict[str, JsonValue] = {
        environment.name: entries_by_environment_id[environment.id].value
        for environment in environments
        if environment.id in entries_by_environment_id
    }
    return compact_json(
        {
            "key": key,
            "kind": (project_entry or entries[0]).kind.value,
            "value": None if project_entry is None else project_entry.value,
            "by_environment": compact_json(by_environment),
            "description": description,
        }
    )


def build_context_environment_json(environment: ContextEnvironment) -> JsonValue:
    return compact_json(
        {
            "name": environment.name,
            "base_url": environment.base_url,
            "health_check_url": environment.health_check_url,
            "is_default": environment.is_default,
        }
    )


def compact_json(content: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    return {key: value for key, value in content.items() if not _is_empty(value)}


def _is_empty(value: JsonValue) -> bool:
    return value is None or value is False or value in ("", [], {})


def build_compact_tool_result(content: Mapping[str, JsonValue]) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content, separators=(",", ":")))])

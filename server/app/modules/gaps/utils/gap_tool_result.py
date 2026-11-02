import json
from collections.abc import Mapping

from mcp_types import CallToolResult, TextContent
from pydantic import JsonValue

from app.modules.gaps.domains.answered_gap.entity import AnsweredGap
from app.modules.gaps.domains.gap_case.entity import GapCase
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.domains.my_gap.entity import MyGap
from app.modules.gaps.domains.my_gaps.entity import MyGaps
from app.modules.gaps.domains.raised_gaps.entity import RaisedGaps
from app.modules.users import UserStatus


def build_raised_gaps_tool_result(raised_gaps: RaisedGaps) -> CallToolResult:
    content = {
        "gap_ids": [str(view.gap.id) for view in raised_gaps.gaps],
        "open_gap_count": raised_gaps.open_gap_count,
        "is_ready": raised_gaps.is_ready,
    }
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])


def build_open_gaps_tool_result(open_gaps: RaisedGaps) -> CallToolResult:
    content = {
        "open_gap_count": open_gaps.open_gap_count,
        "is_ready": open_gaps.is_ready,
        "gaps": [
            {
                "id": str(view.gap.id),
                "type": view.gap.type.value,
                "severity": view.gap.severity.value,
                "target_type": view.gap.target_type.value,
                "target_ref": view.target_ref,
                "question": view.gap.question,
                **_build_assignee(view),
            }
            for view in open_gaps.gaps
        ],
    }
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])


def build_my_gaps_tool_result(my_gaps: MyGaps) -> CallToolResult:
    content: dict[str, JsonValue] = {
        "gap_count": my_gaps.gap_count,
        "gaps": [_build_my_gap(my_gap) for my_gap in my_gaps.gaps],
        "stories": [
            {
                "key": story.jira_key,
                "title": story.title,
                "open_gap_count": story.open_gap_count,
                "is_ready": story.is_ready,
            }
            for story in my_gaps.stories
        ],
        "assignees": [
            {"user_id": str(assignee.user_id), "name": assignee.name, "role": assignee.role.value}
            for assignee in my_gaps.assignees
        ],
    }
    if my_gaps.test_data_url is not None:
        content["test_data_url"] = my_gaps.test_data_url
    return _build_tool_result(content)


def build_answered_gap_tool_result(answered_gap: AnsweredGap) -> CallToolResult:
    content: dict[str, JsonValue] = {
        "status": answered_gap.view.gap.status.value,
        "open_gap_count": answered_gap.open_gap_count,
        "is_ready": answered_gap.is_ready,
    }
    return _build_tool_result(content)


def build_reassigned_gap_tool_result(view: GapView) -> CallToolResult:
    return _build_tool_result(_build_assignee(view))


def _build_assignee(view: GapView) -> dict[str, JsonValue]:
    return _compact(
        {
            "assignee_name": view.assignee_name,
            "assignee_role": None if view.gap.assignee_role is None else view.gap.assignee_role.value,
            "is_assignee_deactivated": True if view.assignee_status is UserStatus.DEACTIVATED else None,
        }
    )


def _build_my_gap(my_gap: MyGap) -> JsonValue:
    gap = my_gap.view.gap
    return _compact(
        {
            "id": str(gap.id),
            "story_key": my_gap.view.story_jira_key,
            "type": gap.type.value,
            "severity": gap.severity.value,
            "data_scope": None if gap.data_scope is None else gap.data_scope.value,
            "question": gap.question,
            "is_assigned_to_me": gap.assignee_id is not None,
            "raised_by_name": my_gap.view.raised_by_name,
            "target": _compact(
                {
                    "type": gap.target_type.value,
                    "ref": my_gap.view.target_ref,
                    "text": my_gap.criterion_text,
                    "case": None if my_gap.case is None else _build_case(my_gap.case),
                }
            ),
            "similar_answers": [
                {
                    "story_key": similar_answer.story_jira_key,
                    "question": similar_answer.question,
                    "answer": similar_answer.answer,
                }
                for similar_answer in my_gap.similar_answers
            ],
        }
    )


def _build_case(case: GapCase) -> JsonValue:
    return _compact(
        {
            "title": case.title,
            "version": case.version_number,
            "preconditions": case.preconditions,
            "steps": [
                _compact(
                    {
                        "order": step.order,
                        "action": step.action,
                        "expected": step.expected,
                        "shared_step_key": step.shared_step_key,
                    }
                )
                for step in case.steps
            ],
        }
    )


def _compact(content: Mapping[str, JsonValue]) -> dict[str, JsonValue]:
    return {key: value for key, value in content.items() if value is not None and value not in ("", [], {})}


def _build_tool_result(content: Mapping[str, JsonValue]) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content, separators=(",", ":")))])

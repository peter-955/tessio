import json
from collections.abc import Mapping
from uuid import UUID

from mcp_types import CallToolResult, TextContent

from app.modules.runs.domains.failed_cases.entity import FailedCases
from app.modules.runs.domains.finished_run.entity import FinishedRun
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.runs.domains.started_run.entity import StartedRun


def build_started_run_tool_result(started_run: StartedRun) -> CallToolResult:
    is_suite_run = started_run.run.test_suite_id is not None
    content: dict[str, object] = {
        "run_id": str(started_run.run.id),
        "environment": started_run.environment.name,
        "base_url": started_run.environment.base_url,
        "health_check_url": started_run.environment.health_check_url,
        "cases": [build_started_case(case, is_suite_run) for case in started_run.cases],
    }
    if is_suite_run:
        content["suite"] = started_run.suite_name
        if started_run.skipped_cases:
            content["skipped_cases"] = [build_skipped_case(case) for case in started_run.skipped_cases]
    return build_json_tool_result(content)


def build_started_case(case: RunCaseView, is_suite_run: bool) -> dict[str, object]:
    content: dict[str, object] = {
        "case_id": str(case.test_case_id),
        "code": case.code,
        "title": case.version.title,
        "version": case.version.number,
        "preconditions": case.version.preconditions,
        "steps": [
            {"order": step.order, "action": step.action, "expected": step.expected}
            for step in sorted(case.version.steps, key=lambda version_step: version_step.order)
        ],
    }
    if case.version.parameters:
        content["parameters"] = case.version.parameters
        content["data_rows"] = case.version.data_rows
    if is_suite_run:
        content["story_key"] = case.story_jira_key
    return content


def build_skipped_case(case: SkippedRunCase) -> dict[str, object]:
    return {"code": case.code, "title": case.title, "story_key": case.story_jira_key, "reason": case.reason.value}


def build_case_result_tool_result(case_result_id: UUID) -> CallToolResult:
    return build_json_tool_result({"case_result_id": str(case_result_id)})


def build_finished_run_tool_result(finished_run: FinishedRun) -> CallToolResult:
    content = {
        "status": finished_run.run.status.value,
        "missing_screenshots": [build_missing_screenshot(missing) for missing in finished_run.missing_screenshots],
    }
    return build_json_tool_result(content)


def build_missing_screenshot(missing: MissingScreenshot) -> dict[str, object]:
    content: dict[str, object] = {"code": missing.code, "step_order": missing.step_order}
    if missing.iteration is not None:
        content["iteration"] = missing.iteration
    return content


def build_failed_cases_tool_result(failed_cases: FailedCases) -> CallToolResult:
    if failed_cases.run.test_suite_id is None:
        content: dict[str, object] = {
            "run_id": str(failed_cases.run.id),
            "run_status": failed_cases.run.status.value,
            "story_key": failed_cases.story_jira_key,
            "environment": failed_cases.environment_name,
            "cases": [
                {"case_id": str(case.test_case_id), "code": case.code, "title": case.title, "status": case.status.value}
                for case in failed_cases.cases
            ],
        }
        return build_json_tool_result(content)
    content = {
        "run_id": str(failed_cases.run.id),
        "run_status": failed_cases.run.status.value,
        "suite": failed_cases.suite_name,
        "environment": failed_cases.environment_name,
        "cases": [
            {
                "case_id": str(case.test_case_id),
                "code": case.code,
                "title": case.title,
                "status": case.status.value,
                "story_key": case.story_jira_key,
            }
            for case in failed_cases.cases
        ],
    }
    return build_json_tool_result(content)


def build_json_tool_result(content: Mapping[str, object]) -> CallToolResult:
    return CallToolResult(content=[TextContent(type="text", text=json.dumps(content))])

import argparse
import asyncio
import json
import re
import sys

from pydantic import JsonValue

from app.config import get_settings
from app.container import Container
from app.modules.jira import JiraIssue
from app.modules.stories import collect_node_types, parse_acceptance_criteria
from app.modules.stories.typing.constants import CRITERION_CODE_PREFIX, EPIC_ISSUE_TYPE_NAME
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode

ISSUE_KEY_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+-[0-9]+$")
ISSUE_JQL_TEMPLATE = 'key = "{issue_key}"'
PROBE_FAILURE_EXIT_CODE = 1


def parse_issue_key(value: str) -> str:
    if ISSUE_KEY_PATTERN.fullmatch(value) is None:
        raise argparse.ArgumentTypeError(f"{value!r} is not a Jira issue key such as SHOP-123.")
    return value


def build_probe_report(issue: JiraIssue, is_including_description: bool) -> dict[str, JsonValue]:
    parsed = parse_acceptance_criteria(issue.description)
    criteria: list[JsonValue] = [
        {"code": f"{CRITERION_CODE_PREFIX}{position}", "text": text}
        for position, text in enumerate(parsed.texts, start=1)
    ]
    node_types: list[JsonValue] = []
    node_types.extend(sorted(collect_node_types(issue.description)))
    report: dict[str, JsonValue] = {
        "key": issue.key,
        "issueType": issue.issue_type_name,
        "isSubtask": issue.is_subtask,
        "isEpic": issue.issue_type_name.casefold() == EPIC_ISSUE_TYPE_NAME,
        "status": issue.status_name,
        "summary": issue.summary,
        "criteriaSource": parsed.source.value,
        "criteria": criteria,
        "nodeTypes": node_types,
    }
    if is_including_description:
        report["description"] = issue.description
    return report


async def fetch_issue(issue_key: str) -> JiraIssue | None:
    container = Container(get_settings())
    try:
        credentials = await container.load_jira_credentials.execute()
        issues = await container.jira_client.search_issues(credentials, ISSUE_JQL_TEMPLATE.format(issue_key=issue_key))
    finally:
        await container.close()
    return next((issue for issue in issues if issue.key == issue_key), None)


async def probe_issue(issue_key: str, is_including_description: bool) -> int:
    try:
        issue = await fetch_issue(issue_key)
    except TessioError as error:
        sys.stderr.write(f"{error.code.value}: {error.message}\n")
        return PROBE_FAILURE_EXIT_CODE
    if issue is None:
        sys.stderr.write(f"{ErrorCode.NOT_FOUND.value}: Jira issue {issue_key} not found.\n")
        return PROBE_FAILURE_EXIT_CODE
    report = build_probe_report(issue, is_including_description)
    sys.stdout.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch one Jira issue and print how Tessio parses its acceptance criteria."
    )
    parser.add_argument("--issue", required=True, type=parse_issue_key, help="Jira issue key, for example SHOP-123.")
    parser.add_argument("--raw", action="store_true", help="Also print the raw ADF description.")
    arguments = parser.parse_args()
    sys.exit(asyncio.run(probe_issue(arguments.issue, arguments.raw)))


if __name__ == "__main__":
    main()

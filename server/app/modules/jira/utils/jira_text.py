import re

from app.modules.jira.typing.constants import (
    JIRA_ISSUE_KEY_PATTERN,
    JIRA_ISSUE_KEYS_JQL_TEMPLATE,
    JIRA_SUMMARY_MAX_LENGTH,
)


def clean_jira_summary(summary: str) -> str:
    single_line = " ".join(summary.split())
    if len(single_line) <= JIRA_SUMMARY_MAX_LENGTH:
        return single_line
    return single_line[: JIRA_SUMMARY_MAX_LENGTH - 1].rstrip() + "…"


def build_issue_keys_jql(issue_keys: list[str]) -> str:
    return JIRA_ISSUE_KEYS_JQL_TEMPLATE.format(issue_keys=", ".join(f'"{issue_key}"' for issue_key in issue_keys))


def is_valid_issue_key(issue_key: str) -> bool:
    return re.fullmatch(JIRA_ISSUE_KEY_PATTERN, issue_key) is not None

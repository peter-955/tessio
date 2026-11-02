from datetime import UTC, datetime
from uuid import uuid7

import pytest

from app.modules.jira import (
    JiraCommentJob,
    JiraCommentTrigger,
    JiraPermission,
    build_jira_comment_job_data,
    parse_jira_comment_job_data,
)
from app.modules.jira.utils.jira_post_results import is_posting_results
from app.modules.jira.utils.jira_text import build_issue_keys_jql, is_valid_issue_key
from app.modules.jira.utils.jira_write_access import build_jira_write_access
from app.modules.projects import JiraPostResults

NOW = datetime(2026, 11, 2, 9, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("setting", "trigger", "expected"),
    [
        (JiraPostResults.OFF, JiraCommentTrigger.SIGN_OFF, False),
        (JiraPostResults.OFF, JiraCommentTrigger.RUN_FINISHED, False),
        (JiraPostResults.ON_SIGN_OFF, JiraCommentTrigger.SIGN_OFF, True),
        (JiraPostResults.ON_SIGN_OFF, JiraCommentTrigger.RUN_FINISHED, False),
        (JiraPostResults.EVERY_RUN, JiraCommentTrigger.SIGN_OFF, False),
        (JiraPostResults.EVERY_RUN, JiraCommentTrigger.RUN_FINISHED, True),
    ],
)
def test_the_project_setting_decides_when_results_are_posted(
    setting: JiraPostResults, trigger: JiraCommentTrigger, expected: bool
) -> None:
    assert is_posting_results(setting, trigger) is expected


def test_write_access_names_each_missing_permission_in_a_fixed_order() -> None:
    write_access = build_jira_write_access({JiraPermission.LINK_ISSUES, JiraPermission.ADD_COMMENTS}, NOW)

    assert write_access.can_create_issues is True
    assert write_access.can_comment is False
    assert write_access.missing_permissions == [JiraPermission.ADD_COMMENTS, JiraPermission.LINK_ISSUES]
    assert write_access.checked_at == NOW
    assert write_access.is_comment_refused is True
    assert write_access.is_create_refused is False


def test_full_write_access_has_nothing_missing() -> None:
    write_access = build_jira_write_access(set(), NOW)

    assert write_access.can_create_issues is True
    assert write_access.can_comment is True
    assert write_access.missing_permissions == []


def test_comment_job_data_round_trips_and_bad_data_is_refused() -> None:
    job = JiraCommentJob(trigger=JiraCommentTrigger.RUN_FINISHED, project_id=uuid7(), story_id=uuid7(), run_id=uuid7())

    assert parse_jira_comment_job_data(build_jira_comment_job_data(job)) == job
    assert parse_jira_comment_job_data({"trigger": "later", "projectId": str(uuid7()), "storyId": str(uuid7())}) is None
    assert parse_jira_comment_job_data({"trigger": "sign_off", "projectId": "nope", "storyId": str(uuid7())}) is None


def test_issue_keys_are_quoted_in_one_jql_search() -> None:
    assert build_issue_keys_jql(["PAY-1", "PAY-12"]) == 'key in ("PAY-1", "PAY-12") ORDER BY key ASC'
    assert is_valid_issue_key("PAY-12") is True
    assert is_valid_issue_key('PAY-1") OR (1=1') is False

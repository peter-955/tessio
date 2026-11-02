from datetime import datetime

from app.modules.failures.domains.failure.entity import Failure
from app.modules.failures.typing.constants import JIRA_ISSUE_PENDING_TIMEOUT


def is_jira_issue_pending(failure: Failure, now: datetime) -> bool:
    requested_at = failure.jira_issue_requested_at
    return (
        failure.jira_issue_key is None and requested_at is not None and requested_at > now - JIRA_ISSUE_PENDING_TIMEOUT
    )


def is_jira_issue_request_blocked(failure: Failure, now: datetime) -> bool:
    if failure.has_jira_issue:
        return True
    return is_jira_issue_pending(failure, now) and failure.jira_issue_error_code is None

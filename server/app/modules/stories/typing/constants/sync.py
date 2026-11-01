from collections.abc import Mapping
from datetime import timedelta

from app.modules.jira import JiraSprintState

JIRA_SYNC_JOB_ID_TEMPLATE = "jira-sync:{project_id}"
CLOSED_SPRINT_SYNC_WINDOW = timedelta(days=30)
SYNC_STALE_AFTER = timedelta(minutes=15)
JIRA_BROWSE_URL_TEMPLATE = "{site_url}/browse/{jira_key}"
EPIC_ISSUE_TYPE_NAME = "epic"
SPRINT_ISSUES_JQL_TEMPLATE = (
    'project = "{jira_project_key}" AND sprint = {jira_sprint_id} '
    "AND issuetype not in subTaskIssueTypes() ORDER BY Rank ASC"
)
JIRA_SPRINT_STATE_PRECEDENCE: Mapping[JiraSprintState, int] = {
    JiraSprintState.CLOSED: 0,
    JiraSprintState.FUTURE: 1,
    JiraSprintState.ACTIVE: 2,
}

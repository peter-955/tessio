from app.modules.stories.typing.constants import SPRINT_ISSUES_JQL_TEMPLATE


def build_sprint_issues_jql(jira_project_key: str, jira_sprint_id: int) -> str:
    return SPRINT_ISSUES_JQL_TEMPLATE.format(jira_project_key=jira_project_key, jira_sprint_id=jira_sprint_id)

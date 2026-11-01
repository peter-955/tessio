from app.modules.jira import JiraIssue
from app.shared.common import Entity


class FetchedStory(Entity):
    issue: JiraIssue
    jira_sprint_id: int

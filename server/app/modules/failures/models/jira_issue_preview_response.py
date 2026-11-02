from app.shared.common import WireModel


class JiraIssuePreviewResponse(WireModel):
    jira_project_key: str
    issue_type_name: str
    summary: str
    description: str
    linked_story_jira_key: str | None
    has_screenshot: bool

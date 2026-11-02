from app.modules.failures.domains.jira_bug_content.entity import JiraBugContent
from app.modules.failures.models.jira_issue_preview_response import JiraIssuePreviewResponse
from app.modules.jira import render_jira_document_text


def build_jira_issue_preview_response(content: JiraBugContent) -> JiraIssuePreviewResponse:
    return JiraIssuePreviewResponse(
        jira_project_key=content.jira_project_key,
        issue_type_name=content.issue_type_name,
        summary=content.summary,
        description=render_jira_document_text(content.description),
        linked_story_jira_key=content.linked_story_jira_key,
        has_screenshot=content.screenshot_file_id is not None,
    )

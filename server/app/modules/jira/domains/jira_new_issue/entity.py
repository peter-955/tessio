from app.modules.jira.domains.jira_document_block.entity import JiraDocumentBlock
from app.shared.common import Entity


class JiraNewIssue(Entity):
    jira_project_key: str
    issue_type_name: str
    summary: str
    description: list[JiraDocumentBlock]

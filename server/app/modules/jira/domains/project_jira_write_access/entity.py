from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.shared.common import Entity


class ProjectJiraWriteAccess(Entity):
    is_project_linked: bool
    is_connection_configured: bool
    write_access: JiraWriteAccess | None

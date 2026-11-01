from enum import StrEnum


class WorkspaceCapability(StrEnum):
    USER_MANAGE = "user.manage"
    PROJECT_CREATE = "project.create"
    PROJECT_ARCHIVE = "project.archive"
    PROJECT_VIEW_ALL = "project.view_all"
    JIRA_CONFIGURE = "jira.configure"
    USER_ACCESS_VIEW = "user_access.view"
    WORKSPACE_ROLE_MANAGE = "workspace_role.manage"

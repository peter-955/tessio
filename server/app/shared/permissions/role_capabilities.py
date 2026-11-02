from collections.abc import Mapping

from app.shared.permissions.capability import Capability
from app.shared.permissions.project_role import ProjectRole
from app.shared.permissions.workspace_capability import WorkspaceCapability
from app.shared.permissions.workspace_role import WorkspaceRole

VIEW_CAPABILITIES = frozenset(
    {
        Capability.PROJECT_VIEW,
        Capability.SPRINT_VIEW,
        Capability.STORY_VIEW,
        Capability.TEST_CASE_VIEW,
        Capability.TEST_DATA_VIEW,
        Capability.GAP_VIEW,
        Capability.RUN_VIEW,
        Capability.REPORT_VIEW,
        Capability.FAILURE_VIEW,
        Capability.FILE_DOWNLOAD,
    }
)

READ_CAPABILITIES = VIEW_CAPABILITIES | {Capability.SECRET_REVEAL}

MEMBER_BASE_CAPABILITIES = VIEW_CAPABILITIES | {Capability.API_TOKEN_CREATE}

GAP_CAPABILITIES = frozenset({Capability.GAP_RAISE, Capability.GAP_ANSWER, Capability.GAP_REASSIGN})

ANALYST_CAPABILITIES = MEMBER_BASE_CAPABILITIES | GAP_CAPABILITIES | {Capability.JIRA_SYNC, Capability.STORY_EDIT}

PROJECT_ROLE_CAPABILITIES: Mapping[ProjectRole, frozenset[Capability]] = {
    ProjectRole.ADMIN: frozenset(Capability),
    ProjectRole.PM: ANALYST_CAPABILITIES | {Capability.PLAN_EDIT},
    ProjectRole.BA: ANALYST_CAPABILITIES,
    ProjectRole.QC: MEMBER_BASE_CAPABILITIES
    | GAP_CAPABILITIES
    | {
        Capability.STORY_SIGN_OFF,
        Capability.STORY_EDIT,
        Capability.TEST_CASE_EDIT,
        Capability.TEST_CASE_QUARANTINE,
        Capability.SUITE_EDIT,
        Capability.PLAN_EDIT,
        Capability.PLAN_SIGN_OFF,
        Capability.ENVIRONMENT_MANAGE,
        Capability.TEST_DATA_EDIT,
        Capability.SECRET_EDIT,
        Capability.SECRET_REVEAL,
        Capability.SECRET_USE_IN_RUN,
        Capability.RUN_START,
        Capability.RUN_RECORD_MANUAL,
        Capability.FAILURE_ASSIGN,
        Capability.FAILURE_VERIFY,
        Capability.FAILURE_CREATE_JIRA_ISSUE,
    },
    ProjectRole.DEV: MEMBER_BASE_CAPABILITIES
    | GAP_CAPABILITIES
    | {
        Capability.STORY_MARK_READY_FOR_TEST,
        Capability.ENVIRONMENT_MANAGE,
        Capability.TEST_DATA_EDIT,
        Capability.SECRET_USE_IN_RUN,
        Capability.RUN_START,
        Capability.FAILURE_ASSIGN,
        Capability.FAILURE_MARK_FIXED,
        Capability.FAILURE_CREATE_JIRA_ISSUE,
    },
    ProjectRole.VIEWER: MEMBER_BASE_CAPABILITIES,
}

WORKSPACE_ROLE_CAPABILITIES: Mapping[WorkspaceRole, frozenset[WorkspaceCapability]] = {
    WorkspaceRole.OWNER: frozenset(WorkspaceCapability),
    WorkspaceRole.ADMIN: frozenset(WorkspaceCapability) - {WorkspaceCapability.WORKSPACE_ROLE_MANAGE},
    WorkspaceRole.MEMBER: frozenset(),
}

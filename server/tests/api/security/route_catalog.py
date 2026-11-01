from uuid import uuid7

from app.shared.permissions import Capability, WorkspaceCapability
from tests.api.security.route_access import RouteAccess
from tests.api.security.secured_route import SecuredRoute
from tests.support.sign_in_steps import PASSWORD

PUBLIC = RouteAccess.PUBLIC
SESSION = RouteAccess.SESSION
WORKSPACE = RouteAccess.WORKSPACE
PROJECT_READ = RouteAccess.PROJECT_READ
PROJECT_WRITE = RouteAccess.PROJECT_WRITE
API_TOKEN = RouteAccess.API_TOKEN
UNKNOWN_FILE_ID = str(uuid7())
PROJECT = "/api/projects/{project_key}"


def secured(
    method: str,
    path: str,
    access: RouteAccess,
    capability: Capability | WorkspaceCapability | None = None,
    body: dict[str, object] | None = None,
) -> SecuredRoute:
    return SecuredRoute(method=method, path=path, access=access, capability=capability, body=body)


SECURED_ROUTES = [
    secured("GET", "/api/health", PUBLIC),
    secured("GET", "/api/health/ready", PUBLIC),
    secured("POST", "/api/auth/sign-in", PUBLIC, body={"email": "nobody@tessio.test", "password": PASSWORD}),
    secured("POST", "/api/auth/invites/{token}", PUBLIC, body={"password": PASSWORD}),
    secured("POST", "/api/auth/password/forgot", PUBLIC, body={"email": "nobody@tessio.test"}),
    secured("POST", "/api/auth/password/reset", PUBLIC, body={"token": "unknown", "password": PASSWORD}),
    secured("POST", "/api/auth/two-factor/setup", SESSION),
    secured("POST", "/api/auth/two-factor/confirm", SESSION, body={"code": "000000"}),
    secured("POST", "/api/auth/two-factor", SESSION, body={"code": "000000"}),
    secured("GET", "/api/auth/me", SESSION),
    secured("POST", "/api/auth/sign-out", SESSION),
    secured("POST", "/api/auth/sign-out-all", SESSION),
    secured("GET", "/api/users", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured(
        "POST", "/api/users", WORKSPACE, WorkspaceCapability.USER_MANAGE, {"email": "new@tessio.test", "name": "New"}
    ),
    secured("GET", "/api/users/{user_id}", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured("POST", "/api/users/{user_id}/resend-invite", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured("POST", "/api/users/{user_id}/deactivate", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured("POST", "/api/users/{user_id}/reactivate", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured("POST", "/api/users/{user_id}/reset-two-factor", WORKSPACE, WorkspaceCapability.USER_MANAGE),
    secured(
        "PUT",
        "/api/users/{user_id}/workspace-role",
        WORKSPACE,
        WorkspaceCapability.USER_MANAGE,
        {"workspaceRole": "member"},
    ),
    secured("GET", "/api/users/{user_id}/access", WORKSPACE, WorkspaceCapability.USER_ACCESS_VIEW),
    secured("GET", "/api/users/{user_id}/avatar", SESSION),
    secured("PATCH", "/api/me", SESSION, body={}),
    secured("PUT", "/api/me/password", SESSION, body={"currentPassword": PASSWORD, "newPassword": PASSWORD}),
    secured("POST", "/api/me/recovery-codes", SESSION, body={"password": PASSWORD}),
    secured("POST", "/api/me/two-factor/reset", SESSION, body={"password": PASSWORD}),
    secured("GET", "/api/me/api-tokens", SESSION),
    secured(
        "POST",
        "/api/me/api-tokens",
        SESSION,
        Capability.API_TOKEN_CREATE,
        {"name": "Claude Code", "projectKey": "PUNKNOWN"},
    ),
    secured("DELETE", "/api/me/api-tokens/{token_id}", SESSION),
    secured(
        "POST", "/api/me/avatar-upload", SESSION, body={"fileName": "me.png", "contentType": "image/png", "size": 10}
    ),
    secured("POST", "/api/me/avatar-upload/{file_id}/complete", SESSION),
    secured("GET", "/api/events", SESSION),
    secured("GET", "/api/notifications", SESSION),
    secured("GET", "/api/notifications/unread-count", SESSION),
    secured("PUT", "/api/notifications/read-all", SESSION),
    secured("PUT", "/api/notifications/{notification_id}/read", SESSION),
    secured("GET", "/api/gaps/inbox", SESSION),
    secured("GET", "/api/projects", SESSION),
    secured(
        "POST",
        "/api/projects",
        WORKSPACE,
        WorkspaceCapability.PROJECT_CREATE,
        {"key": "PNEW", "name": "New", "jiraProjectKey": "JNEW", "jiraBoardId": 1},
    ),
    secured("GET", "/api/workspace/jira", WORKSPACE, WorkspaceCapability.JIRA_CONFIGURE),
    secured(
        "PUT",
        "/api/workspace/jira",
        WORKSPACE,
        WorkspaceCapability.JIRA_CONFIGURE,
        {"siteUrl": "https://team.atlassian.net", "accountEmail": "jira@tessio.test"},
    ),
    secured("GET", "/api/workspace/jira/projects", WORKSPACE, WorkspaceCapability.PROJECT_CREATE),
    secured("GET", "/api/workspace/jira/boards", WORKSPACE, WorkspaceCapability.PROJECT_CREATE),
    secured("GET", PROJECT, PROJECT_READ, Capability.PROJECT_VIEW),
    secured("PATCH", PROJECT, PROJECT_WRITE, Capability.PROJECT_EDIT, {}),
    secured("POST", f"{PROJECT}/archive", PROJECT_WRITE, WorkspaceCapability.PROJECT_ARCHIVE),
    secured("POST", f"{PROJECT}/unarchive", PROJECT_WRITE, WorkspaceCapability.PROJECT_ARCHIVE),
    secured("GET", f"{PROJECT}/members", PROJECT_READ, Capability.PROJECT_VIEW),
    secured("GET", f"{PROJECT}/members/candidates", PROJECT_WRITE, Capability.MEMBER_MANAGE),
    secured("PUT", f"{PROJECT}/members/{{user_id}}", PROJECT_WRITE, Capability.MEMBER_MANAGE, {"role": "qc"}),
    secured("DELETE", f"{PROJECT}/members/{{user_id}}", PROJECT_WRITE, Capability.MEMBER_MANAGE),
    secured(
        "POST",
        f"{PROJECT}/uploads",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"kind": "test_file", "fileName": "data.txt", "contentType": "text/plain", "size": 10},
    ),
    secured("POST", f"{PROJECT}/uploads/{{file_id}}/complete", PROJECT_WRITE, Capability.TEST_CASE_EDIT),
    secured("GET", f"{PROJECT}/files/{{file_id}}", PROJECT_READ, Capability.FILE_DOWNLOAD),
    secured("GET", f"{PROJECT}/environments", PROJECT_READ, Capability.PROJECT_VIEW),
    secured(
        "POST",
        f"{PROJECT}/environments",
        PROJECT_WRITE,
        Capability.ENVIRONMENT_MANAGE,
        {"name": "Staging", "baseUrl": "https://staging.shop.test"},
    ),
    secured(
        "PUT",
        f"{PROJECT}/environments/{{environment_id}}",
        PROJECT_WRITE,
        Capability.ENVIRONMENT_MANAGE,
        {"name": "Staging", "baseUrl": "https://staging.shop.test"},
    ),
    secured("POST", f"{PROJECT}/environments/{{environment_id}}/archive", PROJECT_WRITE, Capability.ENVIRONMENT_MANAGE),
    secured(
        "POST", f"{PROJECT}/environments/{{environment_id}}/unarchive", PROJECT_WRITE, Capability.ENVIRONMENT_MANAGE
    ),
    secured("DELETE", f"{PROJECT}/environments/{{environment_id}}", PROJECT_WRITE, Capability.ENVIRONMENT_MANAGE),
    secured("GET", f"{PROJECT}/test-data", PROJECT_READ, Capability.TEST_DATA_VIEW),
    secured("GET", f"{PROJECT}/test-data/effective", PROJECT_READ, Capability.TEST_DATA_VIEW),
    secured(
        "POST",
        f"{PROJECT}/test-data/import/preview",
        PROJECT_WRITE,
        Capability.TEST_DATA_EDIT,
        {"fileId": UNKNOWN_FILE_ID},
    ),
    secured(
        "POST",
        f"{PROJECT}/test-data/import/commit",
        PROJECT_WRITE,
        Capability.TEST_DATA_EDIT,
        {"fileId": UNKNOWN_FILE_ID, "items": [{"key": "BASE_URL", "kind": "endpoint"}]},
    ),
    secured(
        "POST",
        f"{PROJECT}/test-data",
        PROJECT_WRITE,
        Capability.TEST_DATA_EDIT,
        {"key": "BASE_URL", "kind": "endpoint", "value": "https://shop.test"},
    ),
    secured(
        "PUT",
        f"{PROJECT}/test-data/{{item_id}}",
        PROJECT_WRITE,
        Capability.TEST_DATA_EDIT,
        {"key": "BASE_URL", "kind": "endpoint"},
    ),
    secured("DELETE", f"{PROJECT}/test-data/{{item_id}}", PROJECT_WRITE, Capability.TEST_DATA_EDIT),
    secured("POST", f"{PROJECT}/test-data/{{item_id}}/reveal", PROJECT_WRITE, Capability.SECRET_REVEAL),
    secured("GET", f"{PROJECT}/sprints", PROJECT_READ, Capability.SPRINT_VIEW),
    secured("GET", f"{PROJECT}/sprints/{{sprint_id}}", PROJECT_READ, Capability.SPRINT_VIEW),
    secured("GET", f"{PROJECT}/stories", PROJECT_READ, Capability.STORY_VIEW),
    secured("GET", f"{PROJECT}/stories/{{jira_key}}", PROJECT_READ, Capability.STORY_VIEW),
    secured(
        "PUT",
        f"{PROJECT}/stories/{{jira_key}}/test-status",
        PROJECT_WRITE,
        Capability.STORY_MARK_READY_FOR_TEST,
        {"testStatus": "ready_for_test"},
    ),
    secured("GET", f"{PROJECT}/sync", PROJECT_READ, Capability.SPRINT_VIEW),
    secured("POST", f"{PROJECT}/sync", PROJECT_WRITE, Capability.JIRA_SYNC),
    secured("GET", f"{PROJECT}/test-cases", PROJECT_READ, Capability.TEST_CASE_VIEW),
    secured(
        "POST", f"{PROJECT}/test-cases", PROJECT_WRITE, Capability.TEST_CASE_EDIT, {"storyKey": "X-1", "title": "Pay"}
    ),
    secured("GET", f"{PROJECT}/test-cases/{{case_code}}", PROJECT_READ, Capability.TEST_CASE_VIEW),
    secured(
        "PATCH",
        f"{PROJECT}/test-cases/{{case_code}}",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"baseVersionNumber": 1},
    ),
    secured("GET", f"{PROJECT}/test-cases/{{case_code}}/versions", PROJECT_READ, Capability.TEST_CASE_VIEW),
    secured(
        "PUT",
        f"{PROJECT}/test-cases/{{case_code}}/status",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"status": "ready"},
    ),
    secured("POST", f"{PROJECT}/test-cases/{{case_code}}/review", PROJECT_WRITE, Capability.TEST_CASE_EDIT),
    secured(
        "POST",
        f"{PROJECT}/test-cases/{{case_code}}/files",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"key": "invoice", "fileId": UNKNOWN_FILE_ID, "baseVersionNumber": 1},
    ),
    secured(
        "GET",
        f"{PROJECT}/test-cases/{{case_code}}/files/{{file_key}}/versions",
        PROJECT_READ,
        Capability.TEST_CASE_VIEW,
    ),
    secured(
        "POST",
        f"{PROJECT}/test-case-imports/preview",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"fileId": UNKNOWN_FILE_ID},
    ),
    secured(
        "POST",
        f"{PROJECT}/test-case-imports/commit",
        PROJECT_WRITE,
        Capability.TEST_CASE_EDIT,
        {"fileId": UNKNOWN_FILE_ID, "indexes": [0]},
    ),
    secured("GET", f"{PROJECT}/gaps", PROJECT_READ, Capability.GAP_VIEW),
    secured(
        "POST",
        f"{PROJECT}/stories/{{jira_key}}/gaps",
        PROJECT_WRITE,
        Capability.GAP_RAISE,
        {"type": "missing_ac", "question": "Which currencies?"},
    ),
    secured("GET", f"{PROJECT}/gaps/{{gap_id}}", PROJECT_READ, Capability.GAP_VIEW),
    secured("PUT", f"{PROJECT}/gaps/{{gap_id}}/answer", PROJECT_WRITE, Capability.GAP_ANSWER, {"answer": "EUR."}),
    secured("POST", f"{PROJECT}/gaps/{{gap_id}}/reopen", PROJECT_WRITE, Capability.GAP_RAISE),
    secured(
        "PUT", f"{PROJECT}/gaps/{{gap_id}}/assignee", PROJECT_WRITE, Capability.GAP_REASSIGN, {"assigneeRole": "qc"}
    ),
    secured("GET", f"{PROJECT}/runs", PROJECT_READ, Capability.RUN_VIEW),
    secured("GET", f"{PROJECT}/runs/{{run_id}}", PROJECT_READ, Capability.RUN_VIEW),
    secured("POST", f"{PROJECT}/runs", PROJECT_WRITE, Capability.RUN_START, {"storyKey": "X-1"}),
    secured(
        "PUT",
        f"{PROJECT}/runs/{{run_id}}/cases/{{test_case_id}}",
        PROJECT_WRITE,
        Capability.RUN_RECORD_MANUAL,
        {"steps": [{"order": 1, "status": "passed"}]},
    ),
    secured("POST", f"{PROJECT}/runs/{{run_id}}/finish", PROJECT_WRITE, Capability.RUN_RECORD_MANUAL, {}),
    secured("POST", f"{PROJECT}/runs/{{run_id}}/rerun-failed", PROJECT_WRITE, Capability.RUN_START, {}),
    secured(
        "POST", "/api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload", API_TOKEN, Capability.RUN_START
    ),
    secured("GET", f"{PROJECT}/failures", PROJECT_READ, Capability.FAILURE_VIEW),
    secured("GET", f"{PROJECT}/failures/{{failure_id}}", PROJECT_READ, Capability.FAILURE_VIEW),
    secured(
        "PUT",
        f"{PROJECT}/failures/{{failure_id}}/status",
        PROJECT_WRITE,
        Capability.FAILURE_MARK_FIXED,
        {"status": "fixed"},
    ),
    secured(
        "PUT",
        f"{PROJECT}/failures/{{failure_id}}/assignee",
        PROJECT_WRITE,
        Capability.FAILURE_ASSIGN,
        {"assigneeId": None},
    ),
    secured("GET", f"{PROJECT}/stories/{{jira_key}}/traceability", PROJECT_READ, Capability.REPORT_VIEW),
    secured("GET", f"{PROJECT}/story-progress", PROJECT_READ, Capability.REPORT_VIEW),
    secured("GET", f"{PROJECT}/case-latest-results", PROJECT_READ, Capability.REPORT_VIEW),
    secured("GET", f"{PROJECT}/dashboard", PROJECT_READ, Capability.REPORT_VIEW),
    secured("GET", f"{PROJECT}/my-work", PROJECT_READ, Capability.REPORT_VIEW),
    secured("POST", "/mcp", API_TOKEN),
]


def list_routes(*accesses: RouteAccess) -> list[SecuredRoute]:
    return [route for route in SECURED_ROUTES if route.access in accesses]

# Functional specs

**Status:** Draft · **Updated:** 2026-11-01

One spec per feature module of [WBS section 3](../wbs/wbs.md#3-client-application-feature-modules). Each spec describes what the code does today (waves W1–W6), not what the proposals planned. Where the code and the [proposals](../discussions/) differ, the code wins and the spec lists the difference.

The non-functional requirements are in [non-functional-requirements.md](non-functional-requirements.md). The user flows and state diagrams are in [../design/user-flows.md](../design/user-flows.md). Domain words are defined in the [glossary](../product/glossary.md).

## Index

| WBS | Spec | Story prefix | Server module(s) | Client route(s) |
| --- | --- | --- | --- | --- |
| 3.1 | [app-shell.md](app-shell.md) | SHELL | `projects`, `auth` (`/api/auth/me`, `/api/me`), `notifications`, `live_events` | every page under `(app)`, `/`, not-found and error pages |
| 3.2 | [authentication-and-account.md](authentication-and-account.md) | AUTH | `auth`, `api_tokens`, `files` (avatar) | `/sign-in`, `/two-factor`, `/two-factor/setup`, `/invite/[token]`, `/forgot-password`, `/reset-password/[token]`, `/profile`, `/connect-claude` |
| 3.3 | [projects.md](projects.md) | PROJ | `projects`, `jira` (lookups) | `/projects`, `/projects/new`, `/projects/[projectKey]/members`, project switcher |
| 3.3b | [user-management.md](user-management.md) | USER | `auth` (users router), `projects` (user access) | `/users`, `/users/[userId]` |
| 3.4 | [dashboard.md](dashboard.md) | DASH | `insights`, `runs` | `/`, `/projects/[projectKey]` |
| 3.5 | [sprints-and-stories.md](sprints-and-stories.md) | STORY | `stories`, `jira` | `/projects/[projectKey]/sprints`, `/sprints/[sprintId]`, `/stories`, `/stories/[jiraKey]` |
| 3.6 | [test-cases.md](test-cases.md) | CASE | `test_cases`, `files` | `/projects/[projectKey]/test-cases`, `/test-cases/new`, `/test-cases/[caseCode]` |
| 3.7 | [traceability.md](traceability.md) | TRACE | `insights`, `test_cases`, `stories` | Traceability tab of `/projects/[projectKey]/stories/[jiraKey]` |
| 3.8 | [readiness-review.md](readiness-review.md) | GAP | `gaps` (REST and MCP) | Gaps tab of the story detail, `/gaps` |
| 3.9 | [environments-and-test-data.md](environments-and-test-data.md) | DATA | `test_data`, `story_context` (`resolve_data`), `audit` | `/projects/[projectKey]/test-data` |
| 3.10 | [runs.md](runs.md) | RUN | `runs` (REST and MCP), `story_context`, `files` | `/projects/[projectKey]/runs`, `/runs/[runId]`, `/runs/new`, `/runs/[runId]/record` |
| 3.11 | [failures.md](failures.md) | FAIL | `failures` | `/projects/[projectKey]/failures`, `/failures/[failureId]` |
| 3.12 | [notifications.md](notifications.md) | NOTIF | `notifications`, `live_events` | bell and panel in the top bar |
| 3.13 | [settings.md](settings.md) | SET | `jira`, `projects` | `/settings`, `/projects/[projectKey]/settings` |
| 3.14 | [client-api.md](client-api.md) | API | every router, `live_events`, `files`; `app/commands/export_openapi.py` | the data layer behind every route |

The route folders are under [client/src/app](../../client/src/app). The server modules are under [server/app/modules](../../server/app/modules).

## How a spec is written

- **Story ID:** `<PREFIX>-<n>`, numbered from 1 in each spec (for example `RUN-4`). The heading also gives the WBS id: `### RUN-4 Record a case result (WBS 3.10.3)`.
- **Acceptance criteria:** numbered AC1, AC2… inside each story. Each one is a testable statement about today's behaviour.
- **Sections, in order:** Purpose · Roles and capabilities · User stories · Rules · Screens and states · API · Errors · Later · Differences from the proposals · Open points.
- **Code values** are in backticks and match the code exactly (`in_test`, `test_case.edit`, `OPEN_GAPS_BLOCK_RUN`).
- **Button and status names** use the English UI wording from [client/src/lib/i18n/locales/en](../../client/src/lib/i18n/locales/en).
- **Every API path** in a spec starts with `/api`, except the MCP endpoint `/mcp`.

## Capabilities

The permission table lives in one file: [server/app/shared/permissions/role_capabilities.py](../../server/app/shared/permissions/role_capabilities.py). The names come from [capability.py](../../server/app/shared/permissions/capability.py) and [workspace_capability.py](../../server/app/shared/permissions/workspace_capability.py). The check itself is in [permission_checker.py](../../server/app/shared/permissions/permission_checker.py).

### Project capabilities

| Capability | Lets the holder |
| --- | --- |
| `project.view` | Open the project, its members and its environments |
| `sprint.view` | List sprints and see the sync status |
| `story.view` | List and open stories |
| `test_case.view` | List and open test cases, their versions and files |
| `test_data.view` | List test data (secret values stay hidden) |
| `gap.view` | List and open gaps |
| `run.view` | List and open runs; MCP `get_failed_cases` |
| `report.view` | Dashboard, my work, traceability, story progress, latest results |
| `failure.view` | List and open failures |
| `file.download` | Get a 5-minute download link for a stored file |
| `project.edit` | Change the project's name, description, Jira board, default environment and allowed file types |
| `member.manage` | Add, change and remove project members |
| `jira.sync` | Start a Jira sync |
| `story.mark_ready_for_test` | Move a story between `not_started` and `ready_for_test` (and from `failed` back to `ready_for_test`) |
| `story.sign_off` | Mark a story `passed` or `failed` |
| `test_case.edit` | Create, edit, review and change the status of test cases; attach test files; import cases |
| `environment.manage` | Create, edit, archive, unarchive and delete environments |
| `test_data.edit` | Create, edit, delete and import variables and endpoints |
| `secret.edit` | Create, edit, delete and import secrets (needs `test_data.edit` too) |
| `secret.reveal` | Reveal a secret value in the UI (audited) |
| `secret.use_in_run` | Get secret values for one's own running run through MCP `resolve_data` (audited) |
| `gap.raise` | Raise gaps; reopen a gap one raised |
| `gap.answer` | Answer (and so resolve) a gap |
| `gap.reassign` | Change who a gap is assigned to |
| `run.start` | Start runs (MCP `start_run`, a manual run, a re-run), record Claude results, finish one's own run, get screenshot upload links and test files |
| `run.record_manual` | Start, record and finish manual runs; upload evidence |
| `run.finish_any` | Finish or record a run someone else started |
| `failure.assign` | Assign, reassign or unassign a failure |
| `failure.mark_fixed` | Move a failure to `fixed` |
| `failure.verify` | Move a `fixed` failure to `verified` or `reopened` |
| `api_token.create` | Create a personal API token for this project |

### Workspace capabilities

| Capability | Lets the holder |
| --- | --- |
| `user.manage` | List, invite, resend, deactivate, reactivate and reset the two-factor of workspace users |
| `project.create` | Create a project; list Jira projects and boards |
| `project.archive` | Archive and unarchive a project |
| `project.view_all` | See every project. No use case checks this name today: the "acts as project Admin" rule below reads the workspace role directly |
| `jira.configure` | Read and save the workspace Jira connection |
| `user_access.view` | See which projects a user belongs to |
| `workspace_role.manage` | Change workspace roles and invite workspace admins (Owner only) |

## Role × capability matrix

Built by hand from `PROJECT_ROLE_CAPABILITIES` and `WORKSPACE_ROLE_CAPABILITIES`. ✓ = granted, – = refused. Project roles in code: `admin`, `pm`, `ba`, `qc`, `dev`, `viewer`. Workspace roles: `owner`, `admin`, `member`.

### Project roles

| Capability | Admin | PM | BA | QC | Dev | Viewer |
| --- | --- | --- | --- | --- | --- | --- |
| `project.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `sprint.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `story.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `test_case.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `test_data.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `gap.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `run.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `report.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `failure.view` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `file.download` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `api_token.create` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `project.edit` | ✓ | – | – | – | – | – |
| `member.manage` | ✓ | – | – | – | – | – |
| `jira.sync` | ✓ | ✓ | ✓ | – | – | – |
| `story.mark_ready_for_test` | ✓ | – | – | – | ✓ | – |
| `story.sign_off` | ✓ | – | – | ✓ | – | – |
| `test_case.edit` | ✓ | – | – | ✓ | – | – |
| `environment.manage` | ✓ | – | – | ✓ | ✓ | – |
| `test_data.edit` | ✓ | – | – | ✓ | ✓ | – |
| `secret.edit` | ✓ | – | – | ✓ | – | – |
| `secret.reveal` | ✓ | – | – | ✓ | – | – |
| `secret.use_in_run` | ✓ | – | – | ✓ | ✓ | – |
| `gap.raise` | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| `gap.answer` | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| `gap.reassign` | ✓ | ✓ | ✓ | ✓ | ✓ | – |
| `run.start` | ✓ | – | – | ✓ | ✓ | – |
| `run.record_manual` | ✓ | – | – | ✓ | – | – |
| `run.finish_any` | ✓ | – | – | – | – | – |
| `failure.assign` | ✓ | – | – | ✓ | ✓ | – |
| `failure.mark_fixed` | ✓ | – | – | – | ✓ | – |
| `failure.verify` | ✓ | – | – | ✓ | – | – |

### Workspace roles

| Capability | Owner | Workspace admin | Member |
| --- | --- | --- | --- |
| `user.manage` | ✓ | ✓ | – |
| `project.create` | ✓ | ✓ | – |
| `project.archive` | ✓ | ✓ | – |
| `project.view_all` | ✓ | ✓ | – |
| `jira.configure` | ✓ | ✓ | – |
| `user_access.view` | ✓ | ✓ | – |
| `workspace_role.manage` | ✓ | – | – |

## Rules every spec relies on

- **Every call is checked on the server.** Each use case calls `require(access, capability)` or `require_workspace(actor, capability)`. Hiding a button in the client is a convenience only. The client hides items from the project's `capabilities` list, which `GET /api/projects/{project_key}` returns.
- **Workspace admins act as project Admin, for session actors only.** A signed-in Owner or Workspace admin gets the `admin` project role in every project, members or not ([effective_role.py](../../server/app/modules/projects/utils/effective_role.py)). An API token never gets this: it uses the owner's real project membership, so a workspace admin who is not a member of the token's project gets `INVALID_API_TOKEN`.
- **Non-members get 404.** A user who is not a member (and not acting as a workspace admin) gets `NOT_FOUND` ("Project not found."), never `PERMISSION_DENIED`, so they cannot tell that the project exists. A member who lacks a capability gets `PERMISSION_DENIED` (403).
- **Archived projects are read-only.** On an archived project, every capability outside `READ_CAPABILITIES` is refused with `PROJECT_ARCHIVED` (409). `READ_CAPABILITIES` is the ten view capabilities plus `secret.reveal`. The check runs after the role check, so a role that lacks the capability still gets `PERMISSION_DENIED`. The same rule holds for REST and MCP calls. Archiving and unarchiving are workspace actions (`project.archive`), so they work on an archived project.
- **API tokens are bound to one project.** An MCP call works only in the token's project; any other project gives `NOT_FOUND`. Every call re-checks that the token is active, the user is active and still a member, and the role has the capability.
- **Error body.** Every refused call returns `{"code": "<ErrorCode>", "message": "<text>"}` with the HTTP status from [error_handlers.py](../../server/app/api/error_handlers.py). MCP tools return the same pair as an error result, `"<CODE>: <message>"`.

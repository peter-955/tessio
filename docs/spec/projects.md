# Projects

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.3 · Story prefix PROJ · Index: [README](README.md)

## Purpose

A project is one Jira project (one-to-one) plus everything Tessio keeps for it: members and roles, environments, test data, test cases, runs and failures. Workspace admins create and archive projects; the project Admin manages members. Server: [server/app/modules/projects](../../server/app/modules/projects). Client: [client/src/modules/projects](../../client/src/modules/projects).

## Roles and capabilities

| Action | Capability |
| --- | --- |
| List projects | signed in (members see their projects; workspace admins see all) |
| Open a project, list members | `project.view` |
| Create a project, list Jira projects | `project.create` (workspace) |
| Edit a project | `project.edit` (project Admin), see [settings](settings.md) |
| Archive and unarchive | `project.archive` (workspace) plus `project.view` |
| Add, change, remove members; list candidates | `member.manage` (project Admin) |

## User stories

### PROJ-1 Create a project (WBS 3.3.1)

As a workspace admin, I want to create a project linked to a Jira project and board, or one whose stories are written in Tessio, so that the team can test with or without Jira.

- AC1: `/projects/new` is open to the Owner and Workspace admins only; others see "Only workspace admins can create projects".
- AC2: The form starts with a choice: "Link a Jira project" or "Write stories in Tessio" (WBS 3.3.5, [proposal](../discussions/projects-without-jira-proposal.md)). When Jira is not connected, only "Write stories in Tessio" is offered, with "Jira isn't connected, so this project's stories will be written in Tessio…". `POST /api/projects` without `jiraProjectKey` and `jiraBoardId` creates a project without Jira, connection or not; giving only one of them gets 422; giving both without a connection gets `JIRA_NOT_CONFIGURED`.
- AC2b: A project without Jira has `jiraProjectKey` and `jiraBoardId` null and `isLinkedToJira` false. Its settings show "Stories: Written in Tessio" and no board; setting a board gets `JIRA_NOT_CONFIGURED`. The project list shows "Written in Tessio" in the Jira column.
- AC3: The Jira project dropdown is filled from `GET /api/workspace/jira/projects`, which leaves out Jira projects already linked. The board dropdown is filled from `GET /api/workspace/jira/boards?jiraProjectKey=…`.
- AC4: The key must match `^[A-Z][A-Z0-9]{1,9}$` and cannot be changed later. A used key gets `PROJECT_KEY_ALREADY_USED`; a Jira project already linked gets `JIRA_PROJECT_ALREADY_LINKED`.
- AC5: Name (1 to 200 characters) and description (up to 2000) are trimmed. The project starts with the 10 default allowed file types.
- AC6: The creator becomes the project's first `admin` member.

### PROJ-2 Browse projects (WBS 3.3.2)

As a user, I want a list of my projects, so that I can open one or manage it.

- AC1: `/projects` lists name, key, Jira project, "My role" and status. Members see the projects they belong to; workspace admins see every project, with "No role" where they are not a member.
- AC2: "Show archived" adds archived projects (`includeArchived=true`), marked "Archived".
- AC3: The empty state says "No projects yet" to workspace admins (with New project) and "You are not in any project yet. Ask a workspace admin to add you." to others.
- AC4: The row menu offers Members, Settings, and Archive or Unarchive, each shown only when the caller may use it.

### PROJ-3 Archive and unarchive (WBS 3.3.2)

As a workspace admin, I want to archive a finished project, so that its history is kept but nothing changes any more.

- AC1: Archive asks "Archive {name}?" ("Everyone keeps read access; nothing can be changed.") and calls `POST /api/projects/{project_key}/archive`. Archiving twice keeps the first date.
- AC2: On an archived project every capability outside `READ_CAPABILITIES` is refused with `PROJECT_ARCHIVED`, through REST and MCP. Reading, downloading files and revealing secrets still work.
- AC3: Every page shows the archived banner ([SHELL-7](app-shell.md#shell-7-archived-project-banner-wbs-332)). The project leaves the switcher and the gap inbox; a Jira sync job on an archived project fails with `PROJECT_ARCHIVED`.
- AC4: Unarchive calls `POST /api/projects/{project_key}/unarchive`; members can change it again.
- AC5: A project Admin who is not a workspace admin cannot archive (`PERMISSION_DENIED`).

### PROJ-4 Manage members (WBS 3.3.4)

As a project Admin, I want to add workspace users with one role each, so that each person can do their part.

- AC1: `/projects/[projectKey]/members` lists member, status (Invited, Deactivated), role and date added. Every member can see the list (`project.view`).
- AC2: "Add member" searches `GET /api/projects/{project_key}/members/candidates?query=…`: active and invited users who are not members yet, at most 20.
- AC3: `PUT /api/projects/{project_key}/members/{user_id}` adds a member or changes the role to one of `admin`, `pm`, `ba`, `qc`, `dev`, `viewer`. Each person has exactly one role per project.
- AC4: `DELETE /api/projects/{project_key}/members/{user_id}` removes a member. Removing oneself warns "You will lose access to this project."
- AC5: The last `admin` member can be neither removed nor demoted (`LAST_PROJECT_ADMIN`).
- AC6: A `deactivated` user cannot be added (`USER_DEACTIVATED`).
- AC7: Every change publishes `project.members_changed`, so open member lists, project contexts and live-event filters refresh at once.

### PROJ-5 Project context and role (WBS 3.3.2)

As a member, I want every project page to know my role, so that I see only what I may use.

- AC1: `GET /api/projects/{project_key}` returns the project, `myRole` and `capabilities`.
- AC2: A non-member gets `NOT_FOUND` and the "Project not found" view.
- AC3: A workspace admin who is not a member gets `myRole` `admin` and every capability.

### PROJ-6 Project switcher (WBS 3.3.3)

As a member of several projects, I want to switch project from the top bar, so that I move between teams quickly.

- AC1: The switcher lists only active projects the user can open, from `GET /api/projects`.
- AC2: The chosen project is remembered in the browser and used by `/` ([SHELL-3](app-shell.md#shell-3-home-route-wbs-312)).
- AC3: "All projects" opens `/projects`.

## Rules

- Key pattern `^[A-Z][A-Z0-9]{1,9}$`; the key is the URL id (`/projects/SHOP`) and never changes.
- One Tessio project per Jira project (`JIRA_PROJECT_ALREADY_LINKED`).
- At least one `admin` member at all times (`LAST_PROJECT_ADMIN`).
- Member candidates: up to 20 per search.
- Archive keeps everything; there is no delete.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects` | admin or member empty state | "Loading projects" | "Projects could not be loaded" | "Archived" badge, hidden unless "Show archived" | row actions hidden | `project.members_changed` |
| `/projects/new` | "Connect Jira first" | "Loading the Jira connection" | "Jira data could not be loaded" + Open Jira settings | – | "Only workspace admins can create projects" | – |
| `/projects/[projectKey]/members` | "No members yet" | "Loading members" | "Members could not be loaded" | read-only list | read-only list without Add member | `project.members_changed` |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects` | signed in |
| `POST /api/projects` | `project.create` |
| `GET /api/projects/{project_key}` | `project.view` |
| `PATCH /api/projects/{project_key}` | `project.edit` ([settings](settings.md)) |
| `POST /api/projects/{project_key}/archive` | `project.view` + `project.archive` |
| `POST /api/projects/{project_key}/unarchive` | `project.view` + `project.archive` |
| `GET /api/projects/{project_key}/members` | `project.view` |
| `GET /api/projects/{project_key}/members/candidates` | `member.manage` |
| `PUT /api/projects/{project_key}/members/{user_id}` | `member.manage` |
| `DELETE /api/projects/{project_key}/members/{user_id}` | `member.manage` |
| `GET /api/workspace/jira/projects` | `project.create` |
| `GET /api/workspace/jira/boards` | `project.create`, or `project.edit` on the project linked to that Jira project |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown project key, a non-member, or a member or user id that does not exist |
| `PERMISSION_DENIED` | Missing capability (for example a project Admin archiving) |
| `PROJECT_ARCHIVED` | Any write on an archived project |
| `PROJECT_KEY_ALREADY_USED` | Create with a key that exists |
| `JIRA_PROJECT_ALREADY_LINKED` | Create with a Jira project that another project uses |
| `JIRA_NOT_CONFIGURED` | Create, or Jira lookups, before the workspace Jira connection is saved |
| `JIRA_UNREACHABLE`, `JIRA_INVALID_CREDENTIALS` | Jira lookups fail |
| `LAST_PROJECT_ADMIN` | Removing or demoting the last Admin |
| `USER_DEACTIVATED` | Adding a deactivated user |
| `INVALID_REQUEST` | Body fails validation (key pattern, lengths) |

## Later

- Project delete is not planned; archive is the end of a project's life.
- Checking the Jira project key and board against Jira at create time (parked in W2).

## Differences from the proposals

- Archiving needs the workspace capability `project.archive`. The [platform proposal §3](../discussions/platform-features-proposal.md#3-project-management) let the project's managers do it.
- Members are set with one `PUT` per user (add or change) rather than a list update.

## Open points

- `GET /api/users/{user_id}/access` lists real memberships only, not a workspace admin's implicit Admin access ([user-management.md](user-management.md)).
- Not checked in a browser: the create, members and settings flows at 375 px (W3 carry-over).
- The assumptions behind WBS 3.3.1 and 3.3.4 (key format, last-admin guard, candidates list) go into the "Assumptions & blockers" section of [wbs.md](../wbs/wbs.md) (W8.T3).

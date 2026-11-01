# Settings

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.13 · Story prefix SET · Index: [README](README.md)

## Purpose

Two settings pages. **Workspace settings** hold the one Jira connection that every project syncs through. **Project settings** hold a project's name, description, Jira board, default environment and allowed file types, plus the archive action. Server: [server/app/modules/jira](../../server/app/modules/jira) and [server/app/modules/projects](../../server/app/modules/projects). Client: [client/src/modules/settings](../../client/src/modules/settings) and the project settings in [client/src/modules/projects](../../client/src/modules/projects).

## Roles and capabilities

| Action | Capability |
| --- | --- |
| Read and save the Jira connection | `jira.configure` (Owner, Workspace admin) |
| Change project settings | `project.edit` (project Admin; a workspace admin acts as Admin) |
| List boards for the linked Jira project | `project.edit` on that project, or `project.create` |
| Archive the project | `project.archive` (workspace), see [PROJ-3](projects.md#proj-3-archive-and-unarchive-wbs-332) |

## User stories

### SET-1 Workspace Jira connection (WBS 3.13.2)

As a workspace admin, I want to connect Jira once with any Jira user's email and API token, so that every project can sync without Jira admin rights.

- AC1: `/settings` shows "Jira connection" with the status: "Connected as {name} ({email}) on {siteUrl} since {date}", or "Not connected".
- AC2: The form takes the site URL (for example `https://your-team.atlassian.net`), the Jira user email and the API token, and "Test and save" calls `PUT /api/workspace/jira`.
- AC3: The server calls Jira's `/rest/api/3/myself` with these credentials before saving. A refusal (401 or 403) gives `JIRA_INVALID_CREDENTIALS`; no answer gives `JIRA_UNREACHABLE`. Nothing is saved on failure.
- AC4: The API token is stored encrypted (AES-256-GCM) and never returned. When the site URL stays the same, the token may be left empty to keep the saved one ("Leave empty to keep the saved token"); a new site URL needs a token (`INVALID_REQUEST`).
- AC5: There is one connection for the whole workspace. Members who open `/settings` see "Only workspace admins can change workspace settings".

### SET-2 Project settings (WBS 3.13.1)

As a project Admin, I want to change the project's name, Jira board and defaults, so that the project stays correct.

- AC1: `/projects/[projectKey]/settings` saves with `PATCH /api/projects/{project_key}`: name (1 to 200 characters), description (up to 2000), Jira board (from the linked Jira project's boards) and default environment.
- AC2: The key and the linked Jira project cannot be changed.
- AC3: The default environment must be an active environment of the project (`UNKNOWN_REFERENCE`, "Pick an active environment"). It can be cleared. Runs use it when none is chosen ([RUN-2](runs.md#run-2-start-a-claude-run-wbs-3103)). Archiving that environment clears the default.
- AC4: Without `project.edit` the page says "You need the project Admin role to change settings"; on an archived project it says "This project is archived and read-only". The Settings sidebar item is hidden in both cases.
- AC5: The page also shows "Archive project" for workspace admins.

### SET-3 Allowed file types (WBS 3.13.4)

As a project Admin, I want to choose which file types can be uploaded, so that only expected files are stored.

- AC1: "Allowed file types" lists MIME types, saved as `allowedFileTypes` with `PATCH /api/projects/{project_key}`. It holds 1 to 50 types, each matching `^[a-z]+/[a-z0-9.+-]+$`.
- AC2: A new project starts with: `image/png`, `image/jpeg`, `image/webp`, `image/gif`, `application/pdf`, `text/plain`, `text/csv`, `application/json`, the `.docx` type and the `.xlsx` type. "Reset to defaults" brings them back.
- AC3: "Other MIME type" adds a custom type.
- AC4: The list applies to test files, imports and manual-run evidence. Evidence also always accepts PNG, JPEG and WebP. Claude's step screenshots are always allowed ("Screenshots from runs are always allowed.").
- AC5: An upload outside the list gets `FILE_TYPE_NOT_ALLOWED`. The type is also enforced by the storage server through the signed upload policy.

## Rules

- One Jira connection per workspace (`JIRA_CONNECTION_ID = 1`).
- Site URL: an `http` or `https` host; the email is stored in lower case.
- Allowed types: 1 to 50, MIME pattern above; default list `DEFAULT_ALLOWED_FILE_TYPES` in [file_type.py](../../server/app/modules/projects/typing/constants/file_type.py).
- File size limit: 20 MB for every project, not configurable.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/settings` | "Not connected" | "Loading the Jira connection" | "The Jira connection could not be loaded" + Try again | – | "Only workspace admins can change workspace settings" | – |
| `/projects/[projectKey]/settings` | "No environments yet." + Manage environments | "Loading boards…", "Loading environments" | "Boards could not be loaded; the current board is kept."; "Environments could not be loaded" | "This project is archived and read-only" | "You need the project Admin role to change settings" | `project.members_changed` refetches the project |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/workspace/jira` | `jira.configure` |
| `PUT /api/workspace/jira` | `jira.configure` |
| `GET /api/workspace/jira/projects` | `project.create` |
| `GET /api/workspace/jira/boards?jiraProjectKey=` | `project.create`, or `project.edit` on the linked project |
| `PATCH /api/projects/{project_key}` | `project.edit` |
| `GET /api/projects/{project_key}/environments` | `project.view` |

## Errors

| ErrorCode | When |
| --- | --- |
| `JIRA_INVALID_CREDENTIALS` | Jira refuses the email and API token |
| `JIRA_UNREACHABLE` | Jira does not answer, or answers with an error |
| `JIRA_NOT_CONFIGURED` | Board or project lookups before a connection exists |
| `INVALID_REQUEST` | Bad site URL, or a new site URL without a token; invalid MIME type |
| `UNKNOWN_REFERENCE` | Default environment that is not an active environment of the project |
| `PERMISSION_DENIED` | Missing capability |
| `PROJECT_ARCHIVED` | Saving settings on an archived project |

## Later

- 3.13.3 Notification settings.
- Disconnecting Jira (there is no `DELETE /api/workspace/jira`).

## Differences from the proposals

- WBS 3.13.1 names "Jira project" in project settings. The linked Jira project cannot change after create; only the board can.
- No audit event or live event is written when the Jira connection changes (parked in W2).

## Open points

- The connection has not been tried against a real Jira Cloud site; all Jira HTTP behaviour is covered by mock-transport tests (blocker for WBS 1.7.4).
- In project settings, pressing Enter in "Other MIME type" submits the form instead of adding the type; use the Add button (W3 carry-over).

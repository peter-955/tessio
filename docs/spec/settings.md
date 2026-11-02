# Settings

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.13 · Story prefix SET · Index: [README](README.md)

## Purpose

Two settings pages. **Workspace settings** hold the one Jira connection that every project syncs through. **Project settings** hold a project's name, description, Jira board, default environment, allowed file types and the "Reviewer must not be the author" rule, plus the archive action. Server: [server/app/modules/jira](../../server/app/modules/jira) and [server/app/modules/projects](../../server/app/modules/projects). Client: [client/src/modules/settings](../../client/src/modules/settings) and the project settings in [client/src/modules/projects](../../client/src/modules/projects); the chat channels card is in [client/src/modules/chat-channels](../../client/src/modules/chat-channels).

## Roles and capabilities

| Action | Capability |
| --- | --- |
| Read and save the Jira connection | `jira.configure` (Owner, Workspace admin) |
| Change project settings | `project.edit` (project Admin; a workspace admin acts as Admin) |
| List boards for the linked Jira project | `project.edit` on that project, or `project.create` |
| Archive the project | `project.archive` (workspace), see [PROJ-3](projects.md#proj-3-archive-and-unarchive-wbs-332) |
| Manage labels (label manager card) | `test_case.edit` (Admin, QC) through the label routes; the card shows on the settings page, which needs `project.edit` |
| Manage Slack and Teams channels | `integration.manage` (project Admin) |

## User stories

### SET-1 Workspace Jira connection (WBS 3.13.2)

As a workspace admin, I want to connect Jira once with any Jira user's email and API token, so that every project can sync without Jira admin rights.

- AC1: `/settings` shows "Jira connection" with the status: "Connected as {name} ({email}) on {siteUrl} since {date}", or "Not connected".
- AC2: The form takes the site URL (for example `https://your-team.atlassian.net`), the Jira user email and the API token, and "Test and save" calls `PUT /api/workspace/jira`.
- AC3: The server calls Jira's `/rest/api/3/myself` with these credentials before saving. A refusal (401 or 403) gives `JIRA_INVALID_CREDENTIALS`; no answer gives `JIRA_UNREACHABLE`. Nothing is saved on failure.
- AC4: The API token is stored encrypted (AES-256-GCM) and never returned. When the site URL stays the same, the token may be left empty to keep the saved one ("Leave empty to keep the saved token"); a new site URL needs a token (`INVALID_REQUEST`).
- AC5: There is one connection for the whole workspace. Members who open `/settings` see "Only workspace admins can change workspace settings".
- AC6 (write check, WBS 9.4): saving the connection also checks what the Jira account may write, with Jira's `GET /rest/api/3/mypermissions` for `CREATE_ISSUES`, `ADD_COMMENTS`, `CREATE_ATTACHMENTS` and `LINK_ISSUES`. It checks each Jira project linked to an active Tessio project (`projectKey`), or once without a project when none is linked. A permission is missing when any of those projects lacks it; a Jira project that Jira does not find (400 or 404) counts as missing everything. The result is saved with the connection: `canCreateIssues` (Create issues held), `canComment` (Add comments held), `missingPermissions` (the missing ones, in the order above) and `permissionsCheckedAt`.
- AC7: `GET` and `PUT /api/workspace/jira` return `canCreateIssues`, `canComment` (`null` until checked, for a connection saved before migration 0027), `missingPermissions` and `permissionsCheckedAt`. Each Jira sync of a project checks again and saves the result ([STORY-4](sprints-and-stories.md#story-4-sync-from-jira-wbs-354)); a check that fails there is logged and keeps the last result.
- AC8: `GET /api/projects/{project_key}/jira-write-access` (`project.view`, any member, also on an archived project) gives the same check to project members who cannot read the workspace connection: `isProjectLinked`, `isConnectionConfigured`, `canCreateIssues`, `canComment`, `missingPermissions` and `checkedAt` (the last four `null` / empty for a project without Jira or without a connection). The client hides *Create Jira bug* while `canCreateIssues` is `false` and the post-results setting while `canComment` is `false`, and the Jira settings card names each missing permission (W11.T2). Spike S6 (which permissions a real Jira needs) was not run.

### SET-2 Project settings (WBS 3.13.1)

As a project Admin, I want to change the project's name, Jira board and defaults, so that the project stays correct.

- AC1: `/projects/[projectKey]/settings` saves with `PATCH /api/projects/{project_key}`: name (1 to 200 characters), description (up to 2000), Jira board (from the linked Jira project's boards) and default environment.
- AC2: The key and the linked Jira project cannot be changed.
- AC3: The default environment must be an active environment of the project (`UNKNOWN_REFERENCE`, "Pick an active environment"). It can be cleared. Runs use it when none is chosen ([RUN-2](runs.md#run-2-start-a-claude-run-wbs-3103)). Archiving that environment clears the default.
- AC4: Without `project.edit` the page says "You need the project Admin role to change settings"; on an archived project it says "This project is archived and read-only". The Settings sidebar item is hidden in both cases.
- AC5: The page also shows "Archive project" for workspace admins.
- AC6 (WBS 9.4): a project linked to Jira also saves `jiraBugIssueType` (the Jira issue type for bugs created from failures, 1 to 60 characters, trimmed; default "Bug") and `jiraPostResults` (`off`, `on_sign_off` or `every_run`; default `off`) with the same `PATCH`. The project reply always carries both. A project not linked to Jira that sends either gets `JIRA_NOT_CONFIGURED`. What the setting posts is in [STORY-9](sprints-and-stories.md#story-9-results-on-the-jira-story-wbs-94); the bug is in [FAIL-7](failures.md#fail-7-jira-bug-from-a-failure-wbs-94).

### SET-3 Allowed file types (WBS 3.13.4)

As a project Admin, I want to choose which file types can be uploaded, so that only expected files are stored.

- AC1: "Allowed file types" lists MIME types, saved as `allowedFileTypes` with `PATCH /api/projects/{project_key}`. It holds 1 to 50 types, each matching `^[a-z]+/[a-z0-9.+-]+$`.
- AC2: A new project starts with: `image/png`, `image/jpeg`, `image/webp`, `image/gif`, `application/pdf`, `text/plain`, `text/csv`, `application/json`, the `.docx` type and the `.xlsx` type. "Reset to defaults" brings them back.
- AC3: "Other MIME type" adds a custom type.
- AC4: The list applies to test files, imports and manual-run evidence. Evidence also always accepts PNG, JPEG and WebP. Claude's step screenshots are always allowed ("Screenshots from runs are always allowed.").
- AC5: An upload outside the list gets `FILE_TYPE_NOT_ALLOWED`. The type is also enforced by the storage server through the signed upload policy.

### SET-4 Reviewer must not be the author (WBS 9.3)

As a project Admin, I want to make someone other than the author review each case, so that no one approves their own work.

- AC1: "Reviewer must not be the author" is saved as `requireSeparateReviewer` (true or false) with `PATCH /api/projects/{project_key}` (`project.edit`). Leaving the field out, or sending null, keeps the saved value. The project reply always carries `requireSeparateReviewer`.
- AC2: A new project starts with the rule off: anyone with `test_case.edit` (Admin, QC) may mark their own case Ready, as before.
- AC3: With the rule on, the person who saved a case's current version gets `REVIEWER_IS_AUTHOR` when they mark it Ready or "Mark reviewed" ([CASE-15 AC6](test-cases.md#case-15-version-compare-and-review-comments-wbs-93)).
- AC4: Changing the rule touches no case: Ready cases stay Ready.
- AC5: A "Review" card comes after "Labels" in project settings (so only for `project.edit`). It has one switch, "Reviewer must not be the author", with the note "When on, the person who saved a case's current version can't mark it Ready or reviewed. Another QC or Admin has to." Save is enabled only after the switch changes, sends only `requireSeparateReviewer`, and shows "Review settings saved.". The switch follows a newer saved value from the server. The client code is `client/src/modules/case-review/components/review-settings-card/`.

### SET-5 Labels (WBS 9.1)

As a project Admin, I want one place to see, rename, recolour and delete the project's labels, so that the label list stays tidy.

- AC1: A "Labels" card comes after "Allowed file types" ([label-manager-card.tsx](../../client/src/modules/labels/components/label-manager-card/label-manager-card.tsx)). It lists the labels from `GET /api/projects/{project_key}/labels` by name in a table: the label as a chip in its colour and its case count ("Used by {n} case" / "Used by {n} cases"). With no labels it says "No labels yet."; while loading it shows a skeleton; on an error "Labels could not be loaded" + Try again.
- AC2: "New label" opens a dialog with Name (1 to 40 characters, trimmed), Color (the eight colours of [CASE-13 AC2](test-cases.md#case-13-labels-wbs-91), Gray by default) and a preview chip, and posts to `POST …/labels`. The dialog refuses an empty or too long name, and a name another label has in any case ("A label with this name already exists."), before sending; the server's `CONFLICT` shows on the name field too.
- AC3: Each row's Actions menu has Edit and Delete. Edit opens the same dialog and sends only the changed fields with `PATCH …/labels/{label_id}` (changing only the case of the label's own name is allowed); a save with no change closes without a request. Delete asks first ("Delete {name}? It is removed from {n} cases.") and calls `DELETE …/labels/{label_id}`. Toasts: "Label created", "Label saved", "Label deleted".
- AC4: The settings page shows its cards only with `project.edit`, so the card is for project Admins. "New label" and the Actions menu also need `test_case.edit` and a project that is not archived. QC (who also has `test_case.edit`) creates labels from the label picker on the case page; renaming, recolouring and deleting are done by an Admin here.
- AC5: The list refreshes on `label.changed`, and after any label or case-label change made in this browser.

### SET-7 Chat channels (WBS 9.6)

As a project Admin, I want to connect Slack or Teams channels to the project, so that the team sees runs, failures, gaps and sign-offs where it talks.

- AC1: The server side is [NOTIF-8](notifications.md#notif-8-slack-and-teams-channels-wbs-96): the routes `GET/POST …/chat-channels`, `PATCH/DELETE …/chat-channels/{chat_channel_id}` and `POST …/chat-channels/{chat_channel_id}/test`, all `integration.manage` (project Admin), refused on an archived project.
- AC2: A channel row carries `kind`, `name`, `webhookUrlMasked` (never the URL), `events`, `isActive`, `lastDeliveryStatus` (`delivered`, `failed` or null), `lastDeliveryAt`, `lastDeliveryError` and `createdAt`. The list is sorted by name.
- AC3: A "Chat channels" card comes after "Review" (and after the Jira results card when there is one), before "Webhooks" ([chat-channels-card.tsx](../../client/src/modules/chat-channels/components/chat-channels-card/chat-channels-card.tsx)). It shows only with `integration.manage` on a project that is not archived (project Admins), so it never calls the routes for anyone else. It refreshes on `chat_channel.changed` and after every change made in this browser.
- AC4: The card lists the channels in the server's order in a table: the name, a "Slack" or "Teams" badge, an "Off" badge when turned off, the masked URL (`webhookUrlMasked`; the full URL is never shown), the events by name ("Run finished, Failure opened"), and the last message: "Not sent yet", or a "Delivered" or "Failed" badge with its time (UTC), plus `lastDeliveryError` under a failure. With no channels it says "No chat channels yet."; while loading it shows a skeleton; on an error "Chat channels could not be loaded" + Try again.
- AC5: "Add channel" opens a dialog: Chat app (Slack or Teams; it cannot change later), Name (1 to 80 characters, trimmed), Webhook URL, Events (the seven events as checkboxes; a new channel starts with "Run finished" and "Failure opened") and "Post messages to this channel" (on). The URL field explains where to get the URL for the chosen app (Slack: an incoming webhook, `https://hooks.slack.com/…`; Teams: the Workflows template "Post to a channel when a webhook request is received") and that Tessio keeps it encrypted. Before sending, the dialog refuses an empty or too long name, a name another channel of the project has in any case ("A chat channel with this name already exists."), an empty URL, a URL that is not `https` ("Enter an https URL, …") and no event ("Pick at least one event."). The server's `CONFLICT` shows on the name and `WEBHOOK_URL_INVALID` on the URL ("Enter a public https URL from Slack or Teams."). With 20 channels "Add channel" is disabled and the card says "A project can have at most 20 chat channels.".
- AC6: Each row's Actions menu has "Send test message", "Edit", "Turn off" (or "Turn on") and "Delete". Edit opens the same dialog with the URL field empty, labelled "New webhook URL" and saying "Saved URL: {masked}. Leave empty to keep it."; it sends only the changed fields (the URL only when one is typed, events in the server's order) with `PATCH …/chat-channels/{chat_channel_id}`, and closes without a request when nothing changed. Turn off or on sends `{ isActive }` only. Delete asks first ("Delete {name}? Tessio stops posting to this channel. The webhook itself stays in Slack or Teams.") and calls `DELETE`. Toasts: "Chat channel added", "Chat channel saved", "{name} turned off" / "{name} turned on", "Chat channel deleted".
- AC7: "Send test message" calls `POST …/chat-channels/{chat_channel_id}/test`. Success shows "Test message sent to {name}"; `CHAT_DELIVERY_FAILED` shows "The test message to {name} was not delivered. The reason is shown on the channel." Either way the list reloads, so the row shows the new last message status and error.

## Rules

- One Jira connection per workspace (`JIRA_CONNECTION_ID = 1`).
- Site URL: an `http` or `https` host; the email is stored in lower case.
- Allowed types: 1 to 50, MIME pattern above; default list `DEFAULT_ALLOWED_FILE_TYPES` in [file_type.py](../../server/app/modules/projects/typing/constants/file_type.py).
- File size limit: 20 MB for every project, not configurable.
- `requireSeparateReviewer` defaults to false (column `projects.require_separate_reviewer`, migration 0023).
- `jiraBugIssueType` defaults to "Bug" and `jiraPostResults` to `off` (columns `projects.jira_bug_issue_type` and `projects.jira_post_results`, migration 0027). The write check lives on `jira_connection` (`can_create_issues`, `can_comment`, `missing_permissions`, `permissions_checked_at`, migration 0027).
- Labels live in tables `labels` and `test_case_labels` (migration 0021); the rules are in [CASE-13](test-cases.md#case-13-labels-wbs-91).
- Chat channels live in table `project_chat_channels` (migration 0028); the rules are in [NOTIF-8](notifications.md#notif-8-slack-and-teams-channels-wbs-96).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/settings` | "Not connected" | "Loading the Jira connection" | "The Jira connection could not be loaded" + Try again | – | "Only workspace admins can change workspace settings" | – |
| `/projects/[projectKey]/settings` | "No environments yet." + Manage environments; "No labels yet." | "Loading boards…", "Loading environments", labels skeleton | "Boards could not be loaded; the current board is kept."; "Environments could not be loaded"; "Labels could not be loaded" + Try again | "This project is archived and read-only" | "You need the project Admin role to change settings" | `project.members_changed` refetches the project; `label.changed` refetches the labels; `chat_channel.changed` refetches the chat channels |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/workspace/jira` | `jira.configure` |
| `PUT /api/workspace/jira` | `jira.configure` |
| `GET /api/workspace/jira/projects` | `project.create` |
| `GET /api/workspace/jira/boards?jiraProjectKey=` | `project.create`, or `project.edit` on the linked project |
| `PATCH /api/projects/{project_key}` | `project.edit` |
| `GET /api/projects/{project_key}/jira-write-access` | `project.view` |
| `GET /api/projects/{project_key}/environments` | `project.view` |
| `GET /api/projects/{project_key}/labels` | `test_case.view` |
| `POST …/labels`, `PATCH …/labels/{label_id}`, `DELETE …/labels/{label_id}` | `test_case.edit` |
| `GET/POST /api/projects/{project_key}/chat-channels`, `PATCH/DELETE …/chat-channels/{chat_channel_id}`, `POST …/chat-channels/{chat_channel_id}/test` | `integration.manage` |

## Errors

| ErrorCode | When |
| --- | --- |
| `JIRA_INVALID_CREDENTIALS` | Jira refuses the email and API token |
| `JIRA_UNREACHABLE` | Jira does not answer, or answers with an error |
| `JIRA_NOT_CONFIGURED` | Board or project lookups before a connection exists; `jiraBugIssueType` or `jiraPostResults` on a project not linked to Jira |
| `INVALID_REQUEST` | Bad site URL, or a new site URL without a token; invalid MIME type |
| `UNKNOWN_REFERENCE` | Default environment that is not an active environment of the project |
| `PERMISSION_DENIED` | Missing capability |
| `PROJECT_ARCHIVED` | Saving settings on an archived project |
| `WEBHOOK_URL_INVALID` | A chat channel webhook URL that is not public `https` |
| `CHAT_DELIVERY_FAILED` | The chat channel test message was not delivered |

## Later

- Disconnecting Jira (there is no `DELETE /api/workspace/jira`).

## Differences from the proposals

- WBS 3.13.1 names "Jira project" in project settings. The linked Jira project cannot change after create; only the board can.
- No audit event or live event is written when the Jira connection changes (parked in W2).

## Open points

- The connection has not been tried against a real Jira Cloud site; all Jira HTTP behaviour is covered by mock-transport tests (blocker for WBS 1.7.4).
- In project settings, pressing Enter in "Other MIME type" submits the form instead of adding the type; use the Add button (W3 carry-over).

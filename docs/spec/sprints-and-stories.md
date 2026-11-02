# Sprints and user stories

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.5 · Story prefix STORY · Index: [README](README.md)

## Purpose

Sprints, user stories and their acceptance criteria (AC) live in Jira. Tessio copies them read-only when someone presses *Sync from Jira*, and owns only each story's **test status**. Server: [server/app/modules/stories](../../server/app/modules/stories) (sync job, AC parser, test status) and [server/app/modules/jira](../../server/app/modules/jira) (Jira client). Client: [client/src/modules/sprints](../../client/src/modules/sprints) and [client/src/modules/stories](../../client/src/modules/stories).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List sprints, sprint detail, sync status | `sprint.view` | all |
| List and open stories | `story.view` | all |
| Sync from Jira | `jira.sync` | Admin, PM, BA |
| `not_started` ↔ `ready_for_test`, `failed` → `ready_for_test` | `story.mark_ready_for_test` | Admin, Dev |
| → `passed`, → `failed` (sign-off) | `story.sign_off` | Admin, QC |
| Write, edit and delete stories in a project without Jira | `story.edit` | Admin, PM, BA, QC |

## User stories

### STORY-1 Sprint list and sprint detail (WBS 3.5.1)

As a team member, I want the board's sprints, so that I can find this sprint's stories.

- AC1: `/projects/[projectKey]/sprints` lists each synced sprint with name, state (Active, Upcoming, Closed), dates and story count.
- AC2: `/projects/[projectKey]/sprints/[sprintId]` shows the sprint and "Stories in this sprint".
- AC3: An unknown sprint shows "Sprint not found" ("It may have left the sync scope.").
- AC4: With no sprints the page says "No sprints yet. An Admin, PM or BA can sync from Jira to bring in the board's sprints."

### STORY-2 Story list (WBS 3.5.2)

As a team member, I want every synced story with its test status and Jira link, so that I see where testing stands.

- AC1: `/projects/[projectKey]/stories` lists key, title, sprint, Jira status, test status and an "Open in Jira" link.
- AC2: Filters: search by key or title (up to 100 characters), sprint, and test status, sent as `query`, `sprintId` and `testStatus`.
- AC3: Extra columns from the story progress read model: AC coverage, open gaps, failures and last run ([TRACE-4](traceability.md)).
- AC4: A story that left the synced sprints shows "Not in Jira scope" and stays in the list.

### STORY-3 Story detail (WBS 3.5.3)

As a team member, I want one page per story with its description, AC, test cases, gaps, runs and traceability, so that everything about testing the story is in one place.

- AC1: `/projects/[projectKey]/stories/[jiraKey]` shows the title, Jira status, sprint, last sync date and the test status with its actions.
- AC2: Tabs: Overview, Test cases, Gaps, Runs, Traceability. The tab is kept in `?tab=` so links (for example from a gap notification) open the right one.
- AC3: Overview renders the Jira description (Atlassian Document Format) read-only. Attachments show "Attachment – open the story in Jira to view it."
- AC4: Overview lists the AC as AC1, AC2… An AC removed from Jira stays, marked "Removed from Jira {date}".
- AC5: With no AC found it says "No acceptance criteria found. Tessio reads the list under an "Acceptance criteria" heading in Jira, or the first list."
- AC6: A story outside the sync scope shows "No longer in Jira scope. This story left the synced sprints on {date}. Its history stays here."
- AC7: The key is matched without case.

### STORY-4 Sync from Jira (WBS 3.5.4)

As a PM or BA, I want to pull the latest sprints and stories from Jira when I choose, so that Tessio matches the board. Tessio never syncs on its own.

- AC1: "Sync from Jira" calls `POST /api/projects/{project_key}/sync` (202). The project's sync status becomes `queued` and a `jira.sync_project` job is queued with the job id `jira-sync:{project_id}`, so one project never has two sync jobs.
- AC2: Pressing it again while a sync is `queued` or `running` and younger than 15 minutes returns the current state and queues nothing.
- AC3: The worker sets `running`, then `succeeded` (with the last success time) or `failed` (with the error code). It publishes `jira.sync_started` and `jira.sync_finished` or `jira.sync_failed`.
- AC4: The button area shows "Never synced", "Sync queued…", "Syncing…", "Last synced {date}", or "Last sync failed: {reason}" with "Last successful sync {date}". A sync stuck for more than 15 minutes shows "The last sync stopped responding." and can be started again.
- AC5: Scope: the board's `active` and `future` sprints, and `closed` sprints that ended in the last 30 days. Epics and sub-tasks are left out.
- AC6: Title, description, Jira status, issue type and sprint are overwritten from Jira. The test status is kept.
- AC7: A story no longer returned for a synced sprint gets `jira_missing_at` and stays, with its history.
- AC8: Without a Jira connection the call answers `JIRA_NOT_CONFIGURED` ("Ask a workspace admin to connect Jira first.").
- AC9: A sync on an archived project fails with `PROJECT_ARCHIVED`.
- AC10 (WBS 9.4): after a sync succeeds, the worker checks the Jira account's write permissions again ([SET-1 AC6](settings.md#set-1-workspace-jira-connection-wbs-3132)) and refreshes the Jira status of the bugs linked to the project's active failures ([FAIL-7 AC10](failures.md#fail-7-jira-bug-from-a-failure-wbs-94)). Either step failing is logged and leaves the sync `succeeded`.

### STORY-5 AC parsed from the description (WBS 3.5.3, 3.7.4)

As a BA, I want the AC list I write in Jira to become numbered AC in Tessio, so that test cases can cover each one.

- AC1: The parser looks for a heading or short paragraph (60 characters at most) reading "Acceptance criteria" (also "Critères d'acceptation" and "Tiêu chí chấp nhận"), and takes the first list after it.
- AC2: Without that marker it takes the first list in the description. Without a list the story has no AC.
- AC3: Each list item becomes one AC, coded `AC<position>` (AC1, AC2…). Nested items are folded into their parent's text.
- AC4: On each sync the AC are matched by position: new positions add AC, changed text updates the AC and flags linked test cases for review, and positions past the end of the list get `removed_at`. A removed AC that comes back at the same position is restored and flagged.

### STORY-6 QC sign-off (WBS 3.5.5)

As a QC, I want to mark a story Passed or Failed, so that the team knows testing is done.

- AC1: "Mark passed" and "Mark failed" ask for confirmation and call `PUT /api/projects/{project_key}/stories/{jira_key}/test-status`.
- AC2: Allowed moves: `in_test` → `passed` or `failed`; `passed` → `failed`; `failed` → `passed`. Anything else gets `INVALID_STATUS_TRANSITION`.
- AC3: `passed` is refused with `STORY_SIGN_OFF_BLOCKED` while the story has an active failure (`open`, `fixed` or `reopened`) or a running run: a story run of the story, or a suite run that holds one of its cases ([SUITE-7 AC7](suites-and-plans.md#suite-7-read-models-with-suite-runs-wbs-91)) ("Resolve active failures and wait for running runs before marking it passed.").
- AC4: The change records who and when, and publishes `story.changed`.

### STORY-7 Dev marks a story Ready for test (WBS 3.5.6)

As a Dev, I want to mark a story Ready for test, so that QC knows the feature is done.

- AC1: "Mark ready for test" moves `not_started` → `ready_for_test`; "Move back to not started" moves it back. From `failed`, a Dev can also move the story to `ready_for_test` after a fix.
- AC2: Ready for test does not gate runs: a run can start in any test status.
- AC3: Starting a run (Claude or manual) moves the story to `in_test`, whatever its status. `in_test` cannot be set by hand.

### STORY-8 Stories written in Tessio (WBS 3.5.7)

As a BA, PM or QC in a project without Jira, I want to write stories and their AC in Tessio, so that the team can test without Jira.

Design record: [projects without Jira proposal](../discussions/projects-without-jira-proposal.md).

- AC1: "New story" on the story list opens the editor: title (1 to 255 characters), description (plain text, up to 20 000) and the AC list, where each row can be added, edited, moved up or down and removed (up to 50, each up to 2000 characters). It calls `POST /api/projects/{project_key}/stories` and opens the new story.
- AC2: The story gets the key `<PROJECT KEY>-<n>` from a per-project counter (`story_key_counters`); keys never repeat, even after a delete. It has `source: "tessio"`, no sprint, an empty Jira URL and status, and its description is stored as a document of one paragraph per line (`descriptionText` returns the plain text).
- AC3: AC codes come from the order (`AC1`, `AC2`…). "Edit" (`PATCH …/stories/{jira_key}`) uses the same rules as a Jira sync: a changed text marks the AC changed, a removed row keeps the AC as removed, and linked test cases get the Needs review flag.
- AC4: "Delete" (`DELETE …/stories/{jira_key}`) removes the story and its AC only when it has no test cases, runs or gaps; otherwise `CONFLICT` ("This story has test cases, runs or gaps, so it can't be deleted.").
- AC5: The story header shows "Written in Tessio" and "Last edited …" instead of the Jira type, status and "Open in Jira"; the list shows "Written in Tessio" in the Jira status column. Everything else (cases, gaps, runs, traceability, failures, sign-off, the Claude skills) works unchanged.
- AC6: In a project without Jira, "Sync from Jira" is hidden and `POST …/sync` answers `JIRA_NOT_CONFIGURED`; the sprints page says "This project has no sprints". In a Jira project, writing, editing or deleting a story gets `INVALID_REQUEST` ("Stories of this project come from Jira.").

### STORY-9 Results on the Jira story (WBS 9.4)

As a PM, I want Tessio to post the test results on the Jira story, so that people who live in Jira see them without opening Tessio.

- AC1: The project setting `jiraPostResults` ([SET-2 AC6](settings.md#set-2-project-settings-wbs-3131)) decides when: `off` (default) never; `on_sign_off` when a story is signed off as `passed` (STORY-6); `every_run` when a run finishes (Claude `finish_run`, a manual run's Finish, or a JUnit import, [RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)). An aborted run posts nothing: a finish with no results (status `aborted`) queues no job, a stale run aborted by the server queues none either, and a queued job whose run is `aborted` is skipped.
- AC2: The server then queues one job `jira.post_comment` per story on the `jira` queue, with `trigger` (`sign_off` or `run_finished`), `projectId`, `storyId` and `runId` (`null` for a sign-off). A story run gives one job; a suite run or a CI import gives one job per story in its report. Run jobs have the job id `jira-comment:{run_id}:{story_id}`. A project not linked to Jira queues nothing, and an enqueue that Redis refuses is logged and does not fail the sign-off or the finish.
- AC3: The job posts a comment (Atlassian Document Format) on the story's Jira issue: "Tessio: {key} was signed off." or "Tessio: a test run finished ({status})."; then a list with "Passed: {passed} of {total}", "Failed", "Blocked", "Skipped", "Not reported" and "Environment: {name}"; then a link "Open in Tessio" to the run (`{CLIENT_URL}/projects/{key}/runs/{run_id}`) or, for a sign-off, to the story (`…/stories/{jira_key}`). A sign-off uses the counts of the story's latest finished story run whose status is `passed` or `failed`, so an aborted run is passed over ("No results recorded yet." when there is none); a run uses that run's counts for the story.
- AC4: A story written in Tessio, a story or project that no longer exists, or a project unlinked since, is skipped. A refusal from Jira (403 `JIRA_WRITE_NOT_ALLOWED`, refused credentials, missing connection, or a 400/404 for the issue) is logged and the job is not retried. A Jira that stays unreachable after the client's rate-limit retries fails the job, and BullMQ retries it (5 attempts, exponential backoff from 30 s).
- AC5: The client hides the setting while the stored check says the account cannot comment ([SET-1 AC8](settings.md#set-1-workspace-jira-connection-wbs-3132)), and in projects without Jira (W11.T2).

## Rules

Test status transitions (`TEST_STATUS_TRANSITIONS` in [test_status.py](../../server/app/modules/stories/typing/constants/test_status.py)). The diagram is in [user-flows.md](../design/user-flows.md#story-test-status).

| From | To | Capability |
| --- | --- | --- |
| `not_started` | `ready_for_test` | `story.mark_ready_for_test` |
| `ready_for_test` | `not_started` | `story.mark_ready_for_test` |
| `in_test` | `passed`, `failed` | `story.sign_off` |
| `passed` | `failed` | `story.sign_off` |
| `failed` | `passed` | `story.sign_off` |
| `failed` | `ready_for_test` | `story.mark_ready_for_test` |
| any | `in_test` | set only by starting a run |

| Number | Value | Code |
| --- | --- | --- |
| Closed sprints synced back | 30 days | `CLOSED_SPRINT_SYNC_WINDOW` |
| Sync counts as stuck after | 15 minutes | `SYNC_STALE_AFTER` |
| Jira request timeout | 20 s (connect 5 s) | `JIRA_REQUEST_TIMEOUT_SECONDS` |
| Retries on Jira 429 or 503 | up to 3, honouring `Retry-After` (at most 60 s) | `JIRA_MAX_RATE_LIMIT_RETRIES` |
| Jira page size | 50 (sprints, boards), 100 (issue search) | `JIRA_PAGE_SIZE`, `JIRA_SEARCH_PAGE_SIZE` |
| Story search | up to 100 characters | `STORY_QUERY_MAX_LENGTH` |

- Sync statuses: `never`, `queued`, `running`, `succeeded`, `failed` (diagram in [user-flows.md](../design/user-flows.md#sync-status)).
- Jira issue search uses `/rest/api/3/search/jql`; sprints and boards use the Agile API `/rest/agile/1.0/`.
- Jira writes (WBS 9.4) use `POST /rest/api/3/issue`, `/issue/{key}/attachments`, `/issue/{key}/comment`, `/issueLink` and `GET /rest/api/3/mypermissions`, with the same rate-limit retry. On a write, 401 means `JIRA_INVALID_CREDENTIALS` and 403 means `JIRA_WRITE_NOT_ALLOWED` (on reads 403 stays `JIRA_INVALID_CREDENTIALS`).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/sprints` | "No sprints yet" | skeleton | "Sprints could not be loaded" + Try again | no Sync button | no Sync button without `jira.sync` | `jira.sync_finished` |
| `/projects/[projectKey]/sprints/[sprintId]` | no stories | skeleton | "This sprint could not be loaded"; "Sprint not found" | – | – | `jira.sync_finished` |
| `/projects/[projectKey]/stories` | "No stories yet. Stories appear after a sync from Jira."; filtered: "No matching stories" | skeleton | "Stories could not be loaded" | no Sync button | as above | `jira.sync_finished`, `story.changed`; sync status also polls every 5 s while in progress |
| `/projects/[projectKey]/stories/[jiraKey]` | "No description in Jira.", no AC | skeleton | "This story could not be loaded"; "Story not found" | status buttons hidden | buttons shown only with the capability | `story.changed`, `jira.sync_finished` |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/sprints` | `sprint.view` |
| `GET /api/projects/{project_key}/sprints/{sprint_id}` | `sprint.view` |
| `GET /api/projects/{project_key}/stories?sprintId=&testStatus=&query=` | `story.view` |
| `GET /api/projects/{project_key}/stories/{jira_key}` | `story.view` |
| `PUT /api/projects/{project_key}/stories/{jira_key}/test-status` | `story.view` + the capability of the target status |
| `GET /api/projects/{project_key}/sync` | `sprint.view` |
| `POST /api/projects/{project_key}/sync` | `jira.sync` |

There is no MCP tool here; Claude reads stories through `get_story_context` ([runs.md](runs.md)).

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown story or sprint |
| `INVALID_STATUS_TRANSITION` | A move not in the table, or `in_test` asked by hand |
| `STORY_SIGN_OFF_BLOCKED` | `passed` while an active failure or a running run (a story run, or a suite run with a case of the story) exists |
| `PERMISSION_DENIED` | The role lacks the capability for the target status, or `jira.sync` |
| `PROJECT_ARCHIVED` | Any status change or sync on an archived project |
| `JIRA_NOT_CONFIGURED` | Sync before the workspace Jira connection exists |
| `JIRA_UNREACHABLE`, `JIRA_INVALID_CREDENTIALS` | Stored as the sync's error code when Jira fails |

## Later

- Nothing in WBS 3.5 is Later.

## Differences from the proposals

- The [workflow proposal §5](../discussions/testing-workflow-proposal.md#5-roles-and-permissions) let Admin, PM and BA re-sync; the code matches. QC and Dev cannot sync (flagged assumption 3.5.4).
- Sign-off rules are stricter than proposed: `passed` is refused while failures are active or a run is running, and a new run puts the story back to `in_test` (assumption 3.5.5).
- Ready for test does not block runs (assumption 3.5.6).
- AC matching is by position, as decided in the [server proposal §15](../discussions/server-proposal.md#15-numbers-and-rules). Inserting an AC in the middle of the list re-flags every later AC.

## Open points

- WBS 1.7.4 is open: the AC parser and `/rest/api/3/search/jql` have not been tried on a real Jira site. `uv run python -m app.commands.jira_probe --issue KEY` is ready for it.
- On a real site, a search for an unknown key returns HTTP 400, which the Jira client maps to `JIRA_UNREACHABLE` rather than `NOT_FOUND`.
- A Kanban board has no sprints, so a sync succeeds with no stories.
- If a stuck sync is re-requested while the old job is still active in BullMQ, the state stays `queued` until the next request (accepted MVP behaviour).

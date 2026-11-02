# Failures

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.11 · Story prefix FAIL · Index: [README](README.md)

## Purpose

A failure tracks one failing test case from its first failed result until QC verifies the fix. Failures live in Tessio. In a project linked to Jira, a person can also create a Jira bug from a failure (FAIL-7); Tessio then shows the Jira status, but the failure's own status still moves only in Tessio. A failed result opens a failure, Dev marks it fixed, a re-run checks it, and QC verifies or reopens it. Server: [server/app/modules/failures](../../server/app/modules/failures). Client: [client/src/modules/failures](../../client/src/modules/failures).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open failures | `failure.view` | all |
| Assign, reassign, unassign | `failure.assign` | Admin, QC, Dev |
| Mark fixed | `failure.mark_fixed` | Admin, Dev |
| Verify or reopen a fixed failure | `failure.verify` | Admin, QC |
| Create a Jira bug from a failure | `failure.create_jira_issue` | Admin, QC, Dev |

## User stories

### FAIL-1 A failed result opens a failure (WBS 3.11.3)

As a Dev, I want every failing case to become a failure automatically, so that nothing is lost between report and fix.

- AC1: When a case result is `failed` (Claude or manual) and the case has no active failure, a new failure opens with status `open`, no assignee, and an `opened` event.
- AC2: When the case already has an `open` or `reopened` failure, the result is added to it (`failed_again` event).
- AC3: When the case's failure is `fixed`, the failed result reopens it automatically (`fixed` → `reopened`, shown as "Automatic").
- AC4: A `blocked` result opens no failure. A `passed` or `skipped` result changes nothing.
- AC5: After a failure is `verified`, the next failed result opens a new failure.
- AC6: A case has at most one active failure (`open`, `fixed` or `reopened`).
- AC7: A new failure takes the result's suspected cause and reason. A later failed result updates them, unless a person has changed the cause (FAIL-6).

### FAIL-2 Failure list (WBS 3.11.1)

As a Dev, I want a list of failures with status and assignee filters, so that I see what I have to fix.

- AC1: `/projects/[projectKey]/failures` lists test case, story, status (Open, Fixed, Verified, Reopened), assignee ("Unassigned" when none) and when it last failed, from `GET /api/projects/{project_key}/failures`.
- AC2: Filters: status (Active or all statuses, sent as one or more `status`), assignee (Anyone, Unassigned, Assigned to me, or a member, sent as `assigneeId` or `unassigned=true`), and story (`storyKey`). The API also accepts `testCaseId`.
- AC3: `assigneeId` with `unassigned=true` gives `INVALID_REQUEST`.
- AC4: The list returns at most 500 failures.
- AC5: A deactivated assignee shows "{name} (Deactivated)".

### FAIL-3 Failure detail (WBS 3.11.2)

As a Dev, I want the failed step, its screenshot and error, and the case's history across re-runs, so that I can reproduce the bug.

- AC1: `/projects/[projectKey]/failures/[failureId]` shows the case, story, status, assignee, opened and last-failed dates, and who changed the status.
- AC2: "Failed step" shows the step order, action, expected result, actual result, error and its screenshot ("Screenshot uploading…", "Screenshot missing" or "No screenshot"), with "Open run".
- AC3: "History" lists the case's latest results across runs (up to 50): run, result, executor, duration, who started it.
- AC3b: A data-driven case ([RUN-14](runs.md#run-14-shared-steps-and-iterations-in-a-run-wbs-92)) has one history row per iteration, so one run can give several rows. Each item of the detail's `results` has `iteration`: the data row it ran (0 first) for a case version with data rows, `null` for one without. Server: [postgres_case_result_reader.py](../../server/app/modules/failures/infrastructure/postgres_case_result_reader.py). The "History" table then has an "Iteration" column after "Result", numbered from 1 ("—" for a result without an iteration); it is hidden when no result has one. Client: [failure-result-history.tsx](../../client/src/modules/failures/components/failure-result-history/failure-result-history.tsx).
- AC4: "Timeline" lists the events: Failure opened, Failed again, "{from} → {to}" with who changed it (or Automatic), Assigned to {name}, Unassigned.
- AC5: A failure of another project shows "Failure not found".

### FAIL-4 Mark fixed, verify, reopen (WBS 3.11.3)

As a Dev and then a QC, I want to move a failure through fixed and verified, so that we agree when the bug is gone.

- AC1: "Mark fixed" (`PUT …/failures/{failure_id}/status` with `fixed`) works from `open` or `reopened`.
- AC2: "Verify" (`verified`) and "Reopen" (`reopened`) work only from `fixed`.
- AC3: Any other move gets `INVALID_STATUS_TRANSITION`. `verified` is final.
- AC4: Each change records who and when, adds a `status_changed` event and publishes `failure.changed`.
- AC5: The story cannot be signed off as `passed` while any of its failures is active ([STORY-6](sprints-and-stories.md#story-6-qc-sign-off-wbs-355)).

### FAIL-6 Suspected cause (WBS 3.11.6)

As a Dev or QC, I want to see and correct why a case failed, so that a real bug is not confused with bad test data or a broken environment.

- AC1: The failure detail shows a "Suspected cause" card: the cause (App bug, Test data, Environment, Test case out of date, Unknown) and its reason, or "No suspected cause yet."
- AC2: "Failed step" also shows the step's "Why it failed" panel (RUN-7 AC9) when the step has a diagnosis.
- AC3: People with `failure.assign` (Admin, QC, Dev) see "Change", which opens a dialog to pick the cause and write why, and calls `PUT …/failures/{failure_id}/cause` with `cause` and an optional `reason` (up to 500 characters, trimmed). A `verified` failure gives `FAILURE_CLOSED`.
- AC4: The change records who and when, adds a `cause_changed` event ("Suspected cause: {from} → {to}") and publishes `failure.changed`.

### FAIL-5 Assign a failure (WBS 3.11.5)

As a QC, I want to assign a failure to the right Dev, so that someone owns the fix.

- AC1: New failures start unassigned.
- AC2: "Assign" / "Reassign" picks any active project member, or Unassigned, and calls `PUT …/failures/{failure_id}/assignee`.
- AC3: The assignee must be an active member (`ASSIGNEE_NOT_ACTIVE_MEMBER`, "Pick an active project member.").
- AC4: A `verified` failure cannot be reassigned (`INVALID_STATUS_TRANSITION`).
- AC5: A change adds an `assigned` or `unassigned` event. Assigning sends `failure_assigned` to the new assignee, unless they assigned it to themselves.
- AC6: A failure whose assignee was deactivated shows "The assignee is deactivated. Reassign this failure."

### FAIL-7 Jira bug from a failure (WBS 9.4)

As a Dev or QC, I want to create a Jira bug from a failure with the evidence already filled in, so that the team tracks the fix where it plans its work.

- AC1: `POST /api/projects/{project_key}/failures/{failure_id}/jira-issue` (no body, `failure.create_jira_issue`: Admin, QC, Dev) answers `202` with the failure and queues job `jira.create_issue` on the `jira` queue (data `projectId`, `failureId`, `requestedBy`; job id `jira-create-issue:{failure_id}`, so a second job for the same failure is dropped while one is queued or retrying). The failure gets `jira_issue_requested_at` and its last Jira error is cleared; the response has `isJiraIssuePending: true`, and `failure.changed` is published.
- AC2: Refusals, in this order: a viewer, PM or BA gets `PERMISSION_DENIED`; an archived project `PROJECT_ARCHIVED`; an unknown failure `NOT_FOUND`; a project not linked to Jira `JIRA_NOT_CONFIGURED` ("This project is not linked to Jira."); no workspace Jira connection `JIRA_NOT_CONFIGURED`; a connection whose stored check says it cannot create issues (SET-1 AC6) `JIRA_WRITE_NOT_ALLOWED`; a failure that already has a Jira issue, or whose request is pending (asked less than 15 minutes ago and no error recorded since), `JIRA_ISSUE_ALREADY_LINKED`. A request is allowed again after a recorded error, or once a pending request is older than 15 minutes (`JIRA_ISSUE_PENDING_TIMEOUT`).
- AC3: `GET …/failures/{failure_id}/jira-issue/preview` (`failure.view`) returns exactly what the job will send: `jiraProjectKey`, `issueTypeName`, `summary`, `description` (the description as plain text), `linkedStoryJiraKey` (the story's key, or `null` for a story written in Tessio) and `hasScreenshot`. A project not linked to Jira gives `JIRA_NOT_CONFIGURED`.
- AC4: The bug: the issue type is the project's `jiraBugIssueType` (default "Bug", SET-2 AC6). The summary is "{case code} {case title}: step {n} failed" ("{case code} {case title} failed" without a failed step), on one line and at most 255 characters. The description, in Atlassian Document Format, has in order: a line naming the story and the case; "Test data (iteration n)" (data-driven cases, AC5); "Preconditions" (when the case version has them); "Steps to reproduce"; "Expected result" (the failing step's expected result); "Actual result (step n)" with the actual result and the error as a code block; "Environment" (name and base URL); "Suspected cause" with its reason (when there is one); and a link "Open the failure in Tessio" to `{CLIENT_URL}/projects/{key}/failures/{id}`. Empty parts are left out.
- AC5: "Steps to reproduce" are the steps Claude recorded for the result (`case_results.repro_steps`, W12) when present. Until then, and for results without them, they are the actions of the case's steps up to and including the failing step, from the run's step snapshot (or the case version when the run has no snapshot); steps without an action are skipped. The reader keeps a `repro_steps` slot, filled with `null` today. For a data-driven case ([RUN-14](runs.md#run-14-shared-steps-and-iterations-in-a-run-wbs-92)), the bug uses the iteration of the failure's latest result (`case_results.iteration`) and that row of the case version's `data_rows`: every `{{param.name}}` in the preconditions, the step actions and the expected result is replaced by the row's value (a name the row lacks is kept as written, and a `{{data.key}}` in a value stays a reference), and a "Test data (iteration {n})" part (n from 1), placed after the opening line, lists the row as `name = value`. A case without data rows, or an iteration past the last row, gets neither.
- AC6: Every text in the summary and description is masked with the project's secret values for the run's environment before it leaves Tessio.
- AC7: The job creates the issue, then (best effort, a Jira refusal is only logged) attaches the failing step's screenshot (`X-Atlassian-Token: no-check`) and links the issue to the story with the "Relates" link type ("relates to"), only for a story synced from Jira. It reads the new issue's status once. It stores `jiraIssueKey`, `jiraIssueUrl` (`{site}/browse/{key}`) and `jiraIssueStatus`, clears the pending state, adds a `jira_issue_created` event (actor = the person who asked, with the issue key) and publishes `failure.changed`. The key is stored before the attachment and link, so a retry never creates a second issue; a job for a failure that already has a key does nothing.
- AC8: Errors in the job: a Jira 403 records `JIRA_WRITE_NOT_ALLOWED` on the failure (`jiraIssueErrorCode`), clears the pending state, adds a `jira_issue_failed` event with the code and publishes `failure.changed`; the job is not retried. The same happens for a refused issue (Jira 400 or 404, for example an unknown issue type: `INVALID_REQUEST`), refused credentials (`JIRA_INVALID_CREDENTIALS`) and a project unlinked after the request (`JIRA_NOT_CONFIGURED`). A rate limit is retried by the Jira client (up to 3 times, honouring `Retry-After`); a Jira that stays unreachable records `JIRA_UNREACHABLE`, keeps the request pending, and fails the job so BullMQ retries it (5 attempts, exponential backoff from 30 s).
- AC9: The failure list and detail return `jiraIssueKey`, `jiraIssueUrl`, `jiraIssueStatus`, `jiraIssueDoneAt`, `isDoneInJira`, `isJiraIssuePending` and `jiraIssueErrorCode`. Events return `jiraIssueKey` and `errorCode`.
- AC10: Each Jira sync of the project ([STORY-4](sprints-and-stories.md#story-4-sync-from-jira-wbs-354)) reads the status of the linked issues of its active failures (`open`, `fixed`, `reopened`) in one JQL search (`key in (...)`, 100 keys per search). It stores the status name and sets `jiraIssueDoneAt` when the status category is Done (kept while it stays Done, cleared when the issue leaves Done), and publishes `failure.changed` for each failure that changed. Verified failures are not refreshed. A failed status search is logged and does not fail the sync.
- AC11: Tessio never changes a failure's status from Jira. A failure whose Jira issue is Done shows "Done in Jira" (`isDoneInJira`), and a Dev marks it Fixed in Tessio (FAIL-4).
- AC12: Projects not linked to Jira hide the Jira bug actions (W11.T2); the server refuses them (AC2).

## Rules

Manual transitions (`MANUAL_STATUS_TRANSITIONS` in [failure.py](../../server/app/modules/failures/typing/constants/failure.py)); the diagram is in [user-flows.md](../design/user-flows.md#failure-status).

| From | To | Capability or trigger |
| --- | --- | --- |
| (none) | `open` | a `failed` result with no active failure |
| `open`, `reopened` | `fixed` | `failure.mark_fixed` |
| `fixed` | `verified` | `failure.verify` |
| `fixed` | `reopened` | `failure.verify`, or a `failed` result (automatic) |
| `verified` | – | final; the next failed result opens a new failure |

| Limit | Value | Code |
| --- | --- | --- |
| Failure list | 500 | `MAX_FAILURE_LIST_SIZE` |
| Result history | 50 | `MAX_RESULT_HISTORY_SIZE` |
| Event kinds | `opened`, `failed_again`, `status_changed`, `assigned`, `unassigned`, `cause_changed`, `jira_issue_created`, `jira_issue_failed` | `FailureEventKind` |
| Pending Jira bug request | 15 minutes | `JIRA_ISSUE_PENDING_TIMEOUT` |
| Jira summary | 255 characters, one line | `JIRA_SUMMARY_MAX_LENGTH` |
| Linked issues per status search | 100 | `JIRA_STATUS_SEARCH_BATCH_SIZE` |
| Suspected causes | `app_bug`, `test_data`, `environment`, `test_case`, `unknown` | `SuspectedCause` |

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/failures` | "No failures. Failed results from runs show up here."; filtered: "No failures match these filters" + Clear filters | skeleton | "Could not load failures." + Retry | read-only | – | `failure.changed`, `run.case_recorded`, `run.finished` |
| `/projects/[projectKey]/failures/[failureId]` | "No failed step was reported."; "No results yet." | skeleton | "Could not load this failure."; "Failure not found" | actions hidden | each action shown only with its capability | `failure.changed`, `run.case_recorded`, `run.finished`; screenshot polls every 5 s while uploading |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/failures?status=&assigneeId=&unassigned=&storyKey=&testCaseId=` | `failure.view` |
| `GET /api/projects/{project_key}/failures/{failure_id}` | `failure.view` |
| `PUT /api/projects/{project_key}/failures/{failure_id}/status` | `failure.mark_fixed` (to `fixed`) or `failure.verify` (to `verified`, `reopened`) |
| `PUT /api/projects/{project_key}/failures/{failure_id}/assignee` | `failure.assign` |
| `PUT /api/projects/{project_key}/failures/{failure_id}/cause` | `failure.assign` |
| `GET /api/projects/{project_key}/failures/{failure_id}/jira-issue/preview` | `failure.view` |
| `POST /api/projects/{project_key}/failures/{failure_id}/jira-issue` (202) | `failure.create_jira_issue` |

There is no MCP tool for failures; Claude reads failed cases with `get_failed_cases` ([runs.md](runs.md)).

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown failure or another project's failure |
| `INVALID_STATUS_TRANSITION` | A move not in the table, or reassigning a verified failure |
| `ASSIGNEE_NOT_ACTIVE_MEMBER` | Assignee not an active project member |
| `INVALID_REQUEST` | `assigneeId` and `unassigned` together; recorded on the failure when Jira refuses the bug (400 or 404) |
| `JIRA_NOT_CONFIGURED` | Jira bug in a project not linked to Jira, or without a workspace connection |
| `JIRA_WRITE_NOT_ALLOWED` | The stored check says the Jira account cannot create issues; recorded on the failure after a Jira 403 |
| `JIRA_ISSUE_ALREADY_LINKED` | The failure already has a Jira issue, or a request is pending |
| `JIRA_UNREACHABLE` | Recorded on the failure while the job retries an unreachable Jira |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or a write on an archived project |

## Later

- 3.11.4 Comments on a failure.

## Differences from the proposals

- Verify works only from `fixed`, not from `open` (assumption 3.11.3).
- Jira bug (F4): the proposal asked for the Create issues and Add comments check; the check also covers Create attachments and Link issues, and the attachment and link are best effort (assumption 9.4). "Done in Jira" never moves the failure (proposal assumption).
- A `blocked` result opens no failure, and a failure after `verified` is a new failure (assumption 3.11.3).
- `reopened` can be marked fixed again; the proposal drew Reopened as an end state.
- The [workflow proposal §3](../discussions/testing-workflow-proposal.md#3-the-workflow-inside-tessio) assigned new failures to the dev. In code they start unassigned and are assigned by hand ([server proposal §15](../discussions/server-proposal.md#15-numbers-and-rules)).

## Open points

- Jira bug: a real Jira site has not been used yet (spike S6 not run). Whether Jira Cloud answers a missing Create issues permission with 403 (as coded) or with 400 is not verified; a 400 is recorded as `INVALID_REQUEST`.

- An automatic reopen sends no notification; only `failure_assigned` exists (parked).
- Two failed results for one case at the same moment can hit the one-active-failure database guard and return a 500 (MVP).
- Not checked at 375 px in a browser (W6 carry-over).

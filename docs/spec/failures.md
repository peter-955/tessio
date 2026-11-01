# Failures

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.11 · Story prefix FAIL · Index: [README](README.md)

## Purpose

A failure tracks one failing test case from its first failed result until QC verifies the fix. Failures live only in Tessio; there is no external bug tracker. A failed result opens a failure, Dev marks it fixed, a re-run checks it, and QC verifies or reopens it. Server: [server/app/modules/failures](../../server/app/modules/failures). Client: [client/src/modules/failures](../../client/src/modules/failures).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open failures | `failure.view` | all |
| Assign, reassign, unassign | `failure.assign` | Admin, QC, Dev |
| Mark fixed | `failure.mark_fixed` | Admin, Dev |
| Verify or reopen a fixed failure | `failure.verify` | Admin, QC |

## User stories

### FAIL-1 A failed result opens a failure (WBS 3.11.3)

As a Dev, I want every failing case to become a failure automatically, so that nothing is lost between report and fix.

- AC1: When a case result is `failed` (Claude or manual) and the case has no active failure, a new failure opens with status `open`, no assignee, and an `opened` event.
- AC2: When the case already has an `open` or `reopened` failure, the result is added to it (`failed_again` event).
- AC3: When the case's failure is `fixed`, the failed result reopens it automatically (`fixed` → `reopened`, shown as "Automatic").
- AC4: A `blocked` result opens no failure. A `passed` or `skipped` result changes nothing.
- AC5: After a failure is `verified`, the next failed result opens a new failure.
- AC6: A case has at most one active failure (`open`, `fixed` or `reopened`).

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
- AC4: "Timeline" lists the events: Failure opened, Failed again, "{from} → {to}" with who changed it (or Automatic), Assigned to {name}, Unassigned.
- AC5: A failure of another project shows "Failure not found".

### FAIL-4 Mark fixed, verify, reopen (WBS 3.11.3)

As a Dev and then a QC, I want to move a failure through fixed and verified, so that we agree when the bug is gone.

- AC1: "Mark fixed" (`PUT …/failures/{failure_id}/status` with `fixed`) works from `open` or `reopened`.
- AC2: "Verify" (`verified`) and "Reopen" (`reopened`) work only from `fixed`.
- AC3: Any other move gets `INVALID_STATUS_TRANSITION`. `verified` is final.
- AC4: Each change records who and when, adds a `status_changed` event and publishes `failure.changed`.
- AC5: The story cannot be signed off as `passed` while any of its failures is active ([STORY-6](sprints-and-stories.md#story-6-qc-sign-off-wbs-355)).

### FAIL-5 Assign a failure (WBS 3.11.5)

As a QC, I want to assign a failure to the right Dev, so that someone owns the fix.

- AC1: New failures start unassigned.
- AC2: "Assign" / "Reassign" picks any active project member, or Unassigned, and calls `PUT …/failures/{failure_id}/assignee`.
- AC3: The assignee must be an active member (`ASSIGNEE_NOT_ACTIVE_MEMBER`, "Pick an active project member.").
- AC4: A `verified` failure cannot be reassigned (`INVALID_STATUS_TRANSITION`).
- AC5: A change adds an `assigned` or `unassigned` event. Assigning sends `failure_assigned` to the new assignee, unless they assigned it to themselves.
- AC6: A failure whose assignee was deactivated shows "The assignee is deactivated. Reassign this failure."

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
| Event kinds | `opened`, `failed_again`, `status_changed`, `assigned`, `unassigned` | `FailureEventKind` |

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

There is no MCP tool for failures; Claude reads failed cases with `get_failed_cases` ([runs.md](runs.md)).

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown failure or another project's failure |
| `INVALID_STATUS_TRANSITION` | A move not in the table, or reassigning a verified failure |
| `ASSIGNEE_NOT_ACTIVE_MEMBER` | Assignee not an active project member |
| `INVALID_REQUEST` | `assigneeId` and `unassigned` together |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or a write on an archived project |

## Later

- 3.11.4 Comments on a failure.

## Differences from the proposals

- Verify works only from `fixed`, not from `open` (assumption 3.11.3).
- A `blocked` result opens no failure, and a failure after `verified` is a new failure (assumption 3.11.3).
- `reopened` can be marked fixed again; the proposal drew Reopened as an end state.
- The [workflow proposal §3](../discussions/testing-workflow-proposal.md#3-the-workflow-inside-tessio) assigned new failures to the dev. In code they start unassigned and are assigned by hand ([server proposal §15](../discussions/server-proposal.md#15-numbers-and-rules)).

## Open points

- An automatic reopen sends no notification; only `failure_assigned` exists (parked).
- Two failed results for one case at the same moment can hit the one-active-failure database guard and return a 500 (MVP).
- Not checked at 375 px in a browser (W6 carry-over).

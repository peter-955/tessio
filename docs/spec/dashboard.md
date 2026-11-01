# Dashboard

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.4 · Story prefix DASH · Index: [README](README.md)

## Purpose

One page per project that answers "where does the sprint stand, and what needs me?". It shows the current sprint by test status, open gaps, active failures and AC coverage, the recent runs, and a "My work" list for the caller's role. Server read models: [server/app/modules/insights](../../server/app/modules/insights). Client: [client/src/modules/dashboard](../../client/src/modules/dashboard).

## Roles and capabilities

- The sprint panel and My work need `report.view` (every role). Recent runs need `run.view` (every role).
- The My work sections depend on the caller's project role (DASH-3). A workspace admin who is not a member acts as Admin.
- The dashboard writes nothing.

## User stories

### DASH-1 Current sprint panel (WBS 3.4.1)

As a PM or BA, I want the current sprint's testing status at a glance, so that I don't have to open each story.

- AC1: `/projects/[projectKey]` shows "Current sprint" from `GET /api/projects/{project_key}/dashboard`.
- AC2: The current sprint is the `active` sprint with the latest start date. A "Sprint" picker can show any synced sprint (`sprintId`); an unknown sprint id gives "Sprint not found" with "Show the current sprint".
- AC3: The panel shows the number of stories, open gaps, active failures (`open`, `fixed` or `reopened`) and AC covered as a percentage.
- AC4: "Stories by test status" counts the sprint's stories per status: Not started, Ready for test, In test, Passed, Failed.
- AC5: "AC coverage" shows "{covered} of {total} AC covered" and a bar split into Passed, Failed, Blocked, Not run and Uncovered, from the AC status rule in [traceability](traceability.md). Removed AC are not counted.
- AC6: With no active sprint and none picked, the panel says "No active sprint" ("Pick a sprint, or sync with Jira once a sprint starts.").

### DASH-2 Recent runs (WBS 3.4.2)

As a team member, I want the latest runs on the dashboard, so that I see what just happened.

- AC1: "Recent runs" lists the 5 newest runs of the project (`GET /api/projects/{project_key}/runs?limit=5`) with status, story, executor, environment, who started it, when, and "{passed} passed · {failed} failed of {total}".
- AC2: Aborted runs show their reason (no results or inactive).
- AC3: "View all runs" opens `/projects/[projectKey]/runs`. With no runs it says "No runs yet".

### DASH-3 My work per role (WBS 3.4.3)

As a QC, Dev, BA or PM, I want the items waiting for me, so that I know what to do next.

- AC1: `GET /api/projects/{project_key}/my-work` returns the sections for the caller's role:
  - Admin: cases to write, failures to fix, gaps to answer;
  - QC: cases to write, gaps to answer;
  - Dev: failures to fix, gaps to answer;
  - BA and PM: gaps to answer;
  - Viewer: none ("Nothing is assigned to your role.").
- AC2: "Cases to write" has two lists: "AC without a test case" (active AC of the sprint with no linked, non-deprecated case) and "My draft cases" (cases the caller created that are `draft` or `in_review`).
- AC3: "Failures to fix" lists failures assigned to the caller that are `open` or `reopened`.
- AC4: "Gaps to answer" lists open gaps assigned to the caller, or to the caller's role queue when no one is assigned, high severity first.
- AC5: Each list shows at most 20 items with "Showing {count} of {total}" and "View all".
- AC6: Every role sees the number of unassigned failures (`open` or `reopened` with no assignee), linking to the failure list filtered to Unassigned.

### DASH-4 Workspace home (WBS 3.4.1)

As a user, I want `/` to take me to a dashboard, so that I don't start on an empty page.

- AC1: `/` redirects to the last project's dashboard ([SHELL-3](app-shell.md#shell-3-home-route-wbs-312)).

## Rules

- Current sprint: `state` `active`, ordered by `start_at` (latest first, missing dates last), then by Jira sprint id.
- Active failure statuses: `open`, `fixed`, `reopened`. Failures to fix: `open`, `reopened`.
- My work list size: 20 items per section (`MAX_MY_WORK_ITEMS`).
- The sections by role come from `SECTIONS_BY_ROLE` in [my_work.py](../../server/app/modules/insights/typing/constants/my_work.py).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]` | "No active sprint"; empty lists say "Every AC has a case.", "No draft cases.", "No failures to fix.", "No gaps to answer.", "No runs yet" | skeleton per panel | "Could not load the sprint summary." / "Could not load your work." / "Could not load recent runs." + Retry | read-only (nothing to change) | non-member: "Project not found" | dashboard: `run.finished`, `jira.sync_finished`, `gap.changed`, `failure.changed`, `test_case.changed`, `story.changed`; my work: the same except `story.changed`; recent runs: `run.started`, `run.case_recorded`, `run.finished` |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/dashboard?sprintId=` | `report.view` |
| `GET /api/projects/{project_key}/my-work?sprintId=` | `report.view` |
| `GET /api/projects/{project_key}/runs?limit=5` | `run.view` |
| `GET /api/projects/{project_key}/sprints` | `sprint.view` (sprint picker) |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown project, non-member, or a `sprintId` that is not in the project |
| `INVALID_REQUEST` | `sprintId` is not a UUID |

## Later

- 3.4.4 Trend charts across sprints.

## Differences from the proposals

- WBS 3.4.3 says "QC: cases to write". There is no assignee on a test case, so the code reads it as "uncovered AC of the sprint plus my own draft and in-review cases" (assumption 3.4.3).
- When several sprints are active, the code picks the latest started one and offers a picker (assumption 3.4.1).

## Open points

- Not checked in a browser against a running stack, including the 375 px layout (W6 carry-over).

# Traceability

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.7 · Story prefix TRACE · Index: [README](README.md)

## Purpose

Show, for each story, which AC are covered by which test cases and whether each AC passes, fails or has not run yet, from each case's latest result. Server read models: [server/app/modules/insights](../../server/app/modules/insights). Client: [client/src/modules/traceability](../../client/src/modules/traceability) and the DS traceability matrix in [client/src/components/design-system/traceability-matrix](../../client/src/components/design-system/traceability-matrix).

## Roles and capabilities

- Every read here needs `report.view` (every role).
- The "New test case" button in the uncovered-AC warning shows only with `test_case.edit`.
- Nothing here writes data.

## User stories

### TRACE-1 AC × test case matrix (WBS 3.7.1)

As a QC or BA, I want a matrix of AC against test cases, so that I see coverage at a glance.

- AC1: The story's Traceability tab loads `GET /api/projects/{project_key}/stories/{jira_key}/traceability`.
- AC2: Rows are AC in list order, with removed AC last and struck through ("Removed from Jira on {date}"). Columns are the story's non-deprecated cases, by code.
- AC3: A cell is empty ("Not linked") when the case does not cover the AC. A linked cell shows the case's latest result (Passed, Failed, Blocked, Skipped) or "Not run". Draft and In review cases are labelled as such.
- AC4: A case with the Needs review flag is marked "Needs review".
- AC5: Each row ends with the AC status badge (TRACE-3). The status never relies on colour alone.
- AC6: The header shows "{covered} of {total} AC covered" with passed, failed, blocked and not run counts.

### TRACE-2 Uncovered-AC warning (WBS 3.7.2)

As a QC, I want a warning when an AC has no test case, so that I close the gap before testing.

- AC1: When active AC have no linked, non-deprecated case, the tab shows "{count} acceptance criteria have no test case" and "Not covered: {codes}".
- AC2: "New test case" opens the new-case page for that story.
- AC3: The same uncovered AC appear in the QC "My work" list ([DASH-3](dashboard.md#dash-3-my-work-per-role-wbs-343)).

### TRACE-3 AC status from the latest results (WBS 3.7.3)

As a PM, I want each AC's pass or fail status from its cases' latest results, so that I can tell whether the story works.

- AC1: The status is worked out over the AC's linked cases that are not `deprecated`:
  1. no such case: `uncovered`;
  2. keep the cases that are `ready` or already have a result; if none is left: `not_run`;
  3. any latest result `failed`: `failed`;
  4. else any `blocked`: `blocked`;
  5. else any case with no result or a `skipped` result: `not_run`;
  6. else: `passed`.
- AC2: A case's latest result is its newest result in any run, except that a `skipped` result is used only when the case has no other result. A run that does not report a case leaves its previous result in place.
- AC3: The same rule gives the AC impact in each run report ([runs.md](runs.md)) and the dashboard coverage bar.

### TRACE-4 Story progress columns (WBS 3.7.1)

As a PM, I want coverage, open gaps, failures and the last run in the story list, so that I can compare stories.

- AC1: `GET /api/projects/{project_key}/story-progress?sprintId=` returns, per story: AC coverage ("{covered}/{total}", with failing, blocked or uncovered counts, or "All passing"), open gaps, active failures and the last run.
- AC2: The story list shows these columns; a missing value shows "Not available".

### TRACE-5 Latest result per case (WBS 3.7.3)

As a QC, I want each case's latest result in the case list, so that I see what is failing.

- AC1: `GET /api/projects/{project_key}/case-latest-results?storyKey=` returns each case's latest result (status, run, time and version), by the rule in TRACE-3 AC2.
- AC2: The test case list shows it in the "Latest result" column.

### TRACE-6 AC changed in Jira (WBS 3.7.4)

As a QC, I want linked cases flagged when an AC changes in Jira, and removed AC kept, so that history is not lost.

- AC1: The flag and "Mark reviewed" are specified in [CASE-8](test-cases.md#case-8-ac-changed-review-wbs-374).
- AC2: A removed AC keeps its code, text and links, and appears struck through in the matrix and the story detail. It is no longer counted in coverage.

## Rules

- AC statuses: `uncovered`, `not_run`, `passed`, `failed`, `blocked` (`CriterionStatus`).
- Precedence: failed > blocked > not run > passed, after the `uncovered` and `not_run` checks above ([criterion_status.py](../../server/app/modules/insights/utils/criterion_status.py)).
- Coverage counts only active (not removed) AC.
- Latest result order: non-skipped first, then newest.

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| Traceability tab of `/projects/[projectKey]/stories/[jiraKey]` | "No acceptance criteria. Add AC to the story in Jira, then sync." / "No test cases yet. Write test cases and link them to the AC to see coverage." | skeleton | "Could not load traceability." + Retry | no "New test case" | no "New test case" | `run.case_recorded`, `run.finished`, `jira.sync_finished`, `test_case.changed`, `story.changed` |
| Story list columns | "No runs" | per-cell placeholder | "Not available" | – | – | `run.started`, `run.case_recorded`, `run.finished`, `gap.changed`, `failure.changed`, `test_case.changed`, `story.changed`, `jira.sync_finished` |

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/stories/{jira_key}/traceability` | `report.view` |
| `GET /api/projects/{project_key}/story-progress?sprintId=` | `report.view` |
| `GET /api/projects/{project_key}/case-latest-results?storyKey=` | `report.view` |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown project, story or sprint, or a non-member |

## Later

- Nothing in WBS 3.7 is Later.

## Differences from the proposals

- The proposals did not say how to combine several cases into one AC status. The code uses the precedence above, and a `skipped` result never replaces an earlier real result (assumption 4.12).
- Draft and In review cases count as coverage (an AC with only a draft case is `not_run`, not `uncovered`).

## Open points

- Not checked in a running browser (W6 carry-over).

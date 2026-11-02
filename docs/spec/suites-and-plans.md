# Suites and plans

**Status:** Draft · **Updated:** 2026-11-02

WBS 9.1 · Story prefixes SUITE (suites, suite runs) and PLAN (test plans) · Index: [README](README.md)

## Purpose

A regression suite is a named, ordered list of test cases taken from any stories of a project. It lasts across sprints, so last sprint's work can be re-checked without picking the cases again. A suite run executes the suite's Ready cases against one environment, the same way a story run does ([runs.md](runs.md)), and its report groups the results by story. Labels ([CASE-13](test-cases.md#case-13-labels-wbs-91)) help fill a suite. A test plan groups suites and stories for a release or a milestone, shows each case's latest result since the plan opened with the active failures and open gaps that stand in the way, and is signed off once no failure on its cases is active (PLAN-1 to PLAN-5). Plans live in [server/app/modules/plans](../../server/app/modules/plans), which reads suites, stories, cases, results, failures and gaps with its own queries ([postgres_plan_view_reader.py](../../server/app/modules/plans/infrastructure/postgres_plan_view_reader.py)); nothing imports `plans`.

Design record: [competitive features proposal F1](../discussions/competitive-features-proposal.md#f1-regression-suites-test-plans-and-labels-l-wbs-91). Server: [server/app/modules/suites](../../server/app/modules/suites) (suites, their cases, `get_suite_context`) and [server/app/modules/runs](../../server/app/modules/runs) (suite runs: [run_start_gate.py](../../server/app/modules/runs/usecases/run_start_gate.py), [start_run.py](../../server/app/modules/runs/usecases/start_run.py)). The runs module reads suites only through its `SuiteRunScopeReader` port, which the suites module implements ([postgres_suite_run_scope_reader.py](../../server/app/modules/suites/infrastructure/postgres_suite_run_scope_reader.py)). Client: [client/src/modules/suites](../../client/src/modules/suites) (suites list and detail, add cases, add by filter, the Claude command), plus the suite parts of run list, run detail and manual run creation in [client/src/modules/runs](../../client/src/modules/runs) and [client/src/modules/manual-run](../../client/src/modules/manual-run), and [client/src/modules/plans](../../client/src/modules/plans) (plans list and plan detail). Claude side: the [`run-suite` skill](../../claude/skills/run-suite/SKILL.md) (SUITE-8).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open suites | `test_case.view` | all |
| Create, rename, describe and archive a suite; set its cases; add cases by filter | `suite.edit` | Admin, QC |
| MCP `get_suite_context` | `run.view` (+ `story.view`, `test_case.view`, `test_data.view`) | all |
| MCP `start_run(suite=…)` | `run.start` | Admin, QC, Dev |
| Start a manual suite run (`POST …/runs` with `suiteId`) | `run.start` + `run.record_manual` | Admin, QC |
| List and open test plans, with their progress and blockers | `report.view` | all |
| Create and edit a plan, set its items, close it | `plan.edit` | Admin, PM, QC |
| Sign off a plan | `plan.sign_off` | Admin, QC |

An archived project keeps its suites and plans readable; every write gives `PROJECT_ARCHIVED`. Another project's suite or plan is `NOT_FOUND`.

## User stories

### SUITE-1 Create and edit a suite (WBS 9.1)

As a QC, I want named regression suites, so that I can re-run the same set of cases every sprint.

- AC1: `POST /api/projects/{project_key}/suites` with `{"name", "description"?}` creates an empty suite (201). The name is trimmed, 1 to 120 characters; the description is trimmed, up to 2000 characters, and blank means none.
- AC2: Names are unique among the project's suites that are not archived, without case (`SUITE_NAME_ALREADY_USED`, 409), because Claude finds a suite by name (`/tessio:run-suite <name>`). An archived suite's name can be used again. The database guards the rule too (partial unique index `uq_test_suites_project_id_name_active`).
- AC3: `PATCH …/suites/{suite_id}` changes `name` and/or `description` (`"description": null` clears it). Renaming to another active suite's name gives `SUITE_NAME_ALREADY_USED`.
- AC4: `POST …/suites/{suite_id}/archive` archives the suite (200, the detail with `archivedAt`). Archiving an archived suite changes nothing. An archived suite cannot be edited, have its cases changed or be run (`SUITE_ARCHIVED`, 409). A run that is already running keeps running.
- AC5: Every create, edit, archive and case change publishes `suite.changed` with `ids.suiteId`. A request that changes nothing publishes nothing: `PUT …/suites/{suite_id}/cases` with the cases the suite already has, in the same order, writes nothing and publishes nothing.

### SUITE-2 List and open suites (WBS 9.1)

As a team member, I want to see the suites and what is in them, so that I know what a suite run will cover.

- AC1: `GET /api/projects/{project_key}/suites` lists the active suites by name (without case); `?archived=true` adds the archived ones. Each row has `id`, `name`, `description`, `caseCount`, `readyCaseCount`, `archivedAt`, `createdAt` and `lastRun` (`id`, `status`, `startedAt`, `finishedAt`, or null).
- AC2: `GET …/suites/{suite_id}` returns the suite with `createdBy`, `caseCount`, `readyCaseCount`, `lastRun`, `runningRun` (the suite's running run, or null) and its `cases` in suite order: `testCaseId`, `code`, `title`, `status`, `priority`, `isNeedingReview`, `isRunnable`, `storyId`, `storyJiraKey`, `storyTitle`, `position`.
- AC3: A case is runnable (counted in `readyCaseCount`) when it is `ready` and not flagged Needs review.

### SUITE-3 Add cases by filter (WBS 9.1)

As a QC, I want to fill a suite from labels, priorities, a story or a sprint, so that I don't pick fifty cases by hand.

- AC1: `PUT …/suites/{suite_id}/cases` with `{"testCaseIds": [...]}` replaces the suite's cases with that ordered list (0 to 1000). Position is the list order. A case listed twice gives `INVALID_REQUEST`; a case of another project, or an unknown one, gives `UNKNOWN_REFERENCE`. Any case of the project can be listed, in any status. Reordering is a `PUT` with the new order.
- AC2: `POST …/suites/{suite_id}/cases/by-filter` with any of `labels` (names, up to 20), `priorities`, `storyKey` and `sprintId` adds the project's cases that match, in case-number order, after the current cases. Each match is added once: cases already in the suite are left where they are. The reply is `{"addedCount", "suite"}` (the detail).
- AC3: A case matches when it carries every named label (names matched without case and trimmed; an unknown name matches nothing, as on the case list, [CASE-13 AC7](test-cases.md#case-13-labels-wbs-91)), has one of the priorities, belongs to the story, and belongs to a story of the sprint. The filters combine. Deprecated cases never match.
- AC4: No filter gives `INVALID_REQUEST`; an unknown story key or a sprint of another project gives `UNKNOWN_REFERENCE`. More than 1000 cases in the suite gives `INVALID_REQUEST`.
- AC5: The filter runs once and the suite keeps a fixed list. Nothing remembers the filter, so a label can be deleted at any time and the suite keeps its cases ([CASE-13 AC4](test-cases.md#case-13-labels-wbs-91)).

### SUITE-4 Start a suite run (WBS 9.1)

As a Dev or a QC, I want Claude (or me, by hand) to run a suite, so that the regression cases of many stories run in one go.

- AC1: MCP `start_run(suite, environment?, case_ids?, parent_run_id?)` starts a suite run. `suite` is the suite's name (matched without case) or its id. Exactly one of `story_key` and `suite` is needed (`INVALID_REQUEST`). An unknown suite gives `NOT_FOUND`; when only an archived suite has the name, or the id is an archived suite's, the reply is `SUITE_ARCHIVED`.
- AC2: The start is refused with `OPEN_GAPS_BLOCK_RUN` while any story with a case in the suite (skipped cases included) has an open gap. The message is "{n} open gaps block this suite run. Answer them first: " followed by up to 20 of those gaps, separated by "; ", each as "{storyKey} gap {gapId} (assigned to {assignee}): {question}". `{assignee}` is the assignee's name; without an assignee it is "the {Role} role" (Admin, PM, BA, QC, Dev, Viewer), and with neither an assignee nor a role it is "nobody". The question has its whitespace collapsed and is cut to 120 characters, ending with "…" when cut. More than 20 gaps end the message with "; and {n} more".
- AC3: Without `case_ids` the run takes the suite's runnable cases in suite order (SUITE-2 AC3). Cases that are not `ready` are skipped with reason `not_ready`, cases flagged Needs review with reason `needs_review`. The reply then has `skipped_cases` (`code`, `title`, `story_key`, `reason`), and the run keeps them (`runs.skipped_cases`). No runnable case gives `SUITE_EMPTY` (409).
- AC4: With `case_ids` the run takes those cases, in that order. A case not in the suite gives `UNKNOWN_REFERENCE`; a case that is not runnable gives `CASE_NOT_READY`. Nothing is listed as skipped. The `run-suite` skill uses this for runs of at most 50 cases.
- AC5: Only one suite run per suite runs at a time (`SUITE_ALREADY_RUNNING`, 409). Two starts that race both pass the first check; the database index `uq_runs_test_suite_id_running` refuses the second, and it also gets `SUITE_ALREADY_RUNNING`. A suite run doesn't block a story run of the same cases, and a story run doesn't block a suite run.
- AC6: The environment is picked as for a story run (RUN-2 AC4). Each case's current version is fixed in the run.
- AC7: The reply is the story-run reply (RUN-2 AC1) plus `suite` (the name) and, on each case, `story_key`.
- AC8: A suite run never changes a story's test status: it doesn't move stories to `in_test`, and it publishes `run.started` with `ids` `runId` and `suiteId` (no `storyId`) and no `story.changed`.
- AC9: `parent_run_id` re-runs a finished suite run of the same suite: the server takes the parent's failed and blocked cases that are still runnable. A parent of another suite or of a story gives `INVALID_REQUEST`; with no such case left, `NO_FAILED_CASES_TO_RERUN`.
- AC10: `POST /api/projects/{project_key}/runs` with `{"suiteId", "environmentId"?, "testCaseIds"?}` starts a manual suite run under the same rules. Exactly one of `storyKey` and `suiteId` is needed (`INVALID_REQUEST`). The reply has `storyId: null`, `testSuiteId` and `skippedCases`.

### SUITE-5 Finish a suite run and its report (WBS 9.1)

As a QC, I want a suite run's results per story, so that I see which stories regressed.

- AC1: Recording and finishing follow RUN-4, RUN-6 and RUN-8. A result's failure opens on the case's own story ([failures.md](failures.md)). `run.case_recorded` carries the case's `storyId` and the `suiteId`.
- AC2: The report has `stories`: one entry per story with a case in the run, in the order of the story's first case, with `storyId`, `storyJiraKey`, `storyTitle` and the counts of RUN-6 AC4 for that story's cases. Story runs get the one entry for their story too.
- AC3: The report's `skippedCases` are the cases skipped at the start (SUITE-4 AC3). Its failed cases carry `storyJiraKey`.
- AC4: The AC impact lists, for each story of the run, its active AC that are linked to at least one case of the run, with `storyJiraKey`, ordered by story and then AC position. (A story run lists every active AC of its story, as before.)
- AC5: `run.finished` carries `runId`, `suiteId` and `status`. The starter and the project's QC members get a `suite_run_finished` notification ([NOTIF-4 AC3](notifications.md#notif-4-run-finished-wbs-3121)). The stale-run abort (RUN-10) does the same for a suite run.
- AC6: MCP `get_failed_cases(run_id)` for a suite run replies `run_id`, `run_status`, `suite`, `environment` and the cases with `story_key`, so that `rerun-failed` can call `start_run(suite=…, parent_run_id=…)`. `POST …/runs/{run_id}/rerun-failed` re-runs a suite run's failed cases by hand as a suite run.

### SUITE-6 Suite context for Claude (WBS 9.1)

As Claude, I want everything about a suite in one call, so that I can run it without guessing.

- AC1: MCP `get_suite_context(suite)` (name or id, up to 200 characters) returns `suite` (`id`, `name`, `description`), `case_count`, `stories` and `skipped_cases`.
- AC2: `stories` lists each story with a runnable case, in the order of its first case: `key`, `title`, `test_status`, `jira_status`, its active `criteria` (`code`, `text`) and its runnable `cases` in suite order, each in the shape of `get_story_context` (RUN-11 AC1: id, code, title, priority, version, AC codes, business value, preconditions, steps, data keys, file keys, labels).
- AC3: `data`, `missing_data_keys`, `files` and `environments` are built as in `get_story_context`, for the keys and files of all the suite's runnable cases. Secrets appear only as `{{data.key}}`.
- AC4: An unknown suite or another project's suite gives `NOT_FOUND`; an archived suite gives `SUITE_ARCHIVED`.

### SUITE-7 Read models with suite runs (WBS 9.1)

As a team member, I want every page to count suite runs right, so that the numbers stay true.

- AC1: Run list (RUN-1): each row has `testSuiteId` and `testSuiteName`; a suite run has `storyId`, `storyJiraKey` and `storyTitle` null. `GET …/runs?suiteId=` lists one suite's runs. `storyKey=` lists story runs only.
- AC2: Run detail (RUN-7): the same fields, `skippedCases`, and on each case `storyId`, `storyJiraKey` and `storyTitle` (story runs too).
- AC3: Traceability, case latest results, the dashboard coverage and story progress coverage use each case's latest result whatever the run, so suite results count for each case's story. A story's test status and the dashboard's test-status counts never change because of a suite run.
- AC4: Story progress `lastRun` is the newest run that ran a case of the story: a story run, or a run without a story (a suite run or a CI import, [RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)) with one of its cases.
- AC5: Failures, my work (failures to fix, unassigned failures) and failure history read the case's story, so a suite failure shows under its story.
- AC6: A Claude suite run accepts its execution log (RUN-13) like a story run.
- AC7: Story sign-off (`passed`, [sprints-and-stories.md](sprints-and-stories.md)) is refused with `STORY_SIGN_OFF_BLOCKED` while a suite run that holds a case of the story is running, as it is while a story run of the story is running. A running suite run without a case of the story doesn't block it.

### SUITE-8 Run a suite with Claude (WBS 9.1)

As a Dev or a QC, I want to run a suite from Claude Code with one command, so that Claude runs every Ready case of it and I see the results per story.

- AC1: [`/tessio:run-suite <suite> [environment] [case codes]`](../../claude/skills/run-suite/SKILL.md) (Admin, QC and Dev) takes the suite's name or id. A name with spaces is quoted; an unquoted name with spaces is tried once more as the whole argument text after `NOT_FOUND`. Words like `TC-<n>` are case codes, another word is the environment.
- AC2: It starts with `get_suite_context(suite)` and tells the user the case count, the stories and the skipped cases with their reason (`not_ready`, `needs_review`). `NOT_FOUND` and `SUITE_ARCHIVED` stop it; no runnable case stops it before any run.
- AC3: The environment is the argument, else the context's `is_default` one, else the only one, else Claude asks. Every run of the suite uses that environment.
- AC4: The cases run in the context's order (stories in order, then each story's cases), or only the given case codes in the given order. They are split into runs of at most 50 cases. With one run that holds every case, Claude calls `start_run(suite=<id>, environment)` without `case_ids`, so the run keeps its skipped cases (SUITE-4 AC3); otherwise each run gets `case_ids` (SUITE-4 AC4).
- AC5: The runs go one after the other: the next run starts only after `finish_run` of the previous one, because a suite has one running run at a time (SUITE-4 AC5). Each run follows the shared procedure of the story runs ([execute-cases.md](../../claude/skills/run-story-tests/references/execute-cases.md): health check, steps, secrets, diagnosis, one result per case, `finish_run`). Its summary names the run's place ("Run 2 of 3") and the stories with failed or blocked cases.
- AC6: `OPEN_GAPS_BLOCK_RUN` follows the blocked-run procedure ([GAP-6 AC4](readiness-review.md#gap-6-open-gaps-block-runs-wbs-384)). `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY`, a down environment or the user asking to stop end the skill too. `CASE_NOT_READY` or `UNKNOWN_REFERENCE` on a case (the suite changed meanwhile) reloads the context and retries once. `UNKNOWN_REFERENCE` naming an environment ("No active environment named …", archived meanwhile) reloads the context, lists its environments and asks the user which one to use for this run and the later ones. When the skill stops before the last run, it gives the command for the cases that did not run: `/tessio:run-suite "<suite name>" <environment> <case codes>`.
- AC7: At the end it reports per story the passed, failed and blocked cases, the skipped cases, each run id with its status and missing screenshots, and `/tessio:rerun-failed <run-id>` for each run with failures. `rerun-failed` re-runs a suite run's failures with `start_run(suite=…, parent_run_id=…)` (SUITE-5 AC6).
- AC8: [`/tessio:rerun-failed <run-id>`](../../claude/skills/rerun-failed/SKILL.md) keeps the 50-case limit for a suite run, whose parent may be a manual suite run of any size (SUITE-4 AC10). With 50 failed or blocked cases or fewer, it starts one child run with `parent_run_id`. With more, it calls `get_suite_context` and keeps the failed cases still in the suite's runnable cases, in the parent's order. If 50 or fewer are left, it starts one child run with `parent_run_id`. Otherwise it splits them into runs of at most 50 and starts each with `start_run(suite=<id>, environment, case_ids=…)`, one after the other as in AC5. `start_run` refuses `parent_run_id` together with `case_ids` (`INVALID_REQUEST`, [runs.md](runs.md)), so these runs have no parent link. Each `finish_run` summary names the parent run instead. A story run's re-run is always one run.

### PLAN-1 Create and edit a test plan (WBS 9.1)

As a QC or a PM, I want a test plan for a release, so that everyone sees what has to be tested before it ships.

- AC1: `POST /api/projects/{project_key}/plans` with `{"name", "description"?, "targetDate"?, "environmentId"?}` creates an `open` plan with no items (201, the detail of PLAN-3 AC2). The name is trimmed, 1 to 120 characters, and need not be unique. The description is trimmed, up to 2000 characters, and blank means none. `targetDate` is a date (`YYYY-MM-DD`). `environmentId` must be an active environment of the project (`UNKNOWN_REFERENCE`).
- AC2: `PATCH …/plans/{plan_id}` changes any of `name`, `description`, `targetDate` and `environmentId`; `null` clears the description, the target date or the environment. Only an `open` plan can be edited (`PLAN_NOT_OPEN`, 409).
- AC3: Every create, edit that changes something, item change, sign-off and close publishes `plan.changed` with `ids.planId`. A `PATCH` that changes nothing publishes nothing.

### PLAN-2 Choose what a plan covers (WBS 9.1)

As a QC or a PM, I want to put regression suites and sprint stories in a plan, so that the plan covers both the new work and the regression.

- AC1: `PUT …/plans/{plan_id}/items` with `{"items": [{"suiteId": …} | {"storyId": …}, …]}` replaces the plan's items with that ordered list (0 to 100). Position is the list order. Each item names exactly one of `suiteId` and `storyId` (a 422 body validation error, "Give exactly one of suiteId or storyId."). A suite or a story listed twice gives `INVALID_REQUEST`; one of another project, or an unknown one, gives `UNKNOWN_REFERENCE`. An archived suite can be listed and stays in the plan with its frozen cases.
- AC2: Only an `open` plan's items can change (`PLAN_NOT_OPEN`).
- AC3: The plan's cases are, in item order, each suite's cases in suite order and each story's cases in case-number order. A case that two items bring is listed once, at its first place. Deprecated cases are left out; cases in any other status (draft, in review, ready, flagged Needs review) are in, so a plan shows the cases that are not ready yet.

### PLAN-3 Follow a plan's progress (WBS 9.1)

As a team member, I want to see how far a plan is, so that I know what still has to pass and what blocks it.

- AC1: `GET /api/projects/{project_key}/plans?status=` lists the project's plans, newest first; `status` (`open`, `signed_off`, `closed`) keeps one status. Each row has `id`, `name`, `description`, `status`, `targetDate`, `environmentId`, `environmentName`, `itemCount`, `counts` (AC5), `createdBy`, `createdAt`, `signedOffAt` and `closedAt`.
- AC2: `GET …/plans/{plan_id}` returns the plan with `createdBy` and `createdByName`, `signedOffBy`, `signedOffByName` and `signedOffAt`, `closedBy`, `closedByName` and `closedAt`, its `items` and its `progress`. Each item has `position`, `kind` (`suite` or `story`), `suiteId`, `storyId`, `name` (the suite's name or the story's title), `storyJiraKey`, `archivedAt` (a suite's) and `caseCount` (its cases that are not deprecated).
- AC3: `progress.cases` lists the cases of PLAN-2 AC3 with `testCaseId`, `code`, `title`, `status`, `priority`, `isNeedingReview`, `storyId`, `storyJiraKey`, `storyTitle`, `latestResult` (`caseResultId`, `runId`, `status`, `recordedAt`, or null when the case has not run) and `activeFailureId` and `activeFailureStatus` (or null).
- AC4: A case's latest result is its newest result recorded since the plan was created, from any run: a story run, a suite run, by Claude or by hand. A `skipped` result counts only when the case has no other result in that time, as on traceability ([SUITE-7 AC3](#suite-7-read-models-with-suite-runs-wbs-91)). A data-driven case's result in a run is its worst iteration, whatever the order its iterations were recorded in, like the other latest-result read models ([RUN-14 AC6](runs.md#run-14-shared-steps-and-iterations-in-a-run-wbs-92)). When the plan has an environment, only runs on that environment count. A signed-off plan counts the results up to its sign-off, and a plan closed without a sign-off the results up to its close, so their numbers no longer move.
- AC5: `progress.counts` has `total`, `passed`, `failed`, `blocked`, `skipped` and `notRun` (cases with no latest result).
- AC6: `progress.failures` lists the active failures (`open`, `fixed`, `reopened`) of the plan's cases, oldest first: `failureId`, `testCaseId`, `code`, `title`, `storyJiraKey`, `status`, `assigneeId`, `assigneeName`, `createdAt`. `progress.gaps` lists the open gaps of every story with a case in the plan and of every story item (also a story with no case left), oldest first: `gapId`, `storyId`, `storyJiraKey`, `question`, `severity`, `assigneeId`, `assigneeName`, `assigneeRole`, `createdAt`. Failures and gaps show today's state, whatever the plan's status.

### PLAN-4 Sign off a plan (WBS 9.1)

As a QC, I want to sign off a plan when its cases pass, so that the release has a recorded go.

- AC1: `POST …/plans/{plan_id}/sign-off` (`plan.sign_off`: Admin, QC) moves an `open` plan to `signed_off` and records `signedOffBy` and `signedOffAt`. The reply is the detail of PLAN-3 AC2.
- AC2: It is refused with `PLAN_FAILURES_ACTIVE` (409) while any case of the plan has an active failure ("Resolve the {n} active failures on this plan's cases before signing it off."), as story sign-off is refused today ([sprints-and-stories.md](sprints-and-stories.md)). Failures of cases outside the plan don't block. Open gaps, cases that have not run and running runs don't block; the plan page shows them so the QC decides.
- AC3: A plan that is already `signed_off` or `closed` gives `PLAN_NOT_OPEN`.
- AC4: It publishes `plan.changed` and then `plan.signed_off`, both with `ids.planId`, on the Redis live events. W11 webhooks subscribe to `plan.signed_off`.

### PLAN-5 Close a plan (WBS 9.1)

As a QC or a PM, I want to close a plan that is done or dropped, so that the list shows what is still going on.

- AC1: `POST …/plans/{plan_id}/close` (`plan.edit`) closes an `open` or a `signed_off` plan and records `closedBy` and `closedAt`. A signed-off plan keeps its sign-off. Closing a closed plan gives `PLAN_NOT_OPEN`.
- AC2: Closed is final: nothing reopens a plan. A closed plan stays readable.
- AC3: It publishes `plan.changed`.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Suite name | 1 to 120 characters, trimmed, unique without case among active suites | `MAX_SUITE_NAME_LENGTH`, `uq_test_suites_project_id_name_active` |
| Suite description | up to 2000 characters | `MAX_SUITE_DESCRIPTION_LENGTH` |
| Cases per suite | 1000 | `MAX_SUITE_CASES` |
| Labels per filter | 20 | `MAX_FILTER_LABELS` |
| Suite reference in MCP (`get_suite_context(suite)`, `start_run(suite)`) | name or id, 1 to 200 characters | `MAX_SUITE_REFERENCE_LENGTH` (in the suites and the runs modules) |
| Running runs per suite | 1 | `uq_runs_test_suite_id_running` |
| Story or suite | a run has exactly one of `story_id` and `test_suite_id` | `ck_runs_story_or_suite` |
| Skip reasons | `not_ready`, `needs_review` | `SkipReason` |
| Gaps listed in `OPEN_GAPS_BLOCK_RUN` | 20, questions cut to 120 characters | `MAX_LISTED_BLOCKING_GAPS`, `MAX_BLOCKING_GAP_QUESTION_LENGTH` |
| Plan name | 1 to 120 characters, trimmed, not unique | `MAX_PLAN_NAME_LENGTH` |
| Plan description | up to 2000 characters | `MAX_PLAN_DESCRIPTION_LENGTH` |
| Items per plan | 100 | `MAX_PLAN_ITEMS` |
| Plan item | exactly one of suite and story; each suite and each story once per plan | `ck_test_plan_items_suite_or_story`, unique (`test_plan_id`, `test_suite_id`) and (`test_plan_id`, `story_id`) |
| Plan status | `open` → `signed_off` → `closed`, or `open` → `closed` | `PlanStatus` |

- Tables: `test_suites` (`project_id`, `name`, `description`, `archived_at`, `created_by`) and `test_suite_cases` (`test_suite_id`, `test_case_id`, `position`), migration `0024_create_suites`. The same migration makes `runs.story_id` nullable and adds `runs.test_suite_id` and `runs.skipped_cases`. Its downgrade first deletes every suite run with its run cases, case results, step results, run files and run log, the failures a suite run opened (with their events and `failure_assigned` notifications) and the `suite_run_finished` notifications; a failure opened by a story run whose latest result came from a suite run falls back to its newest story-run result, and a run whose parent was a suite run loses its parent link.
- Tables: `test_plans` (`project_id`, `name`, `description`, `target_date`, `environment_id`, `status`, `signed_off_by`, `signed_off_at`, `closed_by`, `closed_at`, `created_by`) and `test_plan_items` (`test_plan_id`, `test_suite_id` or `story_id`, `position`), migration `0025_create_plans`. Deleting a plan's row removes its items (`ON DELETE CASCADE`); no route deletes a plan.

## Screens and states

Suites: client module [client/src/modules/suites](../../client/src/modules/suites), on the *Suites* sidebar entry (`test_case.view`). Writes need `suite.edit` (Admin, QC) in a project that is not archived; other roles see the same pages read-only.

- **Suites list** (`/projects/[projectKey]/suites`): a table with each suite's name (linking to the suite) and description, "{n} cases" and "{n} ready to run", the last run (its status badge and start time, linking to the run, or "Not run yet") and the creation date. *Show archived suites* adds the archived ones (`?archived=true`) with an *Archived* badge. *New suite* opens a dialog with a name (required, trimmed, up to 120 characters) and a description (up to 2000 characters); `SUITE_NAME_ALREADY_USED` shows on the name field, and after the create the browser opens the new suite.
- **Suite detail** (`/projects/[projectKey]/suites/[suiteId]`):
  - Header: name, description, "{n} cases · {n} ready to run". Actions: *Start manual run* (opens `/runs/new?suite=<id>`; shown with `run.start` + `run.record_manual` while the suite is active, has a runnable case and no running run), *View runs* (the run list filtered by the suite) and a menu with *Edit* and *Archive* (`suite.edit`). *Archive* asks first; an archived suite shows "This suite is archived" and loses every write action and the Claude command. A running run shows "A run of this suite is in progress" with *Open the run*.
  - *Cases*: the cases in suite order, each with its code (linking to the case), title, story (linking to the story), status and priority badges, *Needs review*, and "Skipped in runs" for a case that is not runnable (SUITE-2 AC3). With `suite.edit` each row has a drag handle: drag it to another row, or focus it and press the up and down arrow keys; a screen reader hears "Moved to position {n} of {total}". The row menu has *Move up*, *Move down*, *Move to the top*, *Move to the bottom* and *Remove from the suite*. The new order shows at once and is saved with `PUT …/cases`; moves made while a save runs are sent after it, the last order winning. *Remove from the suite* shows "{code} removed from the suite" only once a save without the case succeeds. A refused save puts the server's order back and shows the reason as a toast, with no "removed" toast.
  - *Add cases*: search by code or title and narrow to one story; the project's cases that are not deprecated are listed, the suite's own cases checked and disabled ("Already in the suite"). *Add cases* appends the picked cases at the end (`PUT …/cases`); more than 1000 cases in all disables it.
  - *Add by filter*: labels (every one must match), priorities, a story and a sprint; at least one is needed. It explains that the filter runs once and the suite keeps a fixed list (SUITE-3). The toast says "{n} cases added" or "No new case matched the filter."
  - *Run with Claude*: the command to copy, `/tessio:run-suite <name>`. A name with a space is quoted, and a name with a double quote uses the suite's id instead, so the skill always finds the suite (SUITE-8 AC1).
  - *Last run*: the last run's status and start time, linking to the run.
- **Run list** (RUN-1): a suite run shows a *Suite* badge and the suite's name (linking to the suite) in the Story column. A *Suite* filter (the project's suites, archived ones marked "(archived)") lists one suite's runs (`?suite=<id>` in the URL, `suiteId=` to the server); picking a suite clears the story filter and the other way round. The filter is hidden while the project has no suite. The dashboard's recent runs show the suite's name for a suite run.
- **Run detail** (RUN-7): a suite run's title is "Suite run · {name}" with *Open the suite*. Its results are grouped by story, in the order of each story's first case: a heading with the story key and title (linking to the story) and the story's counts, then its case cards. Below them, *Skipped cases* lists the cases skipped at the start with their reason (*Not Ready*, *Needs review*). The report adds *Results by story* (`report.stories`) above the failed cases, the story key on each failed case, and the skipped cases. A story run's page is unchanged.
- **New manual run** (`/projects/[projectKey]/runs/new`): *What to run* chooses *A story* or *A suite* (`?suite=<id>` preselects the suite). A preselected suite that is not in the list (an archived suite, or while the list loads) is named from the loaded suite, never by its id; until the suite loads the field is empty. For a suite: the active suites to pick from, the environment, the suite's runnable cases (all checked; each labelled with code, title and story key) and "{n} cases will be skipped" with each skipped case and its reason. A running run of the suite shows a warning with *Open the run* and disables *Start*. With every case checked the start sends `{"suiteId", "environmentId"}`, so the run keeps its skipped cases (SUITE-4 AC3); with some left out it also sends `testCaseIds` (SUITE-4 AC4). `OPEN_GAPS_BLOCK_RUN` says the gaps on the suite's stories must be answered first (in Tessio or with `/tessio:answer-gaps`); `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY` and `SUITE_ARCHIVED` have their own messages. The recording page's title is "Manual run · {suite name}" for a suite run.
- **Notifications**: `suite_run_finished` shows "Suite run passed: {name}" (failed, aborted) with the counts, the suites icon, and links to the run.

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/suites` | "No suites yet" + *New suite* when allowed; read-only: "A QC or an Admin creates the project's regression suites." | skeleton | "Suites could not be loaded" + Try again | *New suite* hidden | *New suite* only with `suite.edit` | `suite.changed`, `test_case.changed`, `run.started`, `run.finished` |
| `/projects/[projectKey]/suites/[suiteId]` | "No cases in this suite" | skeleton | "The suite could not be loaded" + Try again; "Suite not found" for an unknown id, a malformed id or another project's suite | project or suite archived: no handles, menus, add buttons or manual start | handles, menus and add buttons only with `suite.edit`; manual start only with `run.start` + `run.record_manual` | `suite.changed`, `test_case.changed`, `run.started`, `run.finished` |

Plans: client module [client/src/modules/plans](../../client/src/modules/plans), on the *Plans* sidebar entry (`report.view`).

- **Plans list** (`/projects/[projectKey]/plans`): a status filter (All, Open, Signed off, Closed; the server filters with `?status=`), and a table with each plan's name and description, status badge, a stacked progress bar (passed, failed, blocked, skipped as shares of all the plan's cases; the rest of the bar is "not run") with "{passed} of {total} cases passed", target date, environment ("Any environment" when none) and how many suites and stories it covers. *New plan* (`plan.edit`, not in an archived project) opens a dialog with name (required, up to 120 characters), description, target date and environment (active environments; "only results of runs on this environment count"); after the create the browser opens the new plan.
- **Plan detail** (`/projects/[projectKey]/plans/[planId]`):
  - Header: name, description, status badge, target date, environment, and who created, signed off and closed the plan, and when.
  - Actions, each shown only when it applies: *Edit* and *Choose suites and stories* (`plan.edit`, open plan), *Close plan* (`plan.edit`, open or signed-off plan, with a confirmation that closing is final), *Sign off* (`plan.sign_off`, open plan). None shows in an archived project, which shows a read-only note instead.
  - *Choose suites and stories*: two searchable pickers, regression suites (the project's active suites, plus an archived suite already in the plan) and stories. Saving replaces the items (PLAN-2): the picked suites first, then the picked stories, each in the order picked. More than 100 picks disable Save.
  - *Sign off* opens a confirmation. While any case of the plan has an active failure it says "Resolve the {n} active failures on this plan's cases before signing it off." and the confirm button is disabled (PLAN-4 AC2). Otherwise it warns about cases that have not run and open gaps, which don't block. A refusal from the server (failures that appeared meanwhile, a plan that is no longer open) shows as a toast and the page reloads the plan.
  - *Progress* card: "{n}% passed", the large progress bar, a count badge per status (passed, failed, blocked, skipped, not run), and which results count: "since {created}" for an open plan, "up to the sign-off" or "up to the close" once the numbers are frozen (PLAN-3 AC4).
  - *Cases by status*: tabs All, Failed, Blocked, Not run, Skipped, Passed with their counts, and a table of the cases (code and title linking to the case, a badge for a case that is not Ready and for *Needs review*, the story, the latest result linking to its run, when it was recorded, and the active failure's status linking to the failure).
  - *Blockers*: the active failures (linking to each failure, with status, story and assignee) and the open gaps (question, severity, story linking to its Gaps tab, assignee or assigned role).
  - *What the plan covers*: each suite and story item, with its kind, a link to the suite or story, an *Archived* badge and its case count.

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/plans` | "No test plans yet" + *New plan* when allowed; filtered: "No plan has this status" + *Show all plans* | skeleton | "The plans could not be loaded." + Try again | *New plan* hidden | *New plan* only with `plan.edit` | `plan.changed`, `run.case_recorded`, `run.finished`, `suite.changed`, `test_case.changed`, `story.changed` |
| `/projects/[projectKey]/plans/[planId]` | "This plan covers no suite or story yet."; "Add suites or stories to see their cases here."; no failures, no gaps | skeleton | "The plan could not be loaded." + Try again; "Plan not found" for an unknown id, a malformed id or another project's plan | actions hidden, read-only note | each action only with its capability and plan status | `plan.changed`, `run.case_recorded`, `run.finished`, `failure.changed`, `gap.changed`, `suite.changed`, `test_case.changed`, `story.changed` |

`plan.signed_off` refreshes nothing in the client: the server publishes `plan.changed` with it.

## API

| Method and path or MCP tool | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/suites?archived=` | `test_case.view` |
| `POST /api/projects/{project_key}/suites` | `suite.edit` |
| `GET /api/projects/{project_key}/suites/{suite_id}` | `test_case.view` |
| `PATCH /api/projects/{project_key}/suites/{suite_id}` | `suite.edit` |
| `POST /api/projects/{project_key}/suites/{suite_id}/archive` | `suite.edit` |
| `PUT /api/projects/{project_key}/suites/{suite_id}/cases` | `suite.edit` |
| `POST /api/projects/{project_key}/suites/{suite_id}/cases/by-filter` | `suite.edit` |
| `GET /api/projects/{project_key}/runs?suiteId=` | `run.view` |
| `POST /api/projects/{project_key}/runs` with `suiteId` | `run.start` + `run.record_manual` |
| MCP `get_suite_context(suite)` | `run.view` |
| MCP `start_run(suite, environment?, case_ids?, parent_run_id?)` | `run.start` |
| `GET /api/projects/{project_key}/plans?status=` | `report.view` |
| `POST /api/projects/{project_key}/plans` | `plan.edit` |
| `GET /api/projects/{project_key}/plans/{plan_id}` | `report.view` |
| `PATCH /api/projects/{project_key}/plans/{plan_id}` | `plan.edit` |
| `PUT /api/projects/{project_key}/plans/{plan_id}/items` | `plan.edit` |
| `POST /api/projects/{project_key}/plans/{plan_id}/sign-off` | `plan.sign_off` |
| `POST /api/projects/{project_key}/plans/{plan_id}/close` | `plan.edit` |
| `POST /api/projects/{project_key}/plans/{plan_id}/export` (Markdown or PDF report, [INS-7](insights.md#ins-7-export-a-run-plan-or-story-report-wbs-95-3107)) | `report.view` |

## Errors

| ErrorCode | When |
| --- | --- |
| `SUITE_NAME_ALREADY_USED` (409) | Create or rename to the name of another active suite |
| `SUITE_ARCHIVED` (409) | Editing, changing the cases of, running or reading the context of an archived suite |
| `SUITE_EMPTY` (409) | A suite run with no runnable case |
| `SUITE_ALREADY_RUNNING` (409) | Starting a suite run while one of the same suite runs |
| `OPEN_GAPS_BLOCK_RUN` (409) | An open gap on a story with a case in the suite |
| `CASE_NOT_READY` (409) | A chosen case that is not runnable |
| `PLAN_FAILURES_ACTIVE` (409) | Signing off a plan while a case of it has an active failure |
| `PLAN_NOT_OPEN` (409) | Editing, changing the items of or signing off a plan that is signed off or closed; closing a closed plan |
| `UNKNOWN_REFERENCE` (422) | A case of another project in `PUT …/cases`; a chosen case not in the suite; an unknown story or foreign sprint in the filter; a plan item's suite or story of another project; a plan environment that is not an active one of the project |
| `INVALID_REQUEST` (422) | A case listed twice; no filter; more than 1000 cases; both or neither of story and suite; a parent run of another suite or story; a suite or story listed twice in a plan; more than 100 plan items (a plan item with both or neither of `suiteId` and `storyId` is a 422 body validation error) |
| `NOT_FOUND` (404) | Unknown suite or another project's suite; unknown plan or another project's plan |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or a write on an archived project |

## Later

- Suites that refresh themselves from a saved filter ([proposal §6](../discussions/competitive-features-proposal.md#6-not-in-this-proposal)).
- Unarchiving a suite.
- Reopening a closed plan, deleting a plan, and starting a run from a plan.
- MCP tools for plans (Claude reads a plan's progress through the web page today).

## Differences from the proposals

- The proposal and plan name the gap refusal `GAPS_OPEN`. The code reuses `OPEN_GAPS_BLOCK_RUN`, the code story runs already return, which the skills and the client already handle (W10.PRE).
- The plan's label rule "delete is refused while a suite filter uses the label" doesn't apply: the filter is not stored (SUITE-3 AC5).
- `test_suite_cases.suite_id` in the proposal is `test_suite_id` in the code.
- Skipped cases also cover cases that are not `ready` (draft, in review, deprecated), not only Needs review, and they are stored on the run so the report can list them.
- `runs.executor` accepts `script` and `ci` in the database since migration 0024, so `runs` is migrated once. The API's `RunExecutor` still has only `claude` and `manual`; W11 (`ci`) and W12 (`script`) add the values with their features.
- A suite run's run-finished notification is a new kind, `suite_run_finished`, rather than `run_finished` with a null story, so `run_finished` keeps its shape.
- `test_plan_items.suite_id` in the proposal is `test_plan_items.test_suite_id` in the code, and items have a `position`.
- Plans also record `closed_by` and `closed_at`, which the proposal doesn't list, so the page shows who closed a plan.
- "Since the plan opened" means since the plan was created: a plan is `open` from its creation and never reopens. The proposal doesn't say what a plan's environment does; here only runs on that environment count (PLAN-3 AC4), and a signed-off or closed plan keeps the results it had then.
- The plan's sign-off rule is only "no active failure on its cases", as the proposal says; unlike story sign-off, a running run doesn't block it.

## Open points

- Not checked against a running stack: a real Claude session running a suite through the `run-suite` skill (SUITE-8: only the plugin file tests and `claude plugin validate` check it), and the suites screens (checked by Vitest only, not in a browser). Drag and drop is tested with synthetic drag events; a real browser drag is not verified.
- *Open gaps* on a suite's stories are not listed before a manual suite run starts; the start is refused with `OPEN_GAPS_BLOCK_RUN` and a translated message, without the server's list of gaps.
- The plans screens are checked by Vitest only, not in a browser against a running stack. No webhook subscribes to `plan.signed_off` yet (W11.T4).

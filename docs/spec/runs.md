# Runs

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.10 · Story prefix RUN · Index: [README](README.md)

## Purpose

A run executes a story's Ready test cases, or a regression suite's ([suites-and-plans.md](suites-and-plans.md)), against one environment and keeps a result for every case and step. Claude runs them on the developer's machine through Tessio's MCP server (`/mcp`), with a screenshot for every step. A tester can also run them by hand in the UI. The server builds the report when the run finishes. Tessio never runs a browser itself. Server: [server/app/modules/runs](../../server/app/modules/runs) (REST and MCP) and [server/app/modules/story_context](../../server/app/modules/story_context) (`get_story_context`, `get_test_file`). Client: [client/src/modules/runs](../../client/src/modules/runs) and [client/src/modules/manual-run](../../client/src/modules/manual-run). Claude side: the [Tessio plugin](../../claude/README.md).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open runs, MCP `get_failed_cases` | `run.view` | all |
| MCP `get_story_context` | `story.view` (+ `test_case.view`, `test_data.view`) | all |
| MCP `get_suite_context` | `run.view` (+ `story.view`, `test_case.view`, `test_data.view`) | all |
| MCP `start_run`, `record_case_result`, `finish_run`, `get_test_file`; screenshot upload link | `run.start` | Admin, QC, Dev |
| Start, record and finish a manual run; manual re-run; evidence upload | `run.start` + `run.record_manual` (finish: `run.record_manual`) | Admin, QC |
| Finish or record a run someone else started | `run.finish_any` | Admin |

Every MCP tool needs a personal API token for the project ([AUTH-10](authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326)) and the current plugin: a call whose `X-Tessio-Plugin-Version` header is missing, unreadable or older than the plugin this server serves gets `PLUGIN_OUTDATED` with the update command. The token is checked first, and the sent version is saved on it, so the [AI Harness](ai-harness.md) shows the plugin as out of date ([ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)). Viewer tokens can call only the read tools (`get_story_context`, `get_suite_context`, `get_open_gaps`, `get_failed_cases`); PM and BA tokens can also call `raise_gaps`. Admin and QC tokens can also call `check_draft_cases` and `create_draft_cases` ([test-cases.md](test-cases.md#case-10-claude-imports-cases-from-any-file-wbs-369-58-59)).

## User stories

### RUN-1 Run list (WBS 3.10.1, 3.10.8)

As a team member, I want every run with a status filter, so that I find the one I need.

- AC1: `/projects/[projectKey]/runs` lists runs, newest first, with started time, story, status (Running, Passed, Failed, Aborted), executor (Claude, Manual), environment, who started it, results ("{n} passed", "{n} failed", "{n} blocked", "{n} skipped", "{n} not reported") and duration.
- AC2: Filters: status (including Aborted) and story (`status`, `storyKey`). "Clear filters" resets them. The API also takes `suiteId` (a suite's runs); `storyKey` lists story runs only.
- AC2b: Each row also has `testSuiteId` and `testSuiteName`. A suite run has `storyId`, `storyJiraKey` and `storyTitle` null ([SUITE-7](suites-and-plans.md#suite-7-read-models-with-suite-runs-wbs-91)). The run list shows a *Suite* badge and the suite's name for a suite run, and filters by suite ([suites-and-plans.md, Screens and states](suites-and-plans.md#screens-and-states)).
- AC3: The list returns 50 runs by default, at most 200 (`limit`); the page says "Showing the {count} most recent runs."
- AC4: An aborted run shows its reason: "No results were reported" (`no_results`) or "No activity for 4 hours" (`inactive`).
- AC5: A re-run shows "Re-run of an earlier run" with a link to its parent; a parent lists its re-runs.
- AC6: The story detail has a Runs tab with the story's runs.

### RUN-2 Start a Claude run (WBS 3.10.3)

As a Dev, I want Claude to start a run for a story, so that the Ready cases are executed in my browser.

- AC1: `start_run(story_key, environment?, case_ids?, parent_run_id?)` creates a run with executor `claude` in the token's project and returns the run id, the environment name, `base_url`, `health_check_url`, and each case with its id, code, title, fixed version, preconditions and steps.
- AC2: It is refused while any gap on the story is open (`OPEN_GAPS_BLOCK_RUN`) and while the story already has a `running` run (`RUN_ALREADY_RUNNING`).
- AC3: Without `case_ids` it takes every `ready` case of the story; none gives `NO_READY_CASES`. With `case_ids`, a case not on the story gives `UNKNOWN_REFERENCE` and a case that is not `ready` gives `CASE_NOT_READY` ("TC-4 is not Ready.").
- AC4: The environment is picked in this order: the one named (matched without case; unknown or archived gives `UNKNOWN_REFERENCE`); the parent run's environment; the project default; the only active environment. Otherwise `INVALID_REQUEST` lists the names to pick from.
- AC5: Each case's current version is fixed in the run, so later edits do not change what the run executes. Its steps are fixed too, with shared steps expanded ([RUN-14](#run-14-shared-steps-and-iterations-in-a-run-wbs-92)).
- AC6: The story moves to `in_test`, and `run.started` and `story.changed` are published.
- AC7: `start_run` takes `suite` (a suite name or id, 1 to 200 characters) instead of `story_key` for a suite run ([SUITE-4](suites-and-plans.md#suite-4-start-a-suite-run-wbs-91)); exactly one of the two is needed (`INVALID_REQUEST`). A suite run never moves a story to `in_test`.

### RUN-3 Health check before the run (WBS 3.10.3)

As a Dev, I want Claude to check the environment is up first, so that a down server is not reported as failed cases.

- AC1: Claude calls the `health_check_url` (or `base_url` when there is none) itself with `curl`. The server never calls it.
- AC2: When it is down, Claude calls `finish_run` with no case results and a summary such as "Environment down: <url> <code>"; the run ends `aborted` with reason `no_results`.

### RUN-4 Record a case result (WBS 3.10.2, 3.10.3)

As Claude, I want to record one result per case with every step's outcome, so that the team sees progress case by case.

- AC1: `record_case_result(run_id, case_id, status, duration_ms, steps[])` records one case. Each step has `order`, `status` (`passed`, `failed`, `blocked`, `skipped`), `actual_result`, an optional `error` and an optional local `screenshot_path`. 1 to 200 steps per call.
- AC2: Only the person who started the run may record (`RUN_NOT_OWNED`), only while it is `running` (`RUN_NOT_RUNNING`), and only once per case and iteration (`CASE_RESULT_EXISTS`). `iteration` (default 0) is the data row of a data-driven case ([RUN-14](#run-14-shared-steps-and-iterations-in-a-run-wbs-92)).
- AC3: A step order that is not in the run's fixed steps (RUN-14 AC2), or appears twice, gives `INVALID_REQUEST`. Steps the call leaves out are saved as `skipped`.
- AC4: Actual results and errors are masked against the environment's secret values (`••••`).
- AC5: Each step with a `screenshot_path` gets a pending screenshot file. The reply is only `{"case_result_id": "…"}` (about 30 tokens).
- AC5b: A step may also carry a diagnosis: `page_url` (up to 2000 characters), `console_errors` (up to 5, each up to 500 characters) and `failed_requests` (up to 5: `method`, `path`, `status`, `excerpt` up to 500 characters). Query strings and fragments are dropped from the page URL and request paths, the method is upper-cased, and every text is masked against the environment's secrets. The case may carry `suspected_cause` (`app_bug`, `test_data`, `environment`, `test_case`, `unknown`) and `cause_reason` (up to 500 characters); they are kept only when the case status is `failed` or `blocked`. The `run-story-tests` skill fills them on the failed or blocked step after reading the console and the network.
- AC6: The run's last activity time is updated, `run.case_recorded` is published, and a `failed` result opens or updates a failure ([failures.md](failures.md)). The event's `storyId` and the failure's story are the case's own story; a suite run's event also has `suiteId`.
- AC7: After the result is saved, the runs module asks for a flaky recompute of the case through its `FlakyRecomputeRequester` port: one `test_cases.recompute_flaky` job on the `maintenance` queue with `{"testCaseId": "…"}` ([CASE-14](test-cases.md#case-14-flaky-cases-and-quarantine-wbs-913)). A manual result (RUN-8 AC3) does the same. A refused result enqueues nothing. If Redis cannot be reached, the result stays recorded, a warning is logged, and the nightly sweep catches the case up.

### RUN-5 Screenshot upload by the hook (WBS 3.10.2)

As a Dev, I want each step's screenshot uploaded without costing model tokens, so that every step has evidence.

- AC1: After each `record_case_result`, the plugin's `PostToolUse` hook reads the step paths from the tool input and the `case_result_id` from the reply.
- AC2: It asks `POST /api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload` (Bearer API token) for a signed POST. The link lasts 1 hour, allows image types up to 20 MB, and writes under `projects/{project_id}/screenshot/{case_result_id}/`. Only the run's starter may ask (`RUN_NOT_OWNED`).
- AC3: The hook uploads each file as `<step order>.<ext>`. Claude in Chrome's JPEGs go as they are; other formats are converted with `sips` (macOS) or `cwebp`.
- AC4: Uploads that fail are kept in `~/.tessio/pending-uploads.jsonl` and retried the next time the hook runs.

### RUN-6 Finish a run and build the report (WBS 3.10.6)

As Claude, I want to close the run with a short summary, so that the report is ready for the team.

- AC1: `finish_run(run_id, summary?)` (summary up to 4000 characters) is allowed for the starter, or anyone with `run.finish_any`, while the run is `running`.
- AC2: The server checks the uploaded screenshots: a pending screenshot whose object exists becomes uploaded; one that never arrived is marked missing.
- AC3: The run status comes from the results: no results → `aborted` (`no_results`); any `failed` or `blocked` → `failed`; otherwise (all `passed` or `skipped`) → `passed`.
- AC4: The report holds the counts (total, passed, failed, blocked, skipped, not reported), the failed and blocked cases with their failing step and story key, the AC impact (each active AC's status for this run, with the cases run and the failing cases), the missing screenshots and the masked summary. It also holds `stories` (the counts per story, in run order) and `skippedCases` (a suite run's skipped cases, [SUITE-5](suites-and-plans.md#suite-5-finish-a-suite-run-and-its-report-wbs-91)).
- AC5: The reply is the run status and the list of missing screenshots (case code and step order, plus `iteration` for a data-driven case). The report's `missingScreenshots` have `iteration` too: the iteration number for a case with data rows, `null` otherwise.
- AC6: `run.finished` is published and `run_finished` is sent to the starter and every QC member of the project. A suite run's `run.finished` has `suiteId` instead of `storyId`, and its notification is `suite_run_finished`.

### RUN-7 Run detail and live progress (WBS 3.10.2, 3.10.3)

As a QC, I want to watch a run case by case, with each step's result and screenshot, so that I can review failures right away.

- AC1: `/projects/[projectKey]/runs/[runId]` shows the run details and two tabs: Results and Report.
- AC2: Results lists each case with its version ("v{n}"), its story (`storyId`, `storyJiraKey`, `storyTitle` in the API), status and steps: action, expected, actual result, error and the screenshot. A screenshot shows "Uploading screenshot…" while pending and "Screenshot missing" when it never arrived; clicking opens it full size.
- AC3: A case the run never reported shows "Not reported" ("the case keeps its previous result").
- AC4: While the run is `running` the page shows "Live" and "{reported} of {total} cases reported". It refreshes on `run.case_recorded` and `run.finished`, and also polls every 30 s.
- AC5: Report shows the report of RUN-6, or "The report is built when the run finishes."
- AC6: An unknown run shows "Run not found".
- AC6b: A suite run's page is titled "Suite run · {name}", groups the Results by story (with counts per story), lists the suite's skipped cases, and its Report has "Results by story" ([suites-and-plans.md, Screens and states](suites-and-plans.md#screens-and-states)). A data-driven case shows one block per iteration (RUN-14 AC12).
- AC7: Each case has a "Case details" toggle (closed by default) that opens the case sheet of RUN-12 without its steps: linked AC, why it matters, preconditions and the data of the run's environment. Secrets stay masked here. Placeholders in the steps show as value chips.
- AC9: A failed or blocked case shows its suspected cause and reason under its title, and its failing step shows a "Why it failed" panel: page, failed requests ("POST /api/payments → 502" with the error excerpt) and console errors. The report's failed cases also show the suspected cause.
- AC8: The case code links to `/test-cases/[caseCode]?tab=history&version=n`, which opens History comparing the version the run executed with the latest.

### RUN-8 Manual run (WBS 3.10.4)

As a QC, I want to run cases by hand and record each step, so that cases Claude cannot run still get results.

- AC1: "New manual run" (`/projects/[projectKey]/runs/new`) picks a story, an environment and the Ready cases ("{selected} of {total} selected"), then "Start manual run" calls `POST /api/projects/{project_key}/runs`. The same rules as RUN-2 apply (gaps, one running run, Ready cases, environment order). The API also takes `suiteId` instead of `storyKey` for a manual suite run ([SUITE-4 AC10](suites-and-plans.md#suite-4-start-a-suite-run-wbs-91)); the reply then has `storyId: null`, `testSuiteId` and `skippedCases`. On the page, "What to run" offers *A story* or *A suite*, and `?suite=<id>` preselects a suite ([suites-and-plans.md, Screens and states](suites-and-plans.md#screens-and-states)).
- AC2: `/projects/[projectKey]/runs/[runId]/record` lists the cases. For each step the tester sets a status, the actual result, what went wrong, and optional evidence (a file upload of kind `evidence`: the project's allowed types plus PNG, JPEG and WebP, up to 20 MB).
- AC3: "Save result" calls `PUT /api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}`. Unmarked steps are saved as `skipped`. The case status defaults to the suggested one: failed if any step failed, else blocked, else passed, else skipped. A saved result cannot be changed (`CASE_RESULT_EXISTS`). The body takes `iteration` (default 0) for a data-driven case ([RUN-14](#run-14-shared-steps-and-iterations-in-a-run-wbs-92)).
- AC4: Only the starter (or `run.finish_any`) may record; a Claude run gets `RUN_NOT_MANUAL`. Evidence must be the recorder's own uploaded `evidence` file (`INVALID_REQUEST`, or `UPLOAD_NOT_COMPLETED` while uploading).
- AC5: "Finish run" warns about cases with no result, takes an optional summary (up to 4000 characters) and calls `POST …/runs/{run_id}/finish`. The status, report and notifications follow RUN-6.
- AC6: The header shows the environment name, its base URL as a link that opens in a new tab, and a copy button.
- AC7: Above the steps the case sheet (RUN-12) shows the linked AC, why it matters, preconditions (highlighted) and the test data of the run's environment. Each step shows the action and "Expected result" at the same size, with placeholders as value chips. Steps are timeline nodes (RUN-12 AC5) with the recording fields (status, actual result, what went wrong, evidence) in a box under each. A step's dot shows its number until the tester marks it, then its status icon. A recorded case is shown read-only on the same timeline, with each step's status, actual result, error and "Evidence attached". Evidence sits behind an "Attach evidence" button.
- AC8: When some steps are not marked, the suggestion says how many will be saved as Skipped ("{count} steps are not marked and will be saved as Skipped.").
- AC9: A secret shows `••••` with a Reveal button for the run's starter with `secret.use_in_run`. Reveal calls `POST /api/projects/{project_key}/runs/{run_id}/resolve-data` with `{"keys": [...]}` (1 to 50 keys), under the same rules and audit as MCP `resolve_data`: starter only (`RUN_NOT_OWNED`), running run only (`RUN_NOT_RUNNING`), only keys the run's cases use, one `secret.resolve` audit event per key with the run id. The value stays shown until Hide, the case is saved or the page is left. Anyone else sees "Hidden".
- AC10: When the case result (suggested or chosen) is Failed or Blocked, the tester can pick a suspected cause and write why. `PUT …/cases/{test_case_id}` sends `suspectedCause` and `causeReason`; they are kept only for a failed or blocked result.

### RUN-9 Re-run failed only (WBS 3.10.5)

As a Dev, I want to re-run only what failed, so that I can confirm my fix quickly.

- AC1: On a finished run with failed or blocked cases, "Re-run failed ({count})" shows the Claude command to run the `rerun-failed` skill, or "Re-run manually instead". A suite run's page (grouped by story, with its skipped cases, RUN-7 AC6b) offers the same button, and the re-run is again a suite run ([SUITE-5 AC6](suites-and-plans.md#suite-5-finish-a-suite-run-and-its-report-wbs-91), SUITE-8 AC7 and AC8). A new manual run picks *A story* or *A suite* (RUN-8 AC1).
- AC2: Claude calls `get_failed_cases(run_id)`, then `start_run(story_key, environment, parent_run_id=run_id)` (for a suite run `start_run(suite=…, environment, parent_run_id=run_id)`, or batches of at most 50 without a parent link, [SUITE-8 AC8](suites-and-plans.md#suite-8-run-a-suite-with-claude-wbs-91)); the server picks the parent's failed and blocked cases that are still `ready`.
- AC3: The manual re-run calls `POST /api/projects/{project_key}/runs/{run_id}/rerun-failed` (optional `environmentId`, default: the parent's).
- AC4: The new run links to its parent. A running parent gives `RUN_NOT_FINISHED`; a parent with no failed or blocked case still Ready gives `NO_FAILED_CASES_TO_RERUN`. Passing both `case_ids` and `parent_run_id` gives `INVALID_REQUEST`.

### RUN-10 Aborted runs (WBS 3.10.8)

As a QC, I want runs that were left hanging to close on their own, so that the story is not blocked for ever.

- AC1: The `runs.abort_stale` job runs every 15 minutes and aborts each `running` run with no activity for 4 hours, with reason `inactive`.
- AC2: The aborted run gets a partial report (screenshots checked), `run.finished` is published and `run_finished` (or `suite_run_finished` for a suite run) is sent as in RUN-6.
- AC3: Cases the run never reported keep their previous latest result.
- AC4: Aborted runs appear in the list and the status filter.

### RUN-12 Readable case sheet (WBS 3.10.9, 3.6.10)

As a tester or a Dev, I want each case laid out the way I follow it, so that I can run or review it without opening other pages.

- AC1: `GET /api/projects/{project_key}/runs/{run_id}` also returns `environmentBaseUrl`, and for each case the fixed version's `businessValue`, `preconditions`, active `criteria` (`code`, `text`) and `files` (`key`, `fileName`). `data` lists the effective values for the run's environment of the keys the run's cases use (environment value first, then the project value); a secret has `value: null`. Secret values never appear in this payload.
- AC2: The case sheet shows, in order and only when not empty: Covers (AC), Why it matters, Before you start (highlighted), Test data · {environment} (key, value, copy), Steps.
- AC3: `{{data.key}}` shows the value as a chip with the key in the tooltip; a secret shows `••••`; a key with no value shows "No value for {key} on {environment}". `{{file.key}}` shows the file name, or "No file for {key}".
- AC4: The same component is used by the test case page (CASE-12), the manual run (RUN-8) and the run detail (RUN-7). Code: [client/src/components/case-sheet](../../client/src/components/case-sheet).
- AC5: Steps show as a vertical timeline (`DSStepTimeline`): one node per step, joined to the next by a line. A step with no result shows its number in the dot, then the action, then "Expected result" indented under it with a check icon. A step with a result shows its status icon and label instead of the number. The test case page, the case editor, the manual recording screen, the recorded manual case and the run detail all use it.

### RUN-11 Story context and test files for Claude (WBS 3.10.3)

As Claude, I want everything about a story in one call and the files a step needs, so that I can run it without guessing.

- AC1: `get_story_context(story_key)` returns the story (key, title, test status, Jira status), its active AC, its `ready` cases at their current version (with AC codes, business value, preconditions, steps, file keys and label names, [CASE-13 AC8](test-cases.md#case-13-labels-wbs-91)), the number of other cases, the data the cases use (values per environment, secrets only as `{{data.key}}`, each with its key description), missing data keys, files and environments.
- AC2: `get_test_file(run_id, key, case_id?)` returns a file name and a 5-minute download link for a `{{file.<key>}}` of a case in the caller's own running run. When two cases use the key with different files, `case_id` is needed (`INVALID_REQUEST`). The file version handed out is recorded for the run.

### RUN-13 Execution log of a Claude run (WBS 3.10.10, 4.13, 5.13)

As a tester, I want to see what Claude did during a run, so that I understand how it reached each result.

Design record: [execution log proposal](../discussions/execution-log-proposal.md).

- AC1: After `finish_run`, the plugin hook `claude/hooks/upload_run_log.py` reads the run's part of Claude Code's session log (from the `start_run` result holding the run id to the `finish_run` call). It keeps Claude's visible notes (`note`) and every tool call with its input, output, error flag and duration (`action`), masks the values `resolve_data` returned, replaces images with `[screenshot]`, cuts each text and input to 4000 characters, sums the token usage once per request, and sends it to `POST /api/runs/{run_id}/log`. Claude's hidden thinking is never in the log.
- AC2: `POST /api/runs/{run_id}/log` takes an API token with `run.start` from the run's starter (`RUN_NOT_OWNED` otherwise), for a finished Claude run, at most 24 hours after it finished (`CONFLICT` while it runs or after that; `INVALID_REQUEST` for a manual run). Up to 3000 entries. Sending it again replaces the earlier log.
- AC3: The server masks every text and input again with the environment's secret values and assigns each entry: `setup` before the first browser action, then `case` with the `case_id` of the next `record_case_result` call, then `wrap_up` after the last one. A run that records no case has only setup (and wrap-up after a browser action).
- AC4: `GET /api/projects/{project_key}/runs/{run_id}/log?caseId=` (`run.view`) returns `receivedAt`, `isCut`, `usage` (input, cache creation, cache read and output tokens) and the entries, for the run or one case. Without a log, `receivedAt` and `usage` are null and `entries` is empty. `run.log_received` is published when a log arrives.
- AC5: Claude runs get a **Log** tab: the token total and tokens per case, then sections Setup, one per case ("TC-1 · title") and Wrap-up, each a timeline with the time from the first entry, a plain label (Opened, Typed, Clicked, Read the page, Ran, Tessio: tool…), the duration, an Error badge, and the input and output on demand. Without a log it says "Claude's log arrives when the run finishes.", or "No log was received for this run." 24 hours after the finish. Manual runs have no Log tab.
- AC6: An upload that fails with a network error or a 5xx waits in `~/.tessio/pending-run-logs/` and is retried the next time the hook runs.

### RUN-14 Shared steps and iterations in a run (WBS 9.2)

As a tester, I want a run to keep the exact steps it ran and one result per data row, so that a result always matches what was done and one bad row is never hidden.

Design record: [competitive features proposal F2](../discussions/competitive-features-proposal.md#f2-shared-steps-and-data-driven-cases-m-wbs-92). Shared steps, parameters and data rows themselves: [CASE-16](test-cases.md#case-16-shared-steps-and-data-driven-cases-wbs-92). Server: [run_start_gate.py](../../server/app/modules/runs/usecases/run_start_gate.py), [postgres_run_case_repository.py](../../server/app/modules/runs/infrastructure/postgres_run_case_repository.py), [worst_iteration.py](../../server/app/modules/runs/utils/worst_iteration.py) and [worst_iteration_condition.py](../../server/app/modules/runs/infrastructure/worst_iteration_condition.py).

- AC1 (snapshot): when a run starts (MCP `start_run`, a manual run, a suite run or a re-run), each run case stores its steps in `run_cases.steps`: the case version's steps with every shared step replaced by the steps of its current version, numbered again from 1. An expanded step keeps `shared_step_key` and `shared_step_version_number` in the snapshot.
- AC2 (results match the snapshot): `start_run`, the manual run reply, the run detail, the case sheet and the report read the snapshot. Step orders in `record_case_result` and in the manual record route are checked against the snapshot, not the current case, so saving the shared step during a run changes nothing in that run; the next run gets the new steps.
- AC3 (old runs): a run case without a snapshot (every run started before migration 0026) falls back to its case version's steps, as before.
- AC4 (data in the replies): `start_run` lists `parameters` and `data_rows` for a data-driven case (left out otherwise). `get_story_context` and `get_suite_context` list each case's expanded steps, `parameters`, `data_rows` and `data_keys` (the case's own and its shared steps'), and the data entries those keys need. The manual run reply has `parameters` and `dataRows` for each case.
- AC5 (iterations): each data row runs as one iteration, numbered from 0 in row order. `record_case_result(…, iteration?)` and `PUT …/runs/{run_id}/cases/{test_case_id}` take `iteration` (default 0). A case without data rows has only iteration 0. An iteration the case has no row for gets `ITERATION_OUT_OF_RANGE` (422); a second result for the same run, case and iteration gets `CASE_RESULT_EXISTS` (the unique key of `case_results` is run, case and iteration).
- AC6 (the worst iteration counts): a data-driven case's result in a run is its worst iteration: `failed` before `blocked` before `passed` before `skipped` (the lowest iteration when two are equal). It is used for the run status and counts (run list, run detail, report, per-story counts), `get_failed_cases`, re-runs, the latest result of a case (case list, `case-latest-results`, traceability and AC status, story progress, plan progress) and the flaky score (one decisive result per run).
- AC7 (failures): the first failing iteration of a case in a run opens or updates its failure; later failing iterations of the same case in that run do not add a "failed again" event.
- AC8 (run detail): each case's `result` and `steps` show the worst iteration, and `result.iteration` names it. `parameters` lists the case's parameters, and `iterations` has one entry per data row: `iteration`, `values` (the row), `result` (null until recorded) and `steps`. A case without data rows has `iterations: []`.
- AC9 (events): `run.case_recorded` is published for each iteration, with the same ids as before.
- AC10 (replies): the manual record route's reply has `iteration`. A missing screenshot of a data-driven case names its `iteration`, in the `finish_run` reply and in the report (RUN-6 AC5). A screenshot is uploaded under its iteration's own case result, so two iterations never overwrite each other's evidence (RUN-5).
- AC11 (Claude runs, plugin): the shared run procedure ([execute-cases.md](../../claude/skills/run-story-tests/references/execute-cases.md)), used by `/tessio:run-story-tests`, `/tessio:run-suite` and `/tessio:rerun-failed`:
  - runs the expanded steps as given;
  - runs a case with `data_rows` once per row, in row order, with every `{{param.name}}` in the preconditions, actions and expected results replaced by the row's value, and starts each iteration from the preconditions again;
  - resolves a row value's `{{data.key}}` with `resolve_data` just before that iteration and never writes the secret back;
  - records each iteration right after its last executed step, with one `record_case_result(…, iteration=<row index>)` per row (0 first). A failed or blocked iteration ends only that iteration; the next row still runs;
  - tells the user, per data-driven case, how many iterations passed, failed and were blocked, and the row values of the failed or blocked ones.
- AC12 (run detail screen): on `/projects/[projectKey]/runs/[runId]` a data-driven case card says "{recorded} of {count} iterations recorded" next to its status (the worst iteration). Show steps opens one block per iteration instead of one step list, in row order. Each block has the heading "Iteration {n}" (n from 1), the iteration's status badge (Pending or Not reported while it has no result) and duration, the row values as `name = value` (a `{{data.key}}` value shows as its test data chip), the suspected cause, and the iteration's steps with each `{{param.name}}` replaced by the row's value, with their status, actual result, screenshot and evidence. A case without data rows shows its step list as before. Client: [run-case-iterations.tsx](../../client/src/modules/runs/components/run-case-list/run-case-card/run-case-iterations/run-case-iterations.tsx).
- AC13 (manual recording screen): on `/projects/[projectKey]/runs/[runId]/record` a data-driven case shows the case sheet once, then one block per iteration with its heading, status and row values. One block is open at a time: the first iteration without a result, or the one the tester opens with "Record iteration {n}" (or "Show iteration {n}" for a recorded one, or for someone who can't record). The open block records that iteration with the usual step recorder, suggested status and suspected cause, with `{{param.name}}` replaced by the row's value, and "Save iteration {n}" sends `PUT …/cases/{test_case_id}` with `iteration` (n − 1). After a save the next iteration without a result opens; when every iteration has one, the screen moves to the next unrecorded case. A data-driven case counts as recorded (case list, "x of y cases recorded", next case) only when every iteration has a result; until then the case list shows "{recorded} of {count} iterations recorded". Each iteration keeps its own draft. A case without data rows is recorded as before, with `iteration: 0` in the body. Client: [iteration-recorder.tsx](../../client/src/modules/manual-run/components/iteration-recorder/iteration-recorder.tsx).

### RUN-16 Export the run report (WBS 3.10.7, 9.5)

As a QC, I want the run report as Markdown or PDF, so that I can attach it to a release ticket or send it to someone without a Tessio account.

- AC1: `POST /api/projects/{project_key}/runs/{run_id}/export` with `{"format": "md" | "pdf"}` (`report.view`) answers 202 with `fileId`, `fileName` (`run-{story key or suite name}-{started date}.md`), `format`, `source` (`run`), `sourceId` (the run id) and `sourceLabel`. An unknown run, or another project's, gives `NOT_FOUND`; a bad format gives the 422 validation `detail`.
- AC2: The `report.export` job (queue `reports`) builds the report in the requester's language: the run's facts (status, executor, environment, started by, start, finish, duration, abort reason, parent run), the summary, the counts, results by story for a suite run, the failed and blocked cases with failing step, actual result, error and suspected cause, the AC impact, a suite run's skipped cases, the missing screenshots, and every case with its version and status. A data-driven case has its worst iteration as the status and each iteration's status listed ([RUN-14](#run-14-shared-steps-and-iterations-in-a-run-wbs-92)).
- AC3: Every text is masked again against the project's secret values (`••••`). The PDF is rendered from escaped HTML by WeasyPrint in the worker; no browser runs.
- AC4: When the file is stored, the requester gets the `report_ready` notification ([NOTIF-9](notifications.md#notif-9-report-ready-wbs-95)) and `report.ready`; the file downloads with `GET /api/projects/{project_key}/files/{file_id}`. The full rules, and the plan and story exports, are in [insights.md, INS-7](insights.md#ins-7-export-a-run-plan-or-story-report-wbs-95-3107).

### RUN-17 Import JUnit results from CI (WBS 9.6)

As a QC, I want the results of our Playwright, Jest or pytest suites in CI to show up in Tessio, so that I see them next to Claude and manual results and their failures open as usual.

- AC1: `POST /api/projects/{project_key}/runs/import` (`run.start`) takes a multipart form: `file` (a JUnit XML file of 10 MB at most), `environment` (an active environment's name, any case, or id) and an optional `suite` (a suite's name, any case, or id). It answers 201 with `runId`, `status`, `counts` (`total`, `passed`, `failed`, `blocked`, `skipped`, `notReported`), `mappedTestCount`, `unmappedTestCount` and `unmappedTests`.
- AC2: A CI job calls it with an `api`-scope token in `Authorization: Bearer …` ([integrations.md, INT-6](integrations.md#int-6-api-scope-tokens-for-the-public-rest-api-wbs-96)); a signed-in user can call it with the session too. The token's user needs `run.start` (Admin, QC, Dev), and the token works only for its own project (another project gives `NOT_FOUND`).
- AC3: The file is parsed with `defusedxml`: a DTD, an entity declaration (an XML bomb such as "billion laughs") or an external reference is refused with `JUNIT_INVALID`, as is XML that is not well formed, an XML declaration with an unknown or unsupported encoding (for example `encoding="foo-bar"` or a multi-byte encoding such as `shift_jis`), a root that is not `<testsuites>` or `<testsuite>`, or more than 20 000 `<testcase>` elements. Nested `<testsuite>` elements are read.
- AC4: A `<testcase>` maps to a case when its `name` or a `<property name="tessio.case" value="…">` holds a case code: `TC-<n>` or `TC_<n>`, any case, not glued to other letters or digits (`test_tc_12_login` and `test_refund[TC-3]` map; `ATC-12` and `TC-12x` don't). A test that names several codes counts for each case. Deprecated cases and codes the project doesn't have don't map.
- AC5: Outcome: a `<failure>` or `<error>` child makes the test `failed`, a `<skipped>` child makes it `skipped`, otherwise it `passed`. The error text is the element's `message` attribute, or its text when there is none, cut at 4000 characters and masked against the environment's secret values. `time` (seconds) becomes the duration. A `time` that is not a number, is negative, or is longer than one day (86 400 s) is left out, so the test has no duration.
- AC6: Several tests of one case become one result: `failed` if any failed, else `passed` if any passed, else `skipped`. The durations add up, capped at one day (86 400 000 ms, as for MCP and manual results); with more than one failed test the error lists each as "{test name}: {message}".
- AC7: The import creates one finished run with executor `ci`, started and finished now, by the token's user (`startedViaTokenId` set for a token). With `suite` the run belongs to that suite (`testSuiteId`); without it the run has neither a story nor a suite. Its cases are the mapped cases at their current version (shared steps expanded). Each case gets one result (iteration 0). A failed case also gets one failed step result on its first step that holds the error, because JUnit doesn't say which step failed; passed and skipped cases have no step results.
- AC8: Run status as for any run (any failed → `failed`, else `passed`). The report is built as at finish (counts, failed cases with their error, AC impact by the cases' stories) and also holds `unmappedTests` (`name`, `classname`, `status`, `reason`: `no_case_code` or `unknown_case`; the first 500) and `unmappedTestCount`.
- AC9: Failed results open, reopen or update failures exactly as other runs do ([failures.md](failures.md)), and the cases' flaky scores are recomputed. After the transaction the server publishes `run.started`, one `run.case_recorded` per case, `failure.opened` (or `failure.status_changed` for a reopened failure), then `run.finished`. A suite import also sends the suite run finished notification; an import without a suite sends none. With `jiraPostResults` set to `every_run`, the import queues the Jira result comment for each story in its report, as a finished run does ([STORY-9](sprints-and-stories.md#story-9-results-on-the-jira-story-wbs-94)).
- AC10: Nothing is created when the file has no mapped test (`JUNIT_NO_MAPPED_TESTS`), names an unknown environment or suite (`UNKNOWN_REFERENCE`), an archived suite (`SUITE_ARCHIVED`) or is larger than 10 MB (`FILE_TOO_LARGE`). The 10 MB check runs on the received upload, so the api first receives the whole request; the proxy in front of it (Caddy) has no body size limit today. Open gaps and a running run don't block an import: the tests already ran.
- AC11: Re-running the failed cases of a `ci` run without a suite gives `NO_FAILED_CASES_TO_RERUN` (there is no story to re-run against); a suite import is re-run like any suite run.
- AC12: On the runs page, *Import JUnit results* (shown with `run.start` on an active project, next to *New manual run*) opens a dialog: Environment (required; the project's default environment, or the only one, is picked), Suite (optional, active suites) and a drop zone for one file. The client refuses a file that is not `.xml` ("Choose an .xml file."), is empty or is over 10 MB ("The file is over 10 MB.") before sending, and sends `multipart/form-data` with the environment and suite ids. Server errors (`JUNIT_INVALID`, `JUNIT_NO_MAPPED_TESTS`, `UNKNOWN_REFERENCE`, `SUITE_ARCHIVED`, `FILE_TOO_LARGE`) show in the dialog. A project without an active environment shows "This project has no active environment." and *Import* is disabled.
- AC13: After the import the dialog shows "The CI run passed" or "The CI run failed", the counts, "{n} tests matched a case." and "{n} tests did not match any case.", the unmapped tests (name, class name, result, why: "No case code" or "Unknown or deprecated case") and *Open run*.
- AC14: The `ci` executor shows as "CI" in the run list, the run page, the dashboard's recent runs and a failure's result history. A `ci` run without a story or suite shows "CI import" in the run list's Story column and on the dashboard; its page is titled "CI import" with "JUnit results imported from CI, across the project's stories.", groups the Results by story like a suite run, has no Log tab and no *Re-run failed* button (AC11). Its Report has "Results by story" and, when some tests were not mapped, a "{n} unmapped tests" card with the first 500 and "{n} more tests are not listed." (also for a suite import).
- Tests: [tests/api/runs/junit_import](../../server/tests/api/runs/junit_import) with the Playwright, Jest and pytest samples and the XML bombs in [tests/fixtures/junit](../../server/tests/fixtures/junit); parser and mapping unit tests in [tests/unit/runs](../../server/tests/unit/runs).

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Run statuses | `running`, `passed`, `failed`, `aborted` | `RunStatus` |
| Executors | `claude`, `manual`, `ci` (JUnit import, RUN-17); the database also accepts `script`, reserved for W12 | `RunExecutor`, check `run_executor` |
| Story or suite | each run has exactly one of `story_id` and `test_suite_id`; only a `ci` run may have neither | `ck_runs_story_or_suite` (migration 0029) |
| JUnit file | 10 MB, 20 000 tests, 4000-character error, 500 listed unmapped tests, one day per test and per case | `MAX_JUNIT_FILE_BYTES`, `MAX_JUNIT_TESTS`, `MAX_JUNIT_MESSAGE_LENGTH`, `MAX_LISTED_UNMAPPED_TESTS`, `MAX_JUNIT_DURATION_MS` |
| Abort reasons | `no_results`, `inactive` | `RunAbortReason` |
| Result statuses (case and step) | `passed`, `failed`, `blocked`, `skipped` | `ResultStatus` |
| Running runs per story | 1 | `uq_runs_story_id_running` |
| Running runs per suite | 1 | `uq_runs_test_suite_id_running` |
| Stale after | 4 hours without activity | `STALE_RUN_INACTIVITY` |
| Stale check | every 15 minutes (`*/15 * * * *`) | `runs.abort_stale` |
| Steps per recorded case | 200 | `MAX_STEPS_PER_CASE` |
| Results per run and case | one per iteration (0 to rows − 1, or only 0) | unique `case_results_run_id_test_case_id_iteration_key` |
| Summary | 4000 characters | `MAX_SUMMARY_LENGTH` |
| Run list | 50 by default, 200 at most | `DEFAULT_RUN_LIST_LIMIT`, `MAX_RUN_LIST_LIMIT` |
| Screenshot upload link | 1 hour, `image/*`, 20 MB | `SCREENSHOT_UPLOAD_LIFETIME`, `MAX_SCREENSHOT_BYTES` |
| Test file link | 5 minutes | `TEST_FILE_LINK_LIFETIME` |

- Run status from results: none → `aborted`; any `failed` or `blocked` → `failed`; else `passed` (all `skipped` counts as passed).
- A case's latest result ignores runs that did not report it, and a `skipped` result never replaces a real one ([TRACE-3](traceability.md#trace-3-ac-status-from-the-latest-results-wbs-373)).
- A data-driven case counts once per run, with its worst iteration (RUN-14 AC6).
- Run status diagram: [user-flows.md](../design/user-flows.md#run-status).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/runs` | "No runs yet. Ask Claude to run this project's stories, or start a manual run."; filtered: "No runs match these filters" | "Loading runs" | "Runs could not be loaded" + Try again | no "New manual run", no "Import JUnit results" | no "New manual run" without `run.record_manual`; no "Import JUnit results" without `run.start` | `run.started`, `run.case_recorded`, `run.finished` |
| Import JUnit dialog (runs page, RUN-17) | "This project has no active environment." | "Loading environments" | errors per code in the dialog | – | – | – |
| `/projects/[projectKey]/runs/[runId]` | – | skeleton | "Run not found" | no re-run | re-run hidden without `run.start`; *Export* hidden without `report.view` | `run.case_recorded`, `run.finished`, 30 s poll |
| `/projects/[projectKey]/runs/new` | "This story has no Ready test cases"; "This project has no active environment." | skeleton | errors per code | "You can't start manual runs" | "You can't start manual runs. Ask a project Admin for the QC role." | `test_case.changed`, `story.changed` |
| `/projects/[projectKey]/runs/[runId]/record` | "This case has no steps." | skeleton | "This page could not be loaded."; "Run not found" | read-only | "Only {name} can record this run."; Claude run: "Claude records this run" | `run.case_recorded`, `run.finished` |

The run detail header has *Export* (RUN-16): a dialog to pick Markdown or PDF, then "Preparing {file name}…" until *Download* appears ([insights.md, Export button](insights.md#export-button-run-plan-story)).

## API

| Method and path or MCP tool | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/runs?storyKey=&suiteId=&status=&limit=` | `run.view` (session or `api` token) |
| `GET /api/projects/{project_key}/runs/{run_id}` | `run.view` (session or `api` token) |
| `POST /api/projects/{project_key}/runs/import` (multipart `file`, `environment`, `suite?`) | `run.start` (session or `api` token, RUN-17) |
| `POST /api/projects/{project_key}/runs` | `run.start` + `run.record_manual` |
| `PUT /api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}` | `run.record_manual` (+ starter or `run.finish_any`) |
| `POST /api/projects/{project_key}/runs/{run_id}/finish` | `run.record_manual` (+ starter or `run.finish_any`) |
| `POST /api/projects/{project_key}/runs/{run_id}/rerun-failed` | `run.start` + `run.record_manual` |
| `POST /api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload` | API token, `run.start`, starter |
| `POST /api/projects/{project_key}/uploads` (kind `evidence`) | `run.record_manual` |
| `GET /api/projects/{project_key}/files/{file_id}` | `file.download` (screenshots and evidence) |
| MCP `get_story_context(story_key)` | `story.view` |
| MCP `get_open_gaps(story_key)` | `gap.view` ([readiness-review.md](readiness-review.md)) |
| MCP `start_run(story_key? or suite?, environment?, case_ids?, parent_run_id?)` | `run.start` |
| MCP `get_suite_context(suite)` | `run.view` ([suites-and-plans.md](suites-and-plans.md)) |
| MCP `resolve_data(run_id, keys[])` | `secret.use_in_run` ([environments-and-test-data.md](environments-and-test-data.md)) |
| `POST /api/projects/{project_key}/runs/{run_id}/resolve-data` | `secret.use_in_run`, starter (RUN-8 AC9) |
| MCP `get_test_file(run_id, key, case_id?)` | `run.start` |
| MCP `record_case_result(run_id, case_id, status, duration_ms, steps[], iteration?)` | `run.start` |
| MCP `finish_run(run_id, summary?)` | `run.start` (+ starter or `run.finish_any`) |
| MCP `get_failed_cases(run_id)` | `run.view` |
| `POST /api/runs/{run_id}/log` | API token, `run.start`, starter (RUN-13) |
| `GET /api/projects/{project_key}/runs/{run_id}/log` | `run.view` (session or `api` token) |
| `POST /api/projects/{project_key}/runs/{run_id}/export` | `report.view` (RUN-16) |

The full Claude sequence is drawn in [user-flows.md](../design/user-flows.md#3-a-claude-run).

## Errors

| ErrorCode | When |
| --- | --- |
| `OPEN_GAPS_BLOCK_RUN` | Start while any gap on the story is open (a suite run: on any story with a case in the suite, with the gaps listed) |
| `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY`, `SUITE_ARCHIVED` | Suite runs ([suites-and-plans.md](suites-and-plans.md#errors)) |
| `RUN_ALREADY_RUNNING` | Start while the story has a running run |
| `NO_READY_CASES` | No `ready` case to run |
| `CASE_NOT_READY` | A chosen case is not `ready` |
| `UNKNOWN_REFERENCE` | A case not on the story or run; an unknown or archived environment name |
| `INVALID_REQUEST` | Several environments and none chosen; bad step orders; `case_ids` with `parent_run_id`; parent of another story or suite; both or neither of story and suite; evidence not usable; ambiguous file key |
| `RUN_NOT_OWNED` (403) | Recording, finishing, uploading or resolving on someone else's run without `run.finish_any` (MCP record and upload always need the starter) |
| `RUN_NOT_RUNNING` | Recording or finishing a finished run |
| `RUN_NOT_MANUAL` | Manual recording or finishing on a Claude run |
| `RUN_NOT_FINISHED` | Re-running a parent that is still running |
| `NO_FAILED_CASES_TO_RERUN` | No failed or blocked case of the parent is still `ready` |
| `CASE_RESULT_EXISTS` | A second result for the same case and iteration in a run |
| `ITERATION_OUT_OF_RANGE` | `iteration` names a data row the case's run snapshot does not have (422) |
| `UPLOAD_NOT_COMPLETED` | Evidence still uploading |
| `NOT_FOUND` | Unknown run, story, case result or test file; another project's run |
| `INVALID_API_TOKEN` | MCP or hook call with a bad, expired or revoked token |
| `JUNIT_INVALID` (422) | The import file is not well-formed JUnit XML, or has a DTD, entities or external references (RUN-17) |
| `JUNIT_NO_MAPPED_TESTS` (422) | No test in the import file maps to a case of the project; no run is created |
| `FILE_TOO_LARGE` (413) | The import file is over 10 MB |
| `TOKEN_SCOPE_NOT_ALLOWED` (403) | An `api`-scope token on the hook routes (screenshot upload, log upload) or on `/mcp` |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or any write on an archived project |

## Later

- Nothing is parked for runs. (3.10.7, export the report, is built: RUN-16.)

## Differences from the proposals

- The [workflow proposal §6](../discussions/testing-workflow-proposal.md#6-claude-integration-mcp-server) had `record_step_result`, one call per step with the image. The code has `record_case_result`, one call per case, with screenshot paths only; the hook uploads the images ([server proposal §8](../discussions/server-proposal.md#8-mcp-tools)).
- MCP tools added since the proposals: `get_test_file`. `get_story_context` also returns environments and missing data keys.
- Only one running run per story, and a zero-result run is `aborted` (assumption 4.12).
- A REST re-run is always manual; a Claude re-run goes through `start_run` with `parent_run_id`.
- Suite runs (WBS 9.1) were not in the workflow proposal; they came with the [competitive features proposal F1](../discussions/competitive-features-proposal.md#f1-regression-suites-test-plans-and-labels-l-wbs-91).
- Manual runs need `run.record_manual`, so Dev cannot start one, although Dev can start Claude runs.

## Open points

- WBS 5.7 is open: tokens per test case have not been measured on a pilot story (`claude/scripts/measure-tokens.sh` is ready).
- A screenshot that arrives after `finish_run` stays "missing" (parked).
- A race on the one-running-run rule reaches the database guard and returns a 500 (MVP).
- Not checked against a running stack: a live Claude run updating the detail case by case, a real screenshot or evidence upload to RustFS (needs bucket CORS), and the manual flow end to end.
- The hook keeps retrying a screenshot whose upload keeps failing with 5xx; there is no retry cap.

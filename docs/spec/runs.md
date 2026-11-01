# Runs

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.10 · Story prefix RUN · Index: [README](README.md)

## Purpose

A run executes a story's Ready test cases against one environment and keeps a result for every case and step. Claude runs them on the developer's machine through Tessio's MCP server (`/mcp`), with a screenshot for every step. A tester can also run them by hand in the UI. The server builds the report when the run finishes. Tessio never runs a browser itself. Server: [server/app/modules/runs](../../server/app/modules/runs) (REST and MCP) and [server/app/modules/story_context](../../server/app/modules/story_context) (`get_story_context`, `get_test_file`). Client: [client/src/modules/runs](../../client/src/modules/runs) and [client/src/modules/manual-run](../../client/src/modules/manual-run). Claude side: the [Tessio plugin](../../claude/README.md).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open runs, MCP `get_failed_cases` | `run.view` | all |
| MCP `get_story_context` | `story.view` (+ `test_case.view`, `test_data.view`) | all |
| MCP `start_run`, `record_case_result`, `finish_run`, `get_test_file`; screenshot upload link | `run.start` | Admin, QC, Dev |
| Start, record and finish a manual run; manual re-run; evidence upload | `run.start` + `run.record_manual` (finish: `run.record_manual`) | Admin, QC |
| Finish or record a run someone else started | `run.finish_any` | Admin |

Every MCP tool needs a personal API token for the project ([AUTH-10](authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326)). Viewer tokens can call only the read tools (`get_story_context`, `get_open_gaps`, `get_failed_cases`); PM and BA tokens can also call `raise_gaps`.

## User stories

### RUN-1 Run list (WBS 3.10.1, 3.10.8)

As a team member, I want every run with a status filter, so that I find the one I need.

- AC1: `/projects/[projectKey]/runs` lists runs, newest first, with started time, story, status (Running, Passed, Failed, Aborted), executor (Claude, Manual), environment, who started it, results ("{n} passed", "{n} failed", "{n} blocked", "{n} skipped", "{n} not reported") and duration.
- AC2: Filters: status (including Aborted) and story (`status`, `storyKey`). "Clear filters" resets them.
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
- AC5: Each case's current version is fixed in the run, so later edits do not change what the run executes.
- AC6: The story moves to `in_test`, and `run.started` and `story.changed` are published.

### RUN-3 Health check before the run (WBS 3.10.3)

As a Dev, I want Claude to check the environment is up first, so that a down server is not reported as failed cases.

- AC1: Claude calls the `health_check_url` (or `base_url` when there is none) itself with `curl`. The server never calls it.
- AC2: When it is down, Claude calls `finish_run` with no case results and a summary such as "Environment down: <url> <code>"; the run ends `aborted` with reason `no_results`.

### RUN-4 Record a case result (WBS 3.10.2, 3.10.3)

As Claude, I want to record one result per case with every step's outcome, so that the team sees progress case by case.

- AC1: `record_case_result(run_id, case_id, status, duration_ms, steps[])` records one case. Each step has `order`, `status` (`passed`, `failed`, `blocked`, `skipped`), `actual_result`, an optional `error` and an optional local `screenshot_path`. 1 to 200 steps per call.
- AC2: Only the person who started the run may record (`RUN_NOT_OWNED`), only while it is `running` (`RUN_NOT_RUNNING`), and only once per case (`CASE_RESULT_EXISTS`).
- AC3: A step order that is not in the case's fixed version, or appears twice, gives `INVALID_REQUEST`. Steps the call leaves out are saved as `skipped`.
- AC4: Actual results and errors are masked against the environment's secret values (`••••`).
- AC5: Each step with a `screenshot_path` gets a pending screenshot file. The reply is only `{"case_result_id": "…"}` (about 30 tokens).
- AC6: The run's last activity time is updated, `run.case_recorded` is published, and a `failed` result opens or updates a failure ([failures.md](failures.md)).

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
- AC4: The report holds the counts (total, passed, failed, blocked, skipped, not reported), the failed and blocked cases with their failing step, the AC impact (each active AC's status for this run, with the cases run and the failing cases), the missing screenshots and the masked summary.
- AC5: The reply is the run status and the list of missing screenshots (case code and step order).
- AC6: `run.finished` is published and `run_finished` is sent to the starter and every QC member of the project.

### RUN-7 Run detail and live progress (WBS 3.10.2, 3.10.3)

As a QC, I want to watch a run case by case, with each step's result and screenshot, so that I can review failures right away.

- AC1: `/projects/[projectKey]/runs/[runId]` shows the run details and two tabs: Results and Report.
- AC2: Results lists each case with its version ("v{n}"), status and steps: action, expected, actual result, error and the screenshot. A screenshot shows "Uploading screenshot…" while pending and "Screenshot missing" when it never arrived; clicking opens it full size.
- AC3: A case the run never reported shows "Not reported" ("the case keeps its previous result").
- AC4: While the run is `running` the page shows "Live" and "{reported} of {total} cases reported". It refreshes on `run.case_recorded` and `run.finished`, and also polls every 30 s.
- AC5: Report shows the report of RUN-6, or "The report is built when the run finishes."
- AC6: An unknown run shows "Run not found".

### RUN-8 Manual run (WBS 3.10.4)

As a QC, I want to run cases by hand and record each step, so that cases Claude cannot run still get results.

- AC1: "New manual run" (`/projects/[projectKey]/runs/new`) picks a story, an environment and the Ready cases ("{selected} of {total} selected"), then "Start manual run" calls `POST /api/projects/{project_key}/runs`. The same rules as RUN-2 apply (gaps, one running run, Ready cases, environment order).
- AC2: `/projects/[projectKey]/runs/[runId]/record` lists the cases. For each step the tester sets a status, the actual result, what went wrong, and optional evidence (a file upload of kind `evidence`: the project's allowed types plus PNG, JPEG and WebP, up to 20 MB).
- AC3: "Save result" calls `PUT /api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}`. Unmarked steps are saved as `skipped`. The case status defaults to the suggested one: failed if any step failed, else blocked, else passed, else skipped. A saved result cannot be changed (`CASE_RESULT_EXISTS`).
- AC4: Only the starter (or `run.finish_any`) may record; a Claude run gets `RUN_NOT_MANUAL`. Evidence must be the recorder's own uploaded `evidence` file (`INVALID_REQUEST`, or `UPLOAD_NOT_COMPLETED` while uploading).
- AC5: "Finish run" warns about cases with no result, takes an optional summary (up to 4000 characters) and calls `POST …/runs/{run_id}/finish`. The status, report and notifications follow RUN-6.

### RUN-9 Re-run failed only (WBS 3.10.5)

As a Dev, I want to re-run only what failed, so that I can confirm my fix quickly.

- AC1: On a finished run with failed or blocked cases, "Re-run failed ({count})" shows the Claude command to run the `rerun-failed` skill, or "Re-run manually instead".
- AC2: Claude calls `get_failed_cases(run_id)`, then `start_run(story_key, environment, parent_run_id=run_id)`; the server picks the parent's failed and blocked cases that are still `ready`.
- AC3: The manual re-run calls `POST /api/projects/{project_key}/runs/{run_id}/rerun-failed` (optional `environmentId`, default: the parent's).
- AC4: The new run links to its parent. A running parent gives `RUN_NOT_FINISHED`; a parent with no failed or blocked case still Ready gives `NO_FAILED_CASES_TO_RERUN`. Passing both `case_ids` and `parent_run_id` gives `INVALID_REQUEST`.

### RUN-10 Aborted runs (WBS 3.10.8)

As a QC, I want runs that were left hanging to close on their own, so that the story is not blocked for ever.

- AC1: The `runs.abort_stale` job runs every 15 minutes and aborts each `running` run with no activity for 4 hours, with reason `inactive`.
- AC2: The aborted run gets a partial report (screenshots checked), `run.finished` is published and `run_finished` is sent as in RUN-6.
- AC3: Cases the run never reported keep their previous latest result.
- AC4: Aborted runs appear in the list and the status filter.

### RUN-11 Story context and test files for Claude (WBS 3.10.3)

As Claude, I want everything about a story in one call and the files a step needs, so that I can run it without guessing.

- AC1: `get_story_context(story_key)` returns the story (key, title, test status, Jira status), its active AC, its `ready` cases at their current version (with AC codes, business value, preconditions, steps and file keys), the number of other cases, the data the cases use (values per environment, secrets only as `{{data.key}}`), missing data keys, files and environments.
- AC2: `get_test_file(run_id, key, case_id?)` returns a file name and a 5-minute download link for a `{{file.<key>}}` of a case in the caller's own running run. When two cases use the key with different files, `case_id` is needed (`INVALID_REQUEST`). The file version handed out is recorded for the run.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Run statuses | `running`, `passed`, `failed`, `aborted` | `RunStatus` |
| Executors | `claude`, `manual` | `RunExecutor` |
| Abort reasons | `no_results`, `inactive` | `RunAbortReason` |
| Result statuses (case and step) | `passed`, `failed`, `blocked`, `skipped` | `ResultStatus` |
| Running runs per story | 1 | `uq_runs_story_id_running` |
| Stale after | 4 hours without activity | `STALE_RUN_INACTIVITY` |
| Stale check | every 15 minutes (`*/15 * * * *`) | `runs.abort_stale` |
| Steps per recorded case | 200 | `MAX_STEPS_PER_CASE` |
| Summary | 4000 characters | `MAX_SUMMARY_LENGTH` |
| Run list | 50 by default, 200 at most | `DEFAULT_RUN_LIST_LIMIT`, `MAX_RUN_LIST_LIMIT` |
| Screenshot upload link | 1 hour, `image/*`, 20 MB | `SCREENSHOT_UPLOAD_LIFETIME`, `MAX_SCREENSHOT_BYTES` |
| Test file link | 5 minutes | `TEST_FILE_LINK_LIFETIME` |

- Run status from results: none → `aborted`; any `failed` or `blocked` → `failed`; else `passed` (all `skipped` counts as passed).
- A case's latest result ignores runs that did not report it, and a `skipped` result never replaces a real one ([TRACE-3](traceability.md#trace-3-ac-status-from-the-latest-results-wbs-373)).
- Run status diagram: [user-flows.md](../design/user-flows.md#run-status).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| `/projects/[projectKey]/runs` | "No runs yet. Ask Claude to run this project's stories, or start a manual run."; filtered: "No runs match these filters" | "Loading runs" | "Runs could not be loaded" + Try again | no "New manual run" | no "New manual run" without `run.record_manual` | `run.started`, `run.case_recorded`, `run.finished` |
| `/projects/[projectKey]/runs/[runId]` | – | skeleton | "Run not found" | no re-run | re-run hidden without `run.start` | `run.case_recorded`, `run.finished`, 30 s poll |
| `/projects/[projectKey]/runs/new` | "This story has no Ready test cases"; "This project has no active environment." | skeleton | errors per code | "You can't start manual runs" | "You can't start manual runs. Ask a project Admin for the QC role." | `test_case.changed`, `story.changed` |
| `/projects/[projectKey]/runs/[runId]/record` | "This case has no steps." | skeleton | "This page could not be loaded."; "Run not found" | read-only | "Only {name} can record this run."; Claude run: "Claude records this run" | `run.case_recorded`, `run.finished` |

## API

| Method and path or MCP tool | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/runs?storyKey=&status=&limit=` | `run.view` |
| `GET /api/projects/{project_key}/runs/{run_id}` | `run.view` |
| `POST /api/projects/{project_key}/runs` | `run.start` + `run.record_manual` |
| `PUT /api/projects/{project_key}/runs/{run_id}/cases/{test_case_id}` | `run.record_manual` (+ starter or `run.finish_any`) |
| `POST /api/projects/{project_key}/runs/{run_id}/finish` | `run.record_manual` (+ starter or `run.finish_any`) |
| `POST /api/projects/{project_key}/runs/{run_id}/rerun-failed` | `run.start` + `run.record_manual` |
| `POST /api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload` | API token, `run.start`, starter |
| `POST /api/projects/{project_key}/uploads` (kind `evidence`) | `run.record_manual` |
| `GET /api/projects/{project_key}/files/{file_id}` | `file.download` (screenshots and evidence) |
| MCP `get_story_context(story_key)` | `story.view` |
| MCP `get_open_gaps(story_key)` | `gap.view` ([readiness-review.md](readiness-review.md)) |
| MCP `start_run(story_key, environment?, case_ids?, parent_run_id?)` | `run.start` |
| MCP `resolve_data(run_id, keys[])` | `secret.use_in_run` ([environments-and-test-data.md](environments-and-test-data.md)) |
| MCP `get_test_file(run_id, key, case_id?)` | `run.start` |
| MCP `record_case_result(run_id, case_id, status, duration_ms, steps[])` | `run.start` |
| MCP `finish_run(run_id, summary?)` | `run.start` (+ starter or `run.finish_any`) |
| MCP `get_failed_cases(run_id)` | `run.view` |

The full Claude sequence is drawn in [user-flows.md](../design/user-flows.md#3-a-claude-run).

## Errors

| ErrorCode | When |
| --- | --- |
| `OPEN_GAPS_BLOCK_RUN` | Start while any gap on the story is open |
| `RUN_ALREADY_RUNNING` | Start while the story has a running run |
| `NO_READY_CASES` | No `ready` case to run |
| `CASE_NOT_READY` | A chosen case is not `ready` |
| `UNKNOWN_REFERENCE` | A case not on the story or run; an unknown or archived environment name |
| `INVALID_REQUEST` | Several environments and none chosen; bad step orders; `case_ids` with `parent_run_id`; parent of another story; evidence not usable; ambiguous file key |
| `RUN_NOT_OWNED` (403) | Recording, finishing, uploading or resolving on someone else's run without `run.finish_any` (MCP record and upload always need the starter) |
| `RUN_NOT_RUNNING` | Recording or finishing a finished run |
| `RUN_NOT_MANUAL` | Manual recording or finishing on a Claude run |
| `RUN_NOT_FINISHED` | Re-running a parent that is still running |
| `NO_FAILED_CASES_TO_RERUN` | No failed or blocked case of the parent is still `ready` |
| `CASE_RESULT_EXISTS` | A second result for the same case in a run |
| `UPLOAD_NOT_COMPLETED` | Evidence still uploading |
| `NOT_FOUND` | Unknown run, story, case result or test file; another project's run |
| `INVALID_API_TOKEN` | MCP or hook call with a bad, expired or revoked token |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or any write on an archived project |

## Later

- 3.10.7 Export the report as PDF or Markdown.

## Differences from the proposals

- The [workflow proposal §6](../discussions/testing-workflow-proposal.md#6-claude-integration-mcp-server) had `record_step_result`, one call per step with the image. The code has `record_case_result`, one call per case, with screenshot paths only; the hook uploads the images ([server proposal §8](../discussions/server-proposal.md#8-mcp-tools)).
- MCP tools added since the proposals: `get_test_file`. `get_story_context` also returns environments and missing data keys.
- Only one running run per story, and a zero-result run is `aborted` (assumption 4.12).
- A REST re-run is always manual; a Claude re-run goes through `start_run` with `parent_run_id`.
- Manual runs need `run.record_manual`, so Dev cannot start one, although Dev can start Claude runs.

## Open points

- WBS 5.7 is open: tokens per test case have not been measured on a pilot story (`claude/scripts/measure-tokens.sh` is ready).
- A screenshot that arrives after `finish_run` stays "missing" (parked).
- A race on the one-running-run rule reaches the database guard and returns a 500 (MVP).
- Not checked against a running stack: a live Claude run updating the detail case by case, a real screenshot or evidence upload to RustFS (needs bucket CORS), and the manual flow end to end.
- The hook keeps retrying a screenshot whose upload keeps failing with 5xx; there is no retry cap.

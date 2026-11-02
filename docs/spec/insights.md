# Insights and report export

**Status:** Draft · **Updated:** 2026-11-02

WBS 9.5 (covers 3.10.7) · Story prefix INS · Index: [README](README.md)

## Purpose

The Insights page shows how a project's testing goes over time: pass rate per day and per sprint, runs by executor, failures opened against fixed and the mean time to fix, the cases that fail most and the flaky ones, coverage by label, AC coverage per sprint, how long gaps stay open, and the tokens each Claude run used. A nightly job writes one row of daily stats per project (`project_daily_stats`) so the charts read a small table. A run, a test plan or a story can also be exported as a Markdown or PDF report, built in the worker (WeasyPrint renders HTML without a browser, so the server rule holds). Server: [server/app/modules/insights](../../server/app/modules/insights) (read models, daily snapshot) and [server/app/modules/reports](../../server/app/modules/reports) (export). Client: [client/src/modules/insights](../../client/src/modules/insights) (the page) and [client/src/modules/reports](../../client/src/modules/reports) (the *Export* button). Design: [competitive features proposal F5](../discussions/competitive-features-proposal.md#f5-insights-and-report-export-m-wbs-95).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| Every `GET …/insights/*` route, the Insights sidebar entry | `report.view` | all |
| Export a run, plan or story report (`POST …/export`) | `report.view` | all |
| Download the exported file (`GET …/files/{file_id}`) | `file.download` | all |

Exports are reads: they work on archived projects too, like every other read.

## User stories

### INS-1 Trends per day and per sprint (WBS 9.5)

As a QC or PM, I want the pass rate and activity over time, so that I see whether quality goes up or down.

- AC1: `GET /api/projects/{project_key}/insights/trends?from&to&groupBy=day|sprint` returns `groupBy`, `firstDay`, `lastDay`, `executors` (every executor with at least one run in the range, in the order `claude`, `manual`, `script`, `ci`, then others by name), `points` and `total`.
- AC2: `from` and `to` are ISO dates (UTC days). Without them the range is the last 30 days up to today; `from` alone runs to today; `to` alone covers the 30 days before it. `from` after `to`, or a range longer than 366 days, gives `INVALID_REQUEST` (422). A bad date or `groupBy` gives the usual 422 validation `detail`.
- AC3: Each point has `day` (day grouping) or `sprint` (`id`, `name`, `state`, `startAt`, `endAt`; sprint grouping), `firstDay`, `lastDay` and:
  - `runCount` and `runsByExecutor` (`[{executor, count}]`, one entry per executor of AC1, zeros included): runs **started** that day, story runs and suite runs alike;
  - `passedCount`, `failedCount`, `blockedCount`, `skippedCount`: case results recorded that day, one per case and run: a data-driven case counts once, with its **worst iteration** (failed, then blocked, passed, skipped), as in the run report;
  - `passRate`: passed ÷ (passed + failed + blocked), 4 decimals, `null` when there is no such result (skipped results are left out);
  - `failuresOpened`: failures created that day; `failuresFixed`: failures whose **first** move to `fixed` (or straight to `verified`) happened that day; `meanTimeToFixSeconds`: the mean of (first fix − failure opened) for those, `null` when none;
  - `gapsOpened`, `gapsAnswered` (by `answered_at`) and `meanGapAnswerSeconds` (answered − raised);
  - `openGapCount` and `medianOpenGapAgeSeconds`: the gaps open at the end of the day and the median of their ages then.
- AC4: Only days up to today get a point; a range in the future has no points. `total` sums the whole range the same way; its open-gap values are those of the last day with data.
- AC5: With `groupBy=sprint`, each day belongs to the sprint that contains it (from `startAt` to `endAt`; a sprint with no end runs to the end of the range); when sprints overlap, the one that started last wins. Days outside every sprint are left out. A sprint point sums its days, and its open-gap values are those of its last day. Sprints without a start date are not shown; at most 12 sprints.
- AC6: Past days are read from `project_daily_stats`; today, and any past day with no stored row (for example before the first nightly run), are computed live with the same rules. A stored row wins over the live value.

### INS-2 Coverage by label (WBS 9.5)

As a QC, I want each label's cases, how many are Ready and how many pass, so that I see which areas are weak.

- AC1: `GET /api/projects/{project_key}/insights/coverage-by-label` returns `labels` (every label of the project, by name), `unlabelled` and `total`.
- AC2: Each has `caseCount`, `readyCount`, `passedCount`, `readyShare` and `passedShare` (4 decimals, `null` when the label has no case). Deprecated cases are left out.
- AC3: "Passed" means the case's latest result is `passed`: the newest worst-iteration result, a skipped one only when there is nothing else, from story and suite runs alike (the same rule as the traceability page).

### INS-3 The cases that fail most, and flaky cases (WBS 9.5, 9.13)

As a QC, I want to see which cases fail most and which are flaky, so that I fix the right ones first.

- AC1: `GET /api/projects/{project_key}/insights/top-failing?from&to&limit` lists the cases with at least one failed or blocked result in the range (same range rules as INS-1). Results count once per case and run (worst iteration); skipped results are left out.
- AC2: Each item has `testCaseId`, `code`, `title`, `status`, `storyJiraKey`, `resultCount`, `failedCount`, `blockedCount`, `failRate` ((failed + blocked) ÷ results), `lastFailedAt`, `isFlaky` and `isQuarantined`. Order: most failed or blocked first, then the higher fail rate, then the latest failure.
- AC3: `GET /api/projects/{project_key}/insights/flaky?limit` lists the cases that are flaky (`flaky_since` set) or disagreeing (`disagreed_at` set, [CASE-14](test-cases.md#case-14-flaky-cases-and-quarantine-wbs-913)), deprecated cases left out, by `flakyScore` (highest first), then the oldest `flakySince`. Each item has `flakyScore`, `isFlaky`, `flakySince`, `isDisagreeing`, `disagreedAt`, `isQuarantined` and `quarantinedAt`.
- AC4: `limit` is 1 to 50, 10 by default.

### INS-4 Tokens per Claude run (WBS 9.5)

As an Admin, I want the tokens each Claude run used, so that I know what testing costs on our Claude plans.

- AC1: `GET /api/projects/{project_key}/insights/tokens?from&to` lists the runs started in the range whose execution log ([HARN](ai-harness.md), `run_logs`) reported tokens, newest first, at most 200.
- AC2: Each run has `runId`, `startedAt`, `executor`, `storyJiraKey` (story run) or `testSuiteName` (suite run), `caseCount` (the run's cases), `inputTokens`, `cacheCreationInputTokens`, `cacheReadInputTokens`, `outputTokens`, `totalTokens` (the four added), `tokensPerCase` and `isCut` (the log was cut).
- AC3: The reply also has `totalTokens`, `meanTokensPerRun` and `meanTokensPerCase` over the listed runs. Runs without a log (manual runs, or a Claude run whose log never arrived) and runs whose log reported no usage (all four counts 0, the upload's default) are not counted.

### INS-5 AC coverage per sprint (WBS 9.5)

As a PM, I want the AC coverage of each sprint, so that I compare sprints.

- AC1: `GET /api/projects/{project_key}/insights/sprint-coverage?from&to` lists the sprints that overlap the range (with a start date, at most the 12 latest, oldest first).
- AC2: Each has `sprint`, `storyCount` (the sprint's stories still in Jira) and `coverage` (`criterionCount`, `coveredCount`, `passedCount`, `failedCount`, `blockedCount`, `notRunCount`, `uncoveredCount`), counted as on the dashboard ([DASH](dashboard.md)).
- AC3: The coverage is today's state of each sprint's stories, not the state when the sprint ended.

### INS-6 Nightly daily snapshot (WBS 9.5)

As the team, we want the charts to stay fast, so the counts are written once a night.

- AC1: The job `insights.daily_snapshot` runs every night at 02:00 UTC (`0 2 * * *`) on the `maintenance` queue. One job handles every project that is not archived.
- AC2: For each project it writes yesterday's row of `project_daily_stats` (always recomputed) and every missing day of the 90 days before, but not before the day the project was created. Rows are upserted on (`project_id`, `day`), so running it again never duplicates a day.
- AC3: Each row holds `runs_by_executor` (JSON), the result counts, `failures_opened`, `failures_fixed`, `fix_seconds_total`, `gaps_opened`, `gaps_answered`, `answer_seconds_total`, `open_gap_count`, `median_open_gap_age_seconds` and `computed_at`, with the rules of INS-1 AC3. Sums are stored (not means), so any period's mean is exact.
- AC4: After writing a project's rows it publishes `insights.changed` for the project.

### INS-7 Export a run, plan or story report (WBS 9.5, 3.10.7)

As a QC or PM, I want a run, plan or story report as Markdown or PDF, so that I can share it outside Tessio.

- AC1: `POST /api/projects/{project_key}/runs/{run_id}/export`, `POST …/plans/{plan_id}/export` and `POST …/stories/{jira_key}/export` take `{"format": "md" | "pdf"}` and answer 202 with `fileId`, `fileName`, `format`, `source` (`run`, `plan`, `story`), `sourceId` and `sourceLabel`.
- AC2: The request checks `report.view` and that the source exists in the project (`NOT_FOUND` otherwise, also for another project's run or plan). It stores a pending `report` file and queues `report.export` on the `reports` queue (job id = the file id) with the file, project, requester, source and format.
- AC3: File names are ASCII: `run-{story key or suite name}-{started date}.md`, `plan-{name}.pdf`, `story-{jira key}.md`; other characters become `-`, at most 80 characters before the extension.
- AC4: The job re-reads the requester: an inactive user, or one who lost access to the project, gets nothing (the file stays pending and the nightly orphan cleanup removes it). It then builds the document in the requester's language (`en`, `fr`, `vi`):
  - **run:** status, executor, environment, started by, start, finish, duration, abort reason, parent run; the summary; the counts (total, passed, failed, blocked, skipped, not reported); results by story (suite runs); the failed and blocked cases with their failing step, actual result, error and suspected cause; the AC impact; the skipped cases (suite runs); the missing screenshots; and every case with its version, status (worst iteration) and, for a data-driven case, each iteration's status. A run that is still running says "The report is built when the run finishes."
  - **plan:** status, target date, environment, created, signed off (when and by whom), closed; the description; the progress counts; the scope (suites and stories with their case counts); every case with its latest result and active failure; the active failures; the open gaps.
  - **story:** test status and AC coverage; each active AC with its status and linked cases; every case with status, priority, latest result and the flaky and quarantined flags; the story's last 20 runs.
- AC5: Every text of the document is masked against the project's secret values (all environments) with `••••`, on top of the masking done when results were recorded.
- AC6: Markdown: a title, facts as a list, a section per part, tables with `|` and Markdown characters escaped and line breaks folded. PDF: the same document as HTML (every text escaped, A4, page numbers, DejaVu Sans), rendered by WeasyPrint in the worker.
- AC7: The job writes the object (`projects/{project_id}/report/{file_id}/{file_name}`), marks the file uploaded with its size and SHA-256, sends `report_ready` to the requester ([NOTIF-9](notifications.md#notif-9-report-ready-wbs-95)) and publishes `report.ready`. The file is then downloadable with `GET /api/projects/{project_key}/files/{file_id}`; before that it gives `NOT_FOUND`.
- AC8: The job retries on unexpected errors (5 tries, 30 s exponential backoff); a refusal (`NOT_FOUND`, `PERMISSION_DENIED`) or broken job data is logged and not retried. A failed export sends no notification or event: the file stays pending until the nightly orphan cleanup removes it, and the dialog tells the user to export again when no notification comes.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Day boundaries | UTC | `utc_day`, `start_of_day` |
| Default range | 30 days up to today | `DEFAULT_RANGE_DAYS` |
| Longest range | 366 days | `MAX_RANGE_DAYS` |
| Snapshot backfill | 90 days | `SNAPSHOT_BACKFILL_DAYS` |
| Snapshot schedule | `0 2 * * *` on `maintenance` | `SNAPSHOT_CRON_PATTERN`, `SNAPSHOT_SCHEDULER_ID` |
| Case lists (`limit`) | 10 by default, 50 at most | `DEFAULT_CASE_LIST_LIMIT`, `MAX_CASE_LIST_LIMIT` |
| Token runs listed | 200 | `MAX_TOKEN_RUNS` |
| Sprints in trends and sprint coverage | 12 | `MAX_SPRINT_COVERAGE_COUNT` |
| Executor order | `claude`, `manual`, `script`, `ci`, then by name | `EXECUTOR_ORDER` |
| Rates and shares | 4 decimals | `PASS_RATE_DIGITS` |
| Export formats | `md` (`text/markdown; charset=utf-8`), `pdf` (`application/pdf`) | `ReportFormat`, `CONTENT_TYPE_BY_FORMAT` |
| Export sources | `run`, `plan`, `story` | `ReportSource` |
| Story report runs | the last 20 | `MAX_STORY_REPORT_RUNS` |
| Report texts | `en`, `fr`, `vi` | `REPORT_TEXTS`, `VALUE_LABELS` |
| Export job | `report.export` on queue `reports` | `JobName.REPORT_EXPORT`, `QueueName.REPORTS` |

- A gap is open at the end of a day when it was raised before then and either was not answered by then, or is open now after a reopen that happened before then. Earlier answer-and-reopen cycles are not kept, so a past day can read slightly differently from what the screen showed that day.
- Failures fixed count the first fix of each failure only; a failure that is reopened and fixed again is not counted twice.

## Screens and states

### Insights page (`/projects/[projectKey]/insights`)

On the *Insights* sidebar entry (`report.view`, every role). Charts are the design-system charts (`DSLineChart`, `DSBarChart`): each is a named figure with a hidden data table, so no value is told by colour alone. Executors always keep the same colour (Claude, Manual, Script, CI, then any other executor); passed is green, failed red, blocked amber.

- **Filters** (one card at the top):
  - *From* and *To* (UTC days). They start at the last 30 days up to today. Every chart and list with a period reads them.
  - *Sprint*: the project's sprints that have a start date ("{name} · {state}"). Picking one sets *From* and *To* to its start and end (no end: today; never more than 366 days). Clearing it goes back to the last 30 days; editing a date clears it. Hidden while the project has no dated sprint.
  - *Group by*: *Day* or *Sprint* (the trends' `groupBy`).
  - A start after the end, or more than 366 days, shows "Check the dates" and no request is sent.
- **Summary** (INS-1 `total`): the period ("{from} – {to} (UTC days)"), then tiles for the pass rate, runs, results (passed / failed / blocked), failures opened, failures fixed, mean time to fix, open gaps and the median open gap age. Durations show in minutes, hours or days, numbers and percents in the user's language.
- **Trend charts** (two columns, one on narrow screens), one point per day or per sprint:
  - *Pass rate over time*: a line, a gap where a day has no decisive result.
  - *Runs by executor*: stacked bars, one colour per executor of the period (story and suite runs alike). "No runs started in this period." when there is none.
  - *Failures opened and fixed*: two bars per point, and "Mean time to fix: {duration}" for the period.
  - *How long gaps stay open*: the median age of the open gaps and the mean time to answer, in days, with "{n} raised · {n} answered · mean time to answer: {duration}".
- **Cases that fail most** (INS-3, the 10 first) and **Flaky cases** (the 10 first), side by side: the case code (linking to the case) and title with its *Flaky*, *Disagreeing* and *Quarantined* badges, and the story (linking to it). The first adds "{failed} / {blocked} of {results}", the fail rate and the last failure; the second "{n} flips in 10 results" and since when.
- **Coverage by label** (INS-2, today's cases): horizontal bars of the share Ready and the share passed per label, then a table with each label's chip, its cases, and the Ready and passed counts with their share. Cases without a label are a "No label" row.
- **AC coverage per sprint** (INS-5): stacked bars per sprint of passed, failed, blocked, not run and not covered criteria.
- **Tokens per Claude run** (INS-4): tiles for the total, the mean per run, the mean per case and the runs with token counts; stacked bars of the input, cache write, cache read and output tokens of the 30 newest runs (oldest on the left); a table of the 10 newest runs (story key or suite name linking to the run, start time, a "Log cut" badge, executor, cases, tokens, tokens per case) and "Showing the latest 10 of {n} runs." when there are more.

| Part | Empty | Loading | Error | Live refresh |
| --- | --- | --- | --- | --- |
| Summary and trend charts | "Nothing happened in this period" ("No sprint covers this period" when grouped by sprint); the charts are hidden | skeleton | "Could not load Summary." + Retry | `insights.changed`, `run.started`, `run.case_recorded`, `run.finished`, `failure.changed`, `gap.changed` |
| Cases that fail most | "No failing cases" | skeleton | "Could not load …" + Retry | `insights.changed`, `run.case_recorded`, `run.finished`, `test_case.changed` |
| Flaky cases | "No flaky cases" | skeleton | as above | `insights.changed`, `run.case_recorded`, `run.finished`, `test_case.changed` |
| Coverage by label | "No test cases yet" | skeleton | as above | `insights.changed`, `run.case_recorded`, `run.finished`, `test_case.changed`, `label.changed` |
| AC coverage per sprint | "No sprint coverage" (no sprint with criteria in the period) | skeleton | as above | `insights.changed`, `run.case_recorded`, `run.finished`, `test_case.changed`, `story.changed`, `jira.sync_finished` |
| Tokens per Claude run | "No token data" | skeleton | as above | `insights.changed`, `run.log_received`, `run.finished` |

Every part loads and fails on its own, so one slow or failing route never hides the others. Today's numbers are read live, so the events that change runs, results, failures, gaps, cases, labels, stories and logs refresh the parts they feed; `insights.changed` refreshes them all after the nightly snapshot. The page is read-only, so it is the same in an archived project.

### *Export* button (run, plan, story)

On the run detail header ([RUN-16](runs.md#run-16-export-the-run-report-wbs-3107-95)), the plan header and the story header, shown with `report.view` (every role, archived projects included).

- *Export* opens a dialog: "Export the run report" / "Export the test plan" / "Export the story report", a short note (built in the background, secrets masked, a notification follows), and *Format*: *Markdown (.md)* or *PDF (.pdf)* (PDF by default). *Export* sends `POST …/export`; an error shows as a toast.
- After the request the dialog shows "Preparing {file name}…" and asks `GET …/files/{file_id}` every 5 s (at most 60 times) and again on `report.ready`. Once the link comes (it is renewed every 4 minutes, since a link lasts 5), it shows "{file name} is ready." with *Download* (opens the signed link in a new tab). If it takes longer, or the user has no `file.download`, it says "{file name} is still being prepared. You will get a notification when it is ready. If none arrives, export the report again." The dialog can be closed at any time; reopening it shows the last export of that page.
- The `report_ready` notification ([NOTIF-9](notifications.md#notif-9-report-ready-wbs-95)) reads "Report ready: {source label}" ("run …", "plan …" for a run or a plan) with the file name. The item links to the run's report tab, the plan or the story, and has a *Download the report* button that fetches the link and opens it (and marks the notification read). A file that is not ready or was removed says "This report is not ready yet, or it was removed."

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/insights/trends?from&to&groupBy` | `report.view` |
| `GET /api/projects/{project_key}/insights/coverage-by-label` | `report.view` |
| `GET /api/projects/{project_key}/insights/top-failing?from&to&limit` | `report.view` |
| `GET /api/projects/{project_key}/insights/flaky?limit` | `report.view` |
| `GET /api/projects/{project_key}/insights/tokens?from&to` | `report.view` |
| `GET /api/projects/{project_key}/insights/sprint-coverage?from&to` | `report.view` |
| `POST /api/projects/{project_key}/runs/{run_id}/export` | `report.view` |
| `POST /api/projects/{project_key}/plans/{plan_id}/export` | `report.view` |
| `POST /api/projects/{project_key}/stories/{jira_key}/export` | `report.view` |
| `GET /api/projects/{project_key}/files/{file_id}` (download the report) | `file.download` |

Live events: `insights.changed` (after the nightly snapshot of a project; the run, result, failure, gap, case, label, story, sync and log events in the table above also refresh the parts they feed) and `report.ready` (to the requester, `ids.fileId`, `ids.format`), see [client-api.md](client-api.md).

## Errors

| ErrorCode | When |
| --- | --- |
| `INVALID_REQUEST` | `from` after `to`, a range over 366 days; a bad date, `groupBy`, `limit` or `format` (422 validation `detail`) |
| `NOT_FOUND` | Unknown project or non-member; an unknown run, plan or story, or one of another project; a report file not ready yet |
| `PERMISSION_DENIED` | Missing `report.view` (every role has it today) |

## Later

- Project time zones: days are UTC days.
- Tokens per case from the per-case log entries (today: the run's tokens divided by its cases).

## Differences from the proposals

- The plan names Jinja templates for the export. Jinja2 is not a server dependency, so the document is built as a small typed model (`ReportDocument`) and rendered to Markdown and to escaped HTML by plain functions in `reports/utils` (assumption W11.T5-2).
- AC coverage per sprint is its own route (`sprint-coverage`) next to the five routes the plan lists (assumption W11.T5-4).
- The trends route also computes today and any missing past day live, so a new project or a fresh install shows data before the first nightly run (assumption W11.T5-3).
- The plan's "date range and sprint picker" is one filter card: the sprint picker fills in the date range, which every period-based part reads (assumption W11.T5-15).
- *Export* opens a dialog with the format choice and the export's progress, not a dropdown menu, and the page polls for the file next to the `report.ready` event (assumption W11.T5-16).

## Open points

- The real PDF test needs Pango. It runs in CI (the server job installs the four packages and fails the test if WeasyPrint cannot load); on a Mac without `brew install pango` it is skipped.
- The server image with the Pango packages has not been built in this task (W11.POST checks it).

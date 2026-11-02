# Competitive features: from sprint testing tool to a full test platform

**Status:** Accepted (Peter, 2026-11-02). Build plan: [competitive-features-plan.md](competitive-features-plan.md)
**Date:** 2026-11-02
**WBS:** [9.1 to 9.18](../wbs/wbs.md#9-competitive-features)
**Related:** [testing workflow proposal](testing-workflow-proposal.md), [server proposal](server-proposal.md), [readiness review spec](../spec/readiness-review.md), [ADR 0006](../decisions/0006-background-jobs-redis-bullmq.md) (Redis and BullMQ), [ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md) (one plugin for everyone)

## Decisions at a glance

| Area | Decision |
| --- | --- |
| Who Tessio is for | **One company, one workspace** (Peter, 2026-11-02). No multi-tenancy, billing or public sign-up. |
| How Claude works | **Unchanged: Claude always runs in a person's terminal and works through Tessio's MCP server** (Peter, 2026-11-02). Peter tried unattended Claude with an API key and with a plan token, and neither worked as expected. No Claude runs without a person. |
| Scripts | Claude writes Playwright scripts from passing cases (F8). A person starts script runs from Claude Code (F17a). They use few tokens and take seconds per case. |
| Runs with nobody watching | **No** (Peter, 2026-11-02). Every run is started by a person. There is no runner, and the api and worker rule in CLAUDE.md stays as it is. |
| Open gaps | **Gaps block suite runs too** (Peter, 2026-11-02). A new skill, `/tessio:answer-gaps`, helps the person who must answer clear them quickly (F18). |
| When to start | **Phase 1 starts now**, in parallel with the go-live work (Peter, 2026-11-02). |
| Scope | All 17 features (F1 to F16, F17a and F18), in three phases (§5). Peter, 2026-11-02: build them all. |

## 1. Why

Tessio already does what most tools don't: Claude runs cases from Jira stories, gaps are checked before a run, and every failure comes with a suspected cause. What it lacks against the market:

- **Every run is a full Claude run.** Claude looks at a screenshot for almost every action, so a run is slow and costs tokens. Re-checking last sprint's work costs as much as testing it the first time.
- **Cases live only inside stories.** A case belongs to one story ([WBS planning assumption 3.6.2](../wbs/wbs.md#planning-assumptions)). There's no regression suite that lasts across sprints, and no release-level sign-off.
- **Answering gaps is slow.** The person who must answer has to open Tessio, find the context and type an answer from scratch.
- **Jira is read-only.** Teams can't create a Jira bug from a failure or see results on the story in Jira.
- **No trends.** Reports cover one run. Nothing shows pass rate over time, flaky cases or coverage by area.
- **No way out.** There are no webhooks, Slack, public API or import of results from existing Playwright or Cypress suites.

## 2. The market

From Claude's knowledge, not checked against the vendors' current sites.

| Group | Products | What buyers get |
| --- | --- | --- |
| Test management | TestRail, Zephyr Scale, Xray, qTest, Qase, Testmo, PractiTest | Cases, suites, plans and cycles, shared steps, versions, dashboards, deep Jira integration, import of CI results |
| AI and no-code automation | mabl, Testim, testRigor, Functionize, Autify, Rainforest QA, Momentic, Octomind | Tests written in plain English or recorded, run in the vendor's cloud on a schedule or in CI, repaired automatically when the UI changes |
| Managed QA | QA Wolf | The vendor writes and runs Playwright tests for you |
| Platforms | Katalon, BrowserStack (Test Management, Percy), LambdaTest (KaneAI), Applitools | Many browsers and devices, screenshot comparison, AI test authoring |

**Where Tessio can win:** cases come from the story's AC, gaps are answered before a run, and Claude runs the cases, explains failures and writes the script that runs cheaply afterwards (F8). Most competitors offer either management or automation, not both in one place.

## 3. Two ways a test can run

Both are started by a person in Claude Code, and in both Claude works through the Tessio MCP server.

| | Claude run (today) | Script run (F17a) |
| --- | --- | --- |
| Command | `/tessio:run-story-tests` | `/tessio:run-scripts` |
| What clicks the buttons | Claude, through Claude in Chrome | A Playwright script Claude wrote earlier (F8) |
| Claude's part | Every action | Starting the run, reading failures and explaining them |
| Tokens | Many: a screenshot per action | Few: only the failures |
| Time per case | Minutes | Seconds |
| Where it runs | The person's computer | The person's computer |

A runner for runs with nobody watching (nightly or per pull request) was considered and dropped (Peter, 2026-11-02).

## 4. Features

Size: **S** about a week, **M** two to three weeks, **L** a month or more, for one developer with Claude. These are rough guesses.

### F1 Regression suites, test plans and labels (L, WBS 9.1)

- **Labels:** `labels` (project_id, name, color) and `test_case_labels`. They're edited in the case editor and filter the case list. Labels aren't versioned.
- **Suites:** `test_suites` (project_id, name, description, archived_at) and `test_suite_cases` (suite_id, test_case_id, position). Add cases one by one, or "add by filter" (label, priority, story, sprint). The filter runs once and gives a fixed list, which keeps things predictable. Suites that refresh themselves come later.
- **Suite runs:** `runs.story_id` becomes nullable, and `runs.test_suite_id` is added. A run has exactly one of the two.
  - Only *Ready* cases run. Cases flagged *Needs review* are skipped and listed in the report.
  - **Open gaps block a suite run** (Peter, 2026-11-02). The start is refused with `GAPS_OPEN` while any story with a case in the suite has an open gap. The reply lists the gaps by assignee, and the skill offers `/tessio:answer-gaps` (F18).
  - A suite run doesn't change any story's test status. Failures open as usual, on the case's story.
  - At most one running run per suite, like the one-per-story rule.
- **Plans:** `test_plans` (project_id, name, description, target_date, environment_id, status `open` / `signed_off` / `closed`, signed_off_by, signed_off_at) and `test_plan_items` (plan_id, suite_id or story_id). The plan page shows each case's latest result since the plan opened, plus open failures and gaps. Sign-off is refused while failures are active, as story sign-off is today.
- **Permissions:** `suite.edit` (Admin, QC), `plan.edit` (Admin, QC, PM), `plan.sign_off` (Admin, QC).
- **Claude:** `get_suite_context(suite)` returns cases grouped by story. `start_run` takes `suite?`. A new skill, `run-suite`, runs at most 50 cases per run and starts a new run for the rest. For large suites, script runs (F17a) are the cheap way.
- **Screens:** *Suites* and *Plans* in the project sidebar.

### F2 Shared steps and data-driven cases (M, WBS 9.2)

- **Shared steps:** `shared_steps` (project_id, key such as `login_as_admin`, title, current_version_id, archived_at) and `shared_step_versions` (number, steps JSONB, data_keys, created_by). A case step is either `{action, expected}` or `{shared_step_key}`.
- **Snapshot at run start:** `run_cases.steps` (new JSONB) holds the expanded steps, so a recorded result always matches the steps that ran, even after the shared step changes. The shared step editor shows "Used by N cases".
- **Data-driven cases:** `test_case_versions.parameters` and `data_rows` (JSONB, up to 20 rows of 20 values). Steps use `{{param.name}}`, and a value may be `{{data.key}}`. Secrets never go in rows.
  - Each row runs as one iteration: `case_results.iteration` (default 0, unique per run, case and iteration).
  - AC status takes the worst iteration.
- **Scripts:** in F8, a shared step becomes a shared Playwright helper.

### F3 Version compare and review comments (S, WBS 9.3)

- Compare two versions of a case side by side. The client uses the existing versions route.
- Review comments: `test_case_review_comments` (test_case_id, version_id, step_order?, body, author_id, resolved_at). An open comment blocks moving the case to *Ready*.
- Project setting "Reviewer must not be the author" (default off; today anyone with QC or Admin can review their own cases).

### F4 Two-way Jira (M, WBS 9.4)

- **Write access check:** saving the Jira connection checks the account's *Create issues* and *Add comments* permissions (Jira's `mypermissions`). The settings card shows whether it can write.
- **Bug from a failure:** a *Create Jira bug* button on the failure detail (Admin, QC, Dev).
  - Prefilled: summary from the case and the failing step; description with steps to reproduce, expected and actual results, the environment, the suspected cause and a link back; the screenshot as an attachment.
  - Issue type from project settings (default *Bug*), linked to the story with *relates to*.
  - Stored as `failures.jira_issue_key`, `jira_issue_url` and `jira_issue_status`. Sync refreshes the status.
  - When the Jira issue is done, the failure shows "Done in Jira" and a Dev marks it *Fixed*. Tessio never changes the status by itself. *Assumption.*
- **Results on the story:** a project setting (off, on sign-off, after every run). Tessio comments on the Jira story with the counts and a link, through a `jira.post_comment` job with retries.
- Hidden in projects without Jira.

### F5 Insights and report export (M, WBS 9.5)

- **Insights page per project:**
  - pass rate over time (per day and per sprint);
  - runs by executor;
  - failures opened against fixed, and mean time to fix;
  - the cases that fail most, and flaky cases (F13);
  - coverage by label: cases, share *Ready*, share passed;
  - AC coverage per sprint;
  - how long gaps stay open;
  - tokens per Claude run, where the execution log reported them.
- **Fast charts:** a nightly `insights.daily_snapshot` job writes `project_daily_stats`.
- **Export:** a run, plan or story report as Markdown or PDF (this covers WBS 3.10.7, export report). PDF is built in the worker with WeasyPrint, which renders HTML without a browser, so the server rule holds. It adds Pango to the server image.

### F6 Notifications, webhooks, public API and CI result import (M, WBS 9.6)

- **Email and chat:**
  - Email for the existing notification kinds, with per-user settings (covers WBS 3.12.2 and 3.13.3).
  - Slack and Teams through incoming webhook URLs set per project, stored encrypted like secrets. Each channel picks its events. No Slack app.
- **Outbound webhooks:**
  - Tables: `webhooks` (project_id, url, secret_encrypted, events, active) and `webhook_deliveries`.
  - Signed with `X-Tessio-Signature` (HMAC-SHA256) and sent by a `webhook.deliver` job, with five tries and growing delays.
  - Events: `run.started`, `run.finished`, `failure.opened`, `failure.status_changed`, `gap.raised`, `story.signed_off`, `plan.signed_off`.
- **Public API:** an API token gets a scope, `mcp` (today) or `api` (REST, same role checks). The REST docs come from the OpenAPI spec.
- **JUnit import:** `POST …/runs/import` takes a JUnit XML file, an environment and an optional suite.
  - A test whose name or properties hold `TC-123` maps to that case. Unmapped tests are listed in the report.
  - Executor `ci`. Failures open as usual.
  - Teams with existing Playwright or Cypress suites see those results next to Claude and manual results.

### F7 SSO, full audit log and failure comments (M, WBS 9.7)

- Sign-in with Google or Microsoft (OIDC), turned on per workspace. Two-factor is then the identity provider's job. SAML and SCIM are left out, because there's only one company.
- Full audit log (covers WBS 4.10): every write, with an admin page and filters.
- Comments on failures with @mentions that notify (covers WBS 3.11.4).

### F8 Scripts from passing runs (L, WBS 9.8)

The main differentiator: Claude does the slow, careful work once, and a script repeats it in seconds after that.

- **Storage:**
  - `test_case_scripts` (test_case_id, current_version_id, status `active` / `outdated` / `broken` / `retired`).
  - `test_case_script_versions` (script_id, number, test_case_version_id, source text up to 100 KB, created_via `claude` / `person`, created_by, approved_by, approved_at).
  - Tessio keeps the scripts so each one stays linked to its case version. Exporting to the product's repository comes later.
- **Writing:** a new plugin skill, `/tessio:automate-cases <story or case codes>`.
  1. Calls `get_case_for_automation(case_code)`, which returns the case version, steps, data keys, existing shared helpers and any current script.
  2. Replays the case in Claude in Chrome and reads the accessibility tree, so the script uses `getByRole` and `getByLabel` rather than coordinates.
  3. Writes a TypeScript Playwright test. Expected results become `expect` checks, and test data is read through a `data('key')` helper.
  4. Runs it locally with `npx playwright test`, at most three tries. The skill checks for Node and Playwright and prints the install command if they're missing.
  5. Saves it with `save_case_script(...)` as a version waiting for review.
- **Review:** QC or Admin approves a script version (`test_case.review`). An unapproved script never runs. This stops a script being quietly "fixed" so a real bug is hidden.
- **Out of date:** a new case version marks the script `outdated`. It keeps running until replaced, and the result shows a warning.
- **Can't be scripted:** a case whose expected results are visual or subjective is marked `not_automatable` and stays with Claude or manual runs.
- **Bundle:** `GET …/runs/{run_id}/script-bundle` builds a zip containing `playwright.config.ts`, one spec per case and the shared helpers from F2.
- **Repair:** when a script fails, the failure shows `/tessio:repair-script TC-12` for a person to run in Claude Code.
  - Claude replays the case in Claude in Chrome.
  - If the app behaves as the case expects, the script drifted: Claude saves a new version for review, and the suspected cause becomes the new value *Script out of date*.
  - Otherwise it's an app bug and the failure stays.

### F9 Screenshot comparison (M, WBS 9.9)

- `visual_baselines` (test_case_id, step_order, environment_id, browser, viewport, stored_file_id, masked_regions, approved_by).
- After a screenshot uploads, a `visual.compare` job in the worker compares it with the baseline using Pillow (image processing only, no browser). It stores `step_results.visual_diff_ratio` and a diff image.
- Above the project's threshold (default 0.5 % of pixels), the step is flagged *Visual change*. It doesn't fail the case. QC either accepts it as the new baseline or opens a failure.
- On by default only for script runs, which use a fixed viewport. Claude in Chrome screenshots vary in window size and scroll position, so comparison is off for them by default.

### F10 Exploratory sessions (M, WBS 9.10)

- Skill `/tessio:explore <story> "<charter>"`, limited to a set number of browser actions (default 60).
- MCP tools:
  - `start_session(story_key, charter, environment?)`;
  - `record_finding(session_id, kind bug / question / idea, title, steps, expected, actual, screenshot_path, severity)`;
  - `finish_session(session_id, summary, covered_areas)`.
- Tables: `exploratory_sessions`, `exploratory_findings`.
- A bug finding can become a Jira bug (F4) or a Draft case (through `create_draft_cases`). A question becomes a gap. An idea stays a note.
- Screen: a *Sessions* tab on the story.

### F11 Accessibility and speed checks (S, WBS 9.11)

- `step_results.checks` (JSONB): accessibility violations by impact plus the top 10 rules, and page timing (LCP, CLS, TTFB).
- **Script runs:** `@axe-core/playwright` on each new page, plus the browser's navigation timing.
- **Claude runs:** page timing only, through a short `javascript_tool` snippet. Accessibility checks stay script-only: injecting axe by hand costs too many tokens and is often blocked by the page's CSP.
- Project setting: accessibility *warn* (default) or *fail on critical*. Results show in the report.

### F12 Picking which regression cases to run (M, WBS 9.12)

- **In Claude Code:** skill `/tessio:pick-regression`.
  1. Reads the local `git diff main...HEAD`.
  2. Lists cases and labels through a new MCP tool, `list_cases(filter)`.
  3. Proposes a set of cases with a reason for each.
  4. On confirmation, starts a Claude run or a script run, or saves a suite.
- **By rule:** `label_paths` (label_id, glob). `POST …/selections` takes changed paths and returns case codes. The skill uses it first, then adds Claude's judgment.
- **From Jira:** the sync also reads story components and labels, so stories map to labels too.

### F13 Flaky cases and quarantine (S, WBS 9.13)

- **Flaky:** three or more pass↔fail flips in the case's last 10 results on the same case version, across all executors. Stored as `test_cases.flaky_score` and `flaky_since`, recomputed on each result.
- **Disagreement:** a manual and an automated result for the same case version, within 24 hours of each other, that differ.
- Shown as a badge and a filter, and in Insights (F5).
- **Quarantine (QC, Admin):** a quarantined case's failures in script runs don't open failures or fail the run, and they're listed separately. Quarantine ends after 10 passes in a row.

### F14 Better failure evidence (S, WBS 9.14)

- **Claude runs:** `record_case_result` takes `repro_steps` (up to 20 lines) for failed cases. Claude writes them from the actions it took. F4 uses them in the Jira bug.
- **Script runs:** a Playwright trace and video are kept on failure and uploaded as evidence. New `stored_files.kind` values `trace` and `video`, 50 MB maximum, deleted after 30 days by a cleanup job.
- The failure detail plays the video and offers the trace to download, with a hint to open it in Playwright's trace viewer.

### F15 Browsers and screen sizes (M, WBS 9.15)

- New columns: `runs.browser` (`chromium`, `firefox`, `webkit`, or `chrome` for Claude in Chrome), `runs.viewport` (`desktop`, `tablet`, `mobile`, or a width and height) and `runs.run_group_id`. Runs started together show as a matrix.
- **Script runs:** the full matrix, through Playwright projects.
- **Claude runs:** desktop and tablet widths through `resize_window`. Chrome's minimum window width may rule out phone widths. *Not verified.*
- AC status takes the worst latest result across configurations.

### F16 API steps (M, WBS 9.16)

- Step `kind`: `ui` (default) or `api`.
  - An API step has a method, a URL template, headers, a body and checks: status code, plus JSON path equals or exists.
  - Checked on save. The editor gets a step type switch.
- **Claude runs:** Claude runs it with `curl`, gets secrets through `resolve_data` and never prints them.
- **Script runs:** Playwright's `request` context. A case made only of API steps runs without a browser.

### F17a Script runs from Claude Code (M, WBS 9.17)

A person starts the run, as today. Claude works through the Tessio MCP server, as today. The script does the clicking.

1. The person types `/tessio:run-scripts <story or suite> [browser] [viewport]`.
2. Claude calls `start_run(story_key or suite, executor="script", ...)`. It's refused while gaps are open; the skill then offers `/tessio:answer-gaps` (F18). Only cases with an approved script run; the others are listed so the person can start a Claude run for them.
3. Claude runs `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_scripts.py <run_id>`, a standard-library script that runs on Python 3.9. It:
   - downloads the script bundle (F8) through a signed link;
   - fetches the run's secrets over REST, audited, into the Playwright process's environment only, so secret values never reach Claude;
   - runs `npx playwright test` in a temporary folder;
   - uploads each case result, screenshot, trace and video over REST with the plugin's token, as the screenshot upload hook does today;
   - prints a short summary: counts, and the failed cases with their error messages.
4. For each failed case, Claude reads the error. Where it helps, it opens the page in Claude in Chrome to diagnose, then sets the suspected cause with a new MCP tool, `set_case_cause(case_result_id, cause, reason)`. When the script looks out of date, it suggests `/tessio:repair-script`.
5. Claude calls `finish_run(run_id, summary)`.

- New executor value: `script`.
- The person's computer needs Node and Playwright; the skill checks and prints the install command.
- This is a new plugin version (a new skill and script), and the server routes ship with it.

### F18 Answer gaps with Claude (M, WBS 9.18)

Open gaps block story runs and, now, suite runs. This skill lets the person who must answer clear them in minutes, in their own terminal.

- **Skill:** `/tessio:answer-gaps [<story> | mine]`. It's run by the gap's assignee or anyone in its role queue (Admin, PM, BA, QC, Dev).
- **New MCP tools** (same rules and capabilities as the REST routes):
  - `get_my_gaps(story_key?)`: the open gaps assigned to the caller or to their role queue, in the token's project. Each gap comes with:
    - its story;
    - the text of the AC or case it targets;
    - up to three answered gaps with similar questions, from the same story first, then the project.
  - `answer_gap(gap_id, answer)`: like `PUT …/gaps/{gap_id}/answer`. It resolves the gap, records who answered and the token used, and publishes `gap.changed`.
  - `reassign_gap(gap_id, assignee_user_id? or role?)`: like `PUT …/gaps/{gap_id}/assignee`.
  - `set_test_data(key, value, environment?)`: non-secret variables and endpoints only (`test_data.edit`).
- **Flow:**
  1. Load the gaps, group related ones, and put high severity first.
  2. For each gap:
     - Say the question in plain words, and what it blocks (which AC, case and runs).
     - Offer two or three suggested answers, each with its source: the story text, an AC, an earlier answer, existing test data, or the product's code when the person runs Claude in the product's repository (file and line).
     - Also offer: write my own, not mine (reassign), skip.
  3. Ask with Claude Code's question prompt, so the person picks with one key press.
  4. Show the final answer text, then save it with `answer_gap`. For missing non-secret data, also save the value with `set_test_data`.
  5. At the end, show per story the open gaps left and whether runs are unblocked. When a story is ready, offer `/tessio:run-story-tests` or `/tessio:run-scripts`. List the cases the answers suggest updating; QC edits them.
- **Guardrails:**
  - Nothing is saved without the person's confirmation.
  - When Claude finds no source, it says so and asks an open question, rather than inventing a business rule.
  - Claude never asks for a secret value. For a secret data gap, it gives the link to the Test data page.
  - The skill never edits cases or Jira.
- **When a run is refused:** `run-story-tests`, `run-suite` and `run-scripts` handle `GAPS_OPEN` the same way. They list the open gaps by assignee, offer `/tessio:answer-gaps` for the ones the caller can answer, and name who must answer the rest.

## 5. Phases

| Phase | Theme | Features | Needs |
| --- | --- | --- | --- |
| 1, starts now | Regression and visibility | F1, F18, F2, F3, F4, F5, F6, F13 | Nothing new outside the repo; F4 needs a Jira account that can write |
| 2 | Cheap repeat runs | F8, F17a, F14, F15, F11, F16 | Node and Playwright on the testers' computers |
| 3 | More coverage | F10, F12, F9 | Pillow in the server image (F9) |
| Any time | Company basics | F7 | A Google Workspace or Microsoft Entra app registration |
| In parallel | MVP go-live | Release plan M9 to M11 | The current blockers B-1 to B-16 |

F1 and F18 go first and together: suites add more runs that open gaps can block, and F18 is how those gaps get cleared.

## 6. Not in this proposal

- Claude running with nobody watching, through an API key or a plan token (Peter tried both, 2026-11-02).
- A runner for script runs with nobody watching (Peter, 2026-11-02).
- Multi-tenancy, billing, public sign-up, SAML and SCIM (Peter: one company).
- Native mobile app testing (Appium), load testing and security scanning.
- A Tessio-hosted Playwright trace viewer, and exporting scripts to the product's repository.
- Suites that refresh themselves from a saved filter.
- Claude editing cases from gap answers (F18 lists the cases; QC edits them).

## 7. Open points

1. Whether a suite run should be blocked by any open gap on its stories, or only by gaps on the cases in the suite. Assumed: any open gap on the story, as story runs are today.
2. Similar-answer search in `get_my_gaps`: plain Postgres full-text search on the question text. *Assumption.*

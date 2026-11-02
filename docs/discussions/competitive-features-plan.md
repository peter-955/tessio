# Build plan: competitive features (waves W9 to W15)

**Status:** Draft, 2026-11-02
**Design:** [competitive features proposal](competitive-features-proposal.md) (accepted by Peter, 2026-11-02). Each feature's design (tables, routes, rules) is in the proposal; this plan says in what order to build it, who builds what, and when a task is done.
**WBS:** [section 9](../wbs/wbs.md#9-competitive-features), rows 9.1 to 9.18 (9.17b dropped)
**Release plan:** milestones M12 to M18 in [release-plan.md](../product/release-plan.md)

## 1. How to use this plan

- **One task, one Claude session.** Each task (`W10.T2`) is sized for one session and touches its own folders. Tasks in the same wave can run in parallel unless *Depends on* says otherwise.
- **Every wave has three kinds of steps**, as in waves W1 to W8:
  - **PRE** (one session, before the tasks): reserves migrations, capabilities, error codes, event names, translation namespaces and routes, so parallel tasks don't edit the same shared files.
  - **Tasks** (parallel sessions): build the feature with tests.
  - **POST** (one session, after the tasks): regenerates the API types, bumps the plugin version, updates specs and the WBS, adds the e2e spec, runs every check.
- **Before a task:** read the proposal section named in the task, the spec file it names, and the code files it lists. Follow CLAUDE.md, especially: re-read a file before editing it, don't undo other sessions' changes, no commits.
- **When a task is done:** its *Done when* list is true, the checks for every app it touched pass (README "Checks"), and the session reports the files changed, the checks run and their results, and any assumption it added to the WBS.

## 2. Rules for every task

1. **Server layout:** a new feature is a new module under `server/app/modules/<name>/` with the same folders as `runs` and `gaps` (`domains`, `infrastructure`, `models`, `ports`, `typing`, `usecases`, `utils`, `router.py`, `mcp_tools.py`, `dependencies.py`, `errors.py`). Layer rules are enforced by `lint-imports`; a new module gets its contract in the import-linter config in PRE.
2. **Migrations:** only the numbers reserved in §4. PRE writes an empty stub for each of the wave's reserved migrations in chain order, so a task fills in its own file and the chain is never broken.
3. **Permissions:** new capabilities are added only in PRE (`server/app/shared/permissions/capability.py` and `role_capabilities.py`), with the role mapping in §4.2. Every new REST route is classified in the route catalog (`tests/api/security/`), or the security test fails (SEC-15).
4. **MCP tools:** registered in the module's `mcp_tools.py` with `build_mcp_tool_meta(<capability>)`, snake_case arguments, short JSON replies that never repeat the input, and secrets masked.
5. **Client layout:** a new feature is a module under `client/src/modules/<name>/` (`components`, `hooks`, `test`, `typing`, `utils`), with routes under `client/src/app/(app)/projects/[projectKey]/`. Screens use only the design-system components in `client/src/components/design-system/`. Every string goes in the EN, FR and VI locale files. Data goes through react-query hooks on `apiClient`, and live updates through `LIVE_EVENT_QUERY_KEYS`.
6. **Plugin (`claude/`):** skills reference bundled files with `${CLAUDE_PLUGIN_ROOT}`. Scripts and hooks use only the Python standard library and run on Python 3.9. Tasks don't bump the version; POST does it once per wave, in `plugin.json` and `.mcp.json` together.
7. **API types:** tasks may run `export_openapi` and `npm run generate:api` locally to build their screens. POST runs them last, so the committed `openapi.json` and `openapi.type.ts` match the whole wave.
8. **Tests:** each task adds pytest (use cases, routes, MCP tools, permissions), Vitest (screens, hooks, utils) and, for plugin work, unittest under `claude/hooks/tests/`. Each wave's POST adds one e2e spec in `e2e/tests/`.
9. **Docs:** each task writes the feature's behaviour in its spec file in `docs/spec/` (new spec files are listed per task). POST sets the WBS status and writes the assumptions the tasks chose into "Assumptions & blockers".

## 3. Waves at a glance

| Wave | Features (proposal) | WBS | Parallel sessions | Depends on |
| --- | --- | --- | --- | --- |
| W9 Gaps and case quality | F18 answer gaps with Claude, labels from F1, F13 flaky cases, F3 version compare and review comments | 9.18, 9.1 (labels), 9.13, 9.3 | 5 | Nothing; starts now, in parallel with go-live (M9) |
| W10 Suites, plans and shared steps | F1 suites and plans, F2 shared steps and data-driven cases | 9.1, 9.2 | 4, then 2 | W9 (labels) |
| W11 Jira, integrations and insights | F4 two-way Jira, F6 notifications, webhooks, API scope and JUnit import, F5 insights and export | 9.4, 9.6, 9.5 | 5 | W10 (suite runs feed insights and JUnit import) |
| W12 Scripts | F8 scripts from passing runs, F17a script runs, F14 better evidence | 9.8, 9.17, 9.14 | 4 | W10 (run snapshots), W11 (executor `ci` pattern) |
| W13 Matrix, checks and API steps | F15 browsers and screen sizes, F11 accessibility and speed, F16 API steps, F13 quarantine in script runs | 9.15, 9.11, 9.16, 9.13 | 4 | W12 |
| W14 Exploration, picking and visual | F10 exploratory sessions, F12 picking regression cases, F9 screenshot comparison | 9.10, 9.12, 9.9 | 4 | W12 (script screenshots for F9), W9 (labels for F12) |
| W15 Company basics | F7 SSO, full audit log, failure comments | 9.7 | 3 | Nothing; can run beside any wave from W10 on |

## 4. Shared reservations

### 4.1 Migrations

The file is `<number>_<slug>.py`. The revision id is the number alone (`revision = "0020"`), as in the existing migrations, and `down_revision` is the row above.

| Number | Slug | Wave, task | Contents |
| --- | --- | --- | --- |
| 0020 | `gap_answer_search` | W9.T1 | `gaps.answered_via_token_id`; generated `tsvector` column on question and answer, GIN index |
| 0021 | `create_labels` | W9.T3 | `labels`, `test_case_labels` |
| 0022 | `add_flaky_cases` | W9.T4 | `test_cases.flaky_score`, `flaky_since`, `quarantined_at`, `quarantined_by` |
| 0023 | `create_review_comments` | W9.T5 | `test_case_review_comments`; `projects.require_separate_reviewer` |
| 0024 | `create_suites` | W10.T1 | `test_suites`, `test_suite_cases`; `runs.story_id` nullable; `runs.test_suite_id`; check "exactly one of story or suite"; partial unique index "one running run per suite"; `runs.executor` check gains `script` and `ci` |
| 0025 | `create_plans` | W10.T3 | `test_plans`, `test_plan_items` |
| 0026 | `create_shared_steps` | W10.T5 | `shared_steps`, `shared_step_versions`; `test_case_versions.parameters`, `data_rows`; `run_cases.steps`; `case_results.iteration` and its new unique key |
| 0027 | `add_jira_write` | W11.T1 | `failures.jira_issue_key`, `jira_issue_url`, `jira_issue_status`, `jira_issue_done_at`; `projects.jira_bug_issue_type`, `jira_post_results` |
| 0028 | `create_notification_channels` | W11.T3 | `notification_preferences`, `project_chat_channels` |
| 0029 | `create_webhooks` | W11.T4 | `webhooks`, `webhook_deliveries`; `api_tokens.scope` |
| 0030 | `create_daily_stats` | W11.T5 | `project_daily_stats` |
| 0031 | `create_scripts` | W12.T1 | `test_case_scripts`, `test_case_script_versions`; `test_cases.is_automatable` |
| 0032 | `add_script_runs` | W12.T2 | `stored_files.kind` gains `trace` and `video`; `case_results.repro_steps`; suspected cause gains `script_out_of_date`; `run_access_tokens` (if spike S1 needs it) |
| 0033 | `add_run_matrix_and_checks` | W13.T1, W13.T2, W13.T3 | `runs.browser`, `viewport`, `run_group_id`; `step_results.checks`; `projects.accessibility_mode` (step `kind` lives in JSONB, no column) |
| 0034 | `create_exploratory_sessions` | W14.T1 | `exploratory_sessions`, `exploratory_findings` |
| 0035 | `add_label_paths` | W14.T3 | `label_paths`; `stories.jira_components`, `jira_labels` |
| 0036 | `create_visual_baselines` | W14.T4 | `visual_baselines`; `step_results.visual_diff_ratio`, `visual_diff_file_id`, `visual_status`; `projects.visual_threshold` |
| 0037 | `add_sso_audit_comments` | W15 | `workspace_sso`, `user_identities`; `audit_events.action` widened; `failure_comments` |

W13 shares one migration across three tasks: the W13 PRE writes all of 0033's columns itself.

### 4.2 New capabilities

| Capability | Admin | PM | BA | QC | Dev | Viewer | Wave |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `suite.edit` | ✓ | | | ✓ | | | W10 |
| `plan.edit` | ✓ | ✓ | | ✓ | | | W10 |
| `plan.sign_off` | ✓ | | | ✓ | | | W10 |
| `test_case.quarantine` | ✓ | | | ✓ | | | W9 |
| `failure.create_jira_issue` | ✓ | | | ✓ | ✓ | | W11 |
| `integration.manage` (chat channels, webhooks) | ✓ | | | | | | W11 |
| `script.review` | ✓ | | | ✓ | | | W12 |
| `visual.review` | ✓ | | | ✓ | | | W14 |
| `failure.comment` | ✓ | ✓ | ✓ | ✓ | ✓ | | W15 |
| Workspace `audit.view` | Owner and workspace admins | | | | | | W15 |
| Workspace `sso.manage` | Owner and workspace admins | | | | | | W15 |

Existing capabilities reused:
- `gap.answer` and `gap.reassign`: F18 tools.
- `test_data.edit`: `set_test_data`.
- `test_case.edit`: labels, shared steps, review comments, saving a script.
- `run.start`: suite runs, script runs and exploratory sessions.
- `report.view`: Insights and exports.

### 4.3 New MCP tools

| Tool | Module | Capability | Wave |
| --- | --- | --- | --- |
| `get_my_gaps(story_key?)` | gaps | `gap.answer` | W9 |
| `answer_gap(gap_id, answer)` | gaps | `gap.answer` | W9 |
| `reassign_gap(gap_id, assignee_user_id?, assignee_role?)` | gaps | `gap.reassign` | W9 |
| `set_test_data(key, value, kind, environment?)` | test_data | `test_data.edit` | W9 |
| `get_suite_context(suite)` | suites | `run.view` | W10 |
| `start_run(..., suite?, executor?, browser?, viewport?)` | runs (extended) | `run.start` | W10, W12, W13 |
| `record_case_result(..., iteration?, repro_steps?, checks?)` | runs (extended) | `run.start` | W10, W12, W13 |
| `get_case_for_automation(case_code)` | scripts | `test_case.view` | W12 |
| `save_case_script(case_code, test_case_version_id, source)` | scripts | `test_case.edit` | W12 |
| `get_script_bundle(run_id)` | scripts | `run.start` | W12 |
| `set_case_cause(case_result_id, cause, reason)` | runs | `run.start` | W12 |
| `start_session`, `record_finding`, `finish_session` | exploratory | `run.start` | W14 |
| `list_cases(filter)` | test_cases | `test_case.view` | W14 |

### 4.4 New plugin skills and scripts

| Skill or script | Wave |
| --- | --- |
| `/tessio:answer-gaps` | W9 |
| `/tessio:run-suite` | W10 |
| `/tessio:automate-cases`, `/tessio:run-scripts`, `/tessio:repair-script`, `claude/scripts/run_scripts.py` | W12 |
| `/tessio:explore`, `/tessio:pick-regression` | W14 |

### 4.5 New background jobs (BullMQ, ADR 0006)

| Job | Wave |
| --- | --- |
| `test_cases.recompute_flaky` (after each result; nightly sweep) | W9 |
| `jira.create_issue`, `jira.post_comment` | W11 |
| `notification.email`, `chat.deliver` | W11 |
| `webhook.deliver` | W11 |
| `insights.daily_snapshot` (nightly), `report.export` | W11 |
| `files.delete_expired_evidence` (traces and videos after 30 days) | W12 |
| `visual.compare` | W14 |

### 4.6 New dependencies

| Dependency | App | Wave | Spike |
| --- | --- | --- | --- |
| `@mantine/charts` (Recharts underneath), wrapped as design-system charts | client | W11 | No |
| `weasyprint` plus Pango in the server image | server | W11 | S3 |
| `defusedxml` (safe JUnit parsing) | server | W11 | No |
| Node and Playwright on testers' computers (not in Tessio) | plugin users | W12 | S2 |
| `@playwright/test` and `@axe-core/playwright`, in the generated bundle only | bundle | W12, W13 | No |
| `pillow` | server | W14 | S4 |
| `authlib` (OIDC) | server | W15 | S5 |

## 5. Spikes

Run each spike in its wave's PRE, write the result into the WBS assumptions, and adjust the tasks if the answer is "no".

| ID | Question | Wave | If the answer is no |
| --- | --- | --- | --- |
| S1 | Do Bash commands that Claude runs see `CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN`, as the hooks do? `run_scripts.py` needs the token to upload results. | W12 | `start_run` with `executor="script"` returns a run token: valid 4 hours, for this run only, limited to results, uploads and secrets. Claude passes it to the script as an environment variable. Table `run_access_tokens` in 0032. |
| S2 | Can Claude reliably turn Claude in Chrome's accessibility tree into `getByRole` and `getByLabel` locators that pass on the first or second try? Try it on 5 real cases. | W12 | Add a step: Claude opens the page with `npx playwright codegen` and edits the result instead. |
| S3 | Does WeasyPrint install and render on Python 3.14 in `python:3.14-slim` with Pango? | W11 | Generate the PDF with ReportLab (pure Python, simpler layout). |
| S4 | Pillow wheels for Python 3.14 on amd64 and arm64. | W14 | Compare screenshots with `numpy` on decoded PNGs, or move F9 to the client. |
| S5 | Authlib with FastAPI on Python 3.14 for Google and Microsoft OIDC. | W15 | Plain OAuth code flow with `httpx` and `PyJWT`. |
| S6 | Does the Jira account need anything beyond *Create issues*, *Add comments* and *Create attachments*? Check on a real site (blocker B-6). | W11 | Show the missing permission on the Jira settings card and hide the buttons. |
| S7 | Teams: incoming webhooks are being replaced by Workflows webhooks. Which URL and payload work today? | W11 | Ship Slack first, and Teams once a working payload is confirmed. |

## 6. Wave W9: gaps and case quality

### W9.PRE

- Reserve and stub migrations 0020 to 0023.
- Add capability `test_case.quarantine`.
- Add error codes: `GAP_NOT_ASSIGNABLE_HERE` (only if the reassign rules need it), `REVIEW_COMMENTS_OPEN`, `REVIEWER_IS_AUTHOR`.
- Add a `labels` module skeleton and its import-linter contract.
- Add the translation namespace `labels` in EN, FR and VI.

### W9.T1 Answer gaps: server (F18, WBS 9.18)

- **Depends on:** nothing.
- **Read:** proposal F18; [readiness-review spec](../spec/readiness-review.md); `server/app/modules/gaps/usecases/answer_gap.py`, `reassign_gap.py`, `list_gap_inbox.py`, `mcp_tools.py`.
- **Server:**
  1. Migration 0020: `gaps.answered_via_token_id`, and a generated `search_vector` (`to_tsvector('simple', question || ' ' || coalesce(answer, ''))`) with a GIN index.
  2. `GetMyGapsUseCase`: open gaps assigned to the actor or to a role queue the actor is in, in the token's project, optionally for one story. For each gap:
     - the story key and title;
     - the target AC or case text at its current version;
     - up to three answered gaps whose `search_vector` matches the question best, from the same story first, then the project.
  3. MCP tools `get_my_gaps`, `answer_gap` and `reassign_gap`. They call the existing answer and reassign use cases, so the rules, `gap.changed` and `gap_assigned` behave exactly as in REST. `answer_gap` stores `answered_via_token_id`.
  4. MCP tool `set_test_data` in the `test_data` module. Kinds `variable` and `endpoint` only; `kind="secret"` is refused with `INVALID_REQUEST`. An existing key is updated (with the environment's override rule), and a new key is created.
  5. Show "via Claude" on answered gaps, as raised gaps already do (REST field `answeredViaClaude`).
- **Tests:** use case and MCP tests for each tool, including another project's gap (404), a Viewer token (403), a secret kind (refused) and role-queue matching. Plus a search ranking test.
- **Spec:** readiness-review.md gets GAP-8 (answer with Claude). test-data spec: `set_test_data`.
- **Done when:** the four tools work against a test database and pytest, mypy and lint-imports pass.

### W9.T2 Answer gaps: plugin skill (F18, WBS 9.18)

- **Depends on:** W9.T1's tool names and replies (can start from the proposal and finish after T1).
- **Read:** proposal F18; `claude/skills/review-readiness/SKILL.md`; `claude/skills/run-story-tests/SKILL.md` and `references/execute-cases.md`.
- **Plugin:**
  1. New `claude/skills/answer-gaps/SKILL.md` that follows the proposal's flow and guardrails exactly. Allowed tools: the Tessio MCP tools, `Read`, `Grep` and `Glob` (to cite product code), and Claude Code's question prompt.
  2. A shared procedure `claude/skills/answer-gaps/references/when-gaps-block.md`. `run-story-tests`, `rerun-failed` and later `run-suite` and `run-scripts` link to it for `GAPS_OPEN`: list the gaps by assignee, offer `/tessio:answer-gaps` for the ones the caller can answer, and name who must answer the rest.
  3. README contents table and skill count updated.
- **Tests:** `test_plugin_files.py` checks that the skill exists, has valid front matter and references only bundled files. `claude plugin validate claude --strict` passes.
- **Done when:** a dry run against a local server answers two gaps, reassigns one and skips one (done by hand, reported as checked or not verified).

### W9.T3 Labels (from F1, WBS 9.1)

- **Depends on:** W9.PRE.
- **Server:** module `labels`. Migration 0021. REST:
  - `GET/POST …/labels` and `PATCH/DELETE …/labels/{label_id}`. Delete is refused while a suite filter uses the label (that check arrives in W10; for now delete removes the links).
  - `PUT …/test-cases/{case_code}/labels`.
  - The case list filter accepts `label`.
  - `get_story_context` includes each case's labels.
- **Client:** label manager in project settings, a label picker in the case editor, label chips and a filter on the case list.
- **Tests:** pytest for CRUD, permissions, filter and isolation. Vitest for the picker and filter.
- **Spec:** test-cases.md (labels).

### W9.T4 Flaky cases and quarantine flag (F13, WBS 9.13)

- **Depends on:** W9.PRE.
- **Server:**
  1. Migration 0022.
  2. `RecomputeFlakyUseCase` with the proposal's rule: three or more pass↔fail flips in the last 10 results on the same case version. It runs as job `test_cases.recompute_flaky` after each recorded result (enqueued from the runs module through a port), plus a nightly sweep.
  3. Quarantine routes: `PUT/DELETE …/test-cases/{case_code}/quarantine` (`test_case.quarantine`). A case leaves quarantine automatically after 10 passes in a row.
  4. The case list and `case-latest-results` gain `isFlaky` and `isQuarantined`.
- **Client:** flaky and quarantine badges, a filter, and quarantine actions on the case detail.
- **Note:** quarantine changes nothing in runs until script runs exist (W13.T4). Until then it is a label with an audit trail.
- **Tests:** flip-count unit tests (boundaries 2, 3, 10 results; version change resets), job and route tests.
- **Spec:** test-cases.md (flaky and quarantine).

### W9.T5 Version compare and review comments (F3, WBS 9.3)

- **Depends on:** W9.PRE.
- **Server:**
  1. Migration 0023.
  2. Review comments REST: `GET/POST …/test-cases/{case_code}/review-comments` and `PUT …/review-comments/{comment_id}/resolve`.
  3. Moving a case to *Ready* is refused with `REVIEW_COMMENTS_OPEN` while a comment is open.
  4. The project setting `requireSeparateReviewer` refuses an author's own review with `REVIEWER_IS_AUTHOR`.
- **Client:** a *Compare versions* view (two version pickers, steps shown side by side, changed lines highlighted, using the existing versions route), a comments panel on the case review screen, and the setting in project settings.
- **Tests:** rules, permissions, compare util unit tests.
- **Spec:** test-cases.md (review).

### W9.POST

- Run `export_openapi` and `generate:api`.
- Plugin version: **minor bump** (new skill and new MCP tools refuse older plugins).
- Add e2e `12-answer-gaps.spec.ts`: answer a gap through REST with "via Claude", see the story unblocked. The skill itself isn't e2e-tested.
- Update the WBS rows to ✅ or 🚧, and add M12 to the release plan.

## 7. Wave W10: suites, plans and shared steps

### W10.PRE

- Stub migrations 0024 to 0026.
- Add capabilities `suite.edit`, `plan.edit` and `plan.sign_off`.
- Add modules `suites`, `plans` and `shared_steps` with import-linter contracts. `runs` may depend on `suites` through a port only.
- Add error codes `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY` and `PLAN_FAILURES_ACTIVE`.
- Add live events `suite.changed` and `plan.changed`.
- Add translation namespaces `suites`, `plans` and `sharedSteps`.
- Add the sidebar entries *Suites* and *Plans* to the client shell.

### W10.T1 Suites and suite runs: server (F1, WBS 9.1)

- **Depends on:** W9.T3 (labels for "add by filter").
- **Read:** proposal F1; [runs spec](../spec/runs.md); `server/app/modules/runs/usecases/start_run.py`, `run_start_gate.py`, `finish_run.py`, `record_case_result.py`; `server/app/modules/insights/usecases/*`.
- **Server:**
  1. Migration 0024, including the `executor` values `script` and `ci`, so `runs` is migrated once.
  2. Suites module:
     - REST: `GET/POST …/suites`, `GET/PATCH …/suites/{suite_id}`, `POST …/suites/{suite_id}/archive`.
     - REST: `PUT …/suites/{suite_id}/cases` (ordered list), `POST …/suites/{suite_id}/cases/by-filter` (label, priority, story, sprint; adds the matches once).
  3. `start_run` accepts `suite`.
     - `run_start_gate` refuses with `GAPS_OPEN` while any story of a case in the suite has an open gap, and lists those gaps with their assignees.
     - Runs only *Ready* cases. Skips and reports *Needs review* cases.
     - Refuses an empty selection with `SUITE_EMPTY`.
     - Enforces one running run per suite (`SUITE_ALREADY_RUNNING`, with a race test like SEC-7).
  4. Suite runs never change a story's test status. `finish_run` and the report group results by story.
  5. Every read model that assumed `runs.story_id` handles a suite run:
     - run list (filter by suite);
     - run detail;
     - dashboard;
     - my work;
     - story progress (counts the suite's results for each case's story);
     - traceability (the latest result per case, whatever the run);
     - notifications payload;
     - the stale-run abort.
  6. MCP: `get_suite_context(suite)` (cases grouped by story, like `get_story_context`) and `start_run(suite=...)`. `get_failed_cases` and re-run failed work for suite runs.
- **Tests:**
  - the gate (gap on one story blocks; Needs review skipped);
  - the race;
  - every read model with a suite run present;
  - permissions and isolation;
  - existing run tests still pass unchanged.
- **Spec:** new `docs/spec/suites-and-plans.md`; runs.md updated (suite runs, executor values).

### W10.T2 Suites: client (F1, WBS 9.1)

- **Depends on:** W10.T1 routes (start from the proposal; finish after T1).
- **Client:** module `suites`.
  - Suites list.
  - Suite detail: cases with drag-to-reorder, *Add cases*, *Add by filter*, *Start manual run*.
  - The Claude command to copy (`/tessio:run-suite <name>`).
  - Run list and run detail show the suite and group results by story.
  - Manual run creation accepts a suite.
- **Tests:** Vitest for list, detail, filter dialog, run detail grouping.

### W10.T3 Test plans (F1, WBS 9.1)

- **Depends on:** W10.T1.
- **Server:** module `plans`. Migration 0025.
  - REST: `GET/POST …/plans`, `GET/PATCH …/plans/{plan_id}`, `PUT …/plans/{plan_id}/items`.
  - REST: `POST …/plans/{plan_id}/sign-off` (refused with `PLAN_FAILURES_ACTIVE` while failures on the plan's cases are active) and `POST …/plans/{plan_id}/close`.
  - Plan progress read model: for each case in the plan's suites and stories, the latest result since the plan opened, plus open failures and open gaps.
  - The `plan.signed_off` event (used by webhooks in W11).
- **Client:** module `plans`. Plans list, plan detail (progress bar, cases by status, blockers, sign-off).
- **Tests:** progress calculation, sign-off rule, permissions.
- **Spec:** suites-and-plans.md (plans).

### W10.T4 Suite runs: plugin skill (F1, WBS 9.1)

- **Depends on:** W10.T1 (MCP), W9.T2 (gap procedure).
- **Plugin:** `claude/skills/run-suite/SKILL.md`.
  - Starts with `get_suite_context` and `start_run(suite=...)`.
  - Runs at most 50 cases per run and starts a follow-up run for the rest.
  - Reuses `run-story-tests/references/execute-cases.md` for each case, and `when-gaps-block.md` for `GAPS_OPEN`.
- **Tests:** plugin file tests and `claude plugin validate`.

### W10.T5 Shared steps and data-driven cases: server (F2, WBS 9.2)

- **Depends on:** W10.T1 (both change `runs`; run it after T1 is merged into the tree).
- **Read:** proposal F2; test-cases.md; `server/app/modules/test_cases/*` (version save, import), `story_context`, `runs/usecases/start_run.py`, `record_case_result.py`, `record_manual_case_result.py`.
- **Server:**
  1. Migration 0026.
  2. Module `shared_steps`:
     - REST: `GET/POST …/shared-steps`, `GET/PATCH …/shared-steps/{key}` (a save adds a version), `GET …/shared-steps/{key}/usage`.
  3. Test case version validation: a step is `{action, expected}` or `{shared_step_key}`. Parameters (≤ 20) and data rows (≤ 20) are allowed, with no secrets in rows (a value matching a secret key's `{{data.key}}` is fine; a literal secret isn't).
  4. `start_run` writes `run_cases.steps` with shared steps expanded and orders renumbered.
     - `get_story_context` and `get_suite_context` return the expanded steps and the data rows.
     - Step results validate against the snapshot, not the current case.
  5. `record_case_result` and the manual record route take `iteration` (default 0).
     - The unique key becomes (run, case, iteration).
     - Latest result, AC status and failures use the worst iteration.
  6. The CSV and xlsx import and `create_draft_cases` accept plain steps only (shared steps are added in the editor). *Assumption, written in the WBS.*
- **Tests:** expansion and renumbering, snapshot stability after a shared step edit, iteration uniqueness, the worst-iteration rule, old runs without `run_cases.steps` (they fall back to the case version).

### W10.T6 Shared steps and data-driven cases: client and plugin (F2, WBS 9.2)

- **Depends on:** W10.T5.
- **Client:**
  - Shared step library page with "Used by N cases".
  - Case editor: insert a shared step (shown collapsed, expandable read-only), parameters and data rows table editor.
  - Run detail and the manual recording screen show one block per iteration.
- **Plugin:** `execute-cases.md` handles iterations: one `record_case_result` per iteration with `iteration`.
- **Tests:** Vitest for editor, library and recording. Plugin file tests.

### W10.POST

- Run `export_openapi` and `generate:api`.
- Plugin version: minor bump.
- Add e2e `13-suite-run.spec.ts`: create a suite by label, see the gap block, answer it, run it manually, sign off a plan.
- Update the WBS and add M13 to the release plan.

## 8. Wave W11: Jira, integrations and insights

### W11.PRE

- Stub migrations 0027 to 0030.
- Add capabilities `failure.create_jira_issue` and `integration.manage`.
- Add modules `integrations` (chat channels and webhooks) and `reports` (export) with their contracts.
- Add error codes: `JIRA_WRITE_NOT_ALLOWED`, `JIRA_ISSUE_ALREADY_LINKED`, `WEBHOOK_URL_INVALID`, `JUNIT_INVALID`, `TOKEN_SCOPE_NOT_ALLOWED`.
- Run spikes S3, S6 and S7.
- Add `@mantine/charts` and wrap it as design-system chart components (`DSLineChart`, `DSBarChart`, `DSDonutChart`) using semantic color tokens, light and dark.

### W11.T1 Two-way Jira: server (F4, WBS 9.4)

- **Depends on:** W11.PRE (S6).
- **Read:** proposal F4; `server/app/modules/jira/*` (client, sync); failures spec.
- **Server:**
  1. Migration 0027.
  2. Jira client:
     - create issue (ADF description);
     - add attachment (with the `X-Atlassian-Token: no-check` header);
     - add comment;
     - link issues;
     - `mypermissions`.
     All with the existing rate-limit retry.
  3. Saving the Jira connection stores whether it can write. `GET workspace/jira` returns `canCreateIssues` and `canComment`.
  4. `POST …/failures/{failure_id}/jira-issue` enqueues job `jira.create_issue` and returns 202.
     - The job builds the summary and description from the failure (failing step, expected and actual results, steps to reproduce when present, environment, suspected cause, link), attaches the failing screenshot and links the issue to the story.
     - It stores the key and URL, adds a `jira_issue_created` failure event and publishes `failure.changed`.
     - A second create gives `JIRA_ISSUE_ALREADY_LINKED`.
  5. Sync refreshes the linked issues' status in one JQL search (`key in (...)`) and sets `jira_issue_done_at` when the status category is Done.
  6. Project setting `jiraPostResults` (`off`, `on_sign_off`, `every_run`). After story sign-off or run finish, job `jira.post_comment` posts the counts and a link on the story.
- **Tests:** a fake Jira for every call; the job (success, 403 without permission → `JIRA_WRITE_NOT_ALLOWED` recorded on the failure, retry on 429); sync status; projects without Jira refused.
- **Spec:** failures.md (Jira bug), settings.md (write check), sprints-and-stories.md (comment on the story).

### W11.T2 Two-way Jira: client (F4, WBS 9.4)

- **Depends on:** W11.T1.
- **Client:**
  - *Create Jira bug* on the failure detail, with a preview of the summary and description.
  - The Jira key and status on the failure detail and list, and a "Done in Jira" badge.
  - Write-permission rows on the Jira settings card.
  - The post-results setting in project settings.
  - All hidden in projects without Jira.
- **Tests:** Vitest for the button states (no permission, already linked, pending job).

### W11.T3 Email, Slack and Teams notifications (F6, WBS 9.6)

- **Depends on:** W11.PRE (S7).
- **Server:**
  1. Migration 0028.
  2. `notification_preferences` (user, kind, channel `in_app` / `email`). Defaults: email on for `gap_assigned` and `failure_assigned`.
  3. The notification service enqueues `notification.email` with EN, FR and VI templates, in the user's language.
  4. `project_chat_channels` (project, kind `slack` / `teams`, webhook URL encrypted with the secrets key, events). REST: `GET/POST/PATCH/DELETE …/chat-channels` and `POST …/chat-channels/{id}/test` (`integration.manage`).
  5. Job `chat.deliver` with Slack Block Kit and the Teams payload from S7.
- **Client:** notification settings in the profile (covers WBS 3.13.3), and chat channels in project settings.
- **Tests:** template rendering per language, preference filtering, encrypted URL never returned in full (masked), delivery retry.
- **Spec:** notifications.md, settings.md.

### W11.T4 Webhooks, API token scope and JUnit import (F6, WBS 9.6)

- **Depends on:** W10.T1 (executor `ci`, suites).
- **Server:**
  1. Migration 0029.
  2. Webhooks REST: `GET/POST/PATCH/DELETE …/webhooks`, `GET …/webhooks/{id}/deliveries` and `POST …/webhooks/{id}/redeliver/{delivery_id}` (`integration.manage`).
     - Job `webhook.deliver`: HMAC-SHA256 `X-Tessio-Signature`, five tries with backoff, deliveries kept 30 days.
     - Events subscribe through the existing Redis pub/sub events, not new code paths in each module.
  3. `api_tokens.scope`: `mcp` (default, today's behaviour) or `api`.
     - An `api` token is accepted on REST routes the route catalog marks `token_allowed`, which in this wave means the run import and read routes for runs, failures and cases.
     - Other routes give `TOKEN_SCOPE_NOT_ALLOWED`. An `mcp` token on REST is refused as today.
  4. `POST …/runs/import` (multipart: a JUnit XML file of 10 MB at most, `environment`, optional `suite`).
     - Parsed with `defusedxml`.
     - A test maps to a case when its name or a `tessio.case` property holds `TC-<n>`.
     - Creates a finished run with executor `ci`, one case result per mapped test (failed and errored become failed with the message as the error; skipped becomes skipped), and failures as usual.
     - Unmapped tests are listed in the run report.
- **Client:** webhooks in project settings (with a delivery log), a scope choice on the Connect Claude token form, an import dialog on the runs page, and the `ci` executor shown in run lists.
- **Tests:**
  - signature;
  - retry;
  - scope enforcement on every catalogued route;
  - JUnit parsing (Playwright, Jest and pytest samples, an XML bomb rejected);
  - mapping;
  - failures opened.
- **Spec:** new `docs/spec/integrations.md`; runs.md (import, `ci`).

### W11.T5 Insights and report export (F5, WBS 9.5)

- **Depends on:** W10.T1 (suite runs), W9.T3 (labels), W9.T4 (flaky).
- **Server:**
  1. Migration 0030.
  2. `insights.daily_snapshot` (nightly, per project) writes pass rate, runs by executor, failures opened and fixed, gaps opened and answered, and the median gap age.
  3. Routes: `GET …/insights/trends?from&to&groupBy=day|sprint`, `GET …/insights/coverage-by-label`, `GET …/insights/top-failing`, `GET …/insights/flaky`, `GET …/insights/tokens` (from `run_logs`).
  4. Module `reports`: `POST …/runs/{run_id}/export`, `POST …/plans/{plan_id}/export` and `POST …/stories/{jira_key}/export` with `format=md|pdf`.
     - Job `report.export` renders HTML from Jinja templates with secrets masked, then Markdown or a PDF (WeasyPrint, or ReportLab per S3).
     - Stores a `report` file and notifies the requester with a download link.
  5. Server Dockerfile gains Pango (if S3 passed).
- **Client:** module `insights`. An *Insights* page with date range and sprint picker, trend lines, a coverage-by-label bar chart, top-failing and flaky tables, and a tokens chart. *Export* buttons on the run report, plan and story.
- **Tests:** snapshot job math, routes, export job (Markdown content, PDF bytes start with `%PDF`, secrets masked).
- **Spec:** new `docs/spec/insights.md`; runs.md (export, closes WBS 3.10.7).

### W11.POST

- Run `export_openapi` and `generate:api`.
- No plugin bump unless a tool changed.
- Add e2e `14-jira-bug.spec.ts` (fake Jira) and `15-junit-import.spec.ts`.
- Check that the server image builds with the new system packages.
- Update the WBS and add M14 to the release plan.

## 9. Wave W12: scripts

### W12.PRE

- Stub migrations 0031 and 0032.
- Add capability `script.review`.
- Add module `scripts` with its contract.
- Add error codes `SCRIPT_NOT_APPROVED`, `NO_SCRIPTED_CASES` and `SCRIPT_VERSION_STALE`.
- Add the suspected cause value `script_out_of_date` (EN, FR and VI labels).
- Run spikes S1 and S2 and record the decisions.

### W12.T1 Scripts: storage, review and bundle (F8, WBS 9.8)

- **Depends on:** W10.T5 (shared steps become helpers).
- **Server:**
  1. Migration 0031.
  2. Scripts module:
     - MCP `get_case_for_automation` and `save_case_script`, which saves a version waiting for review and refuses with `SCRIPT_VERSION_STALE` if the case version moved on.
     - REST: `GET …/test-cases/{case_code}/scripts` (versions and source) and `POST …/scripts/{script_id}/versions/{n}/approve` or `/reject` (`script.review`).
     - REST: `PUT …/test-cases/{case_code}/automatable`.
  3. Saving a new case version marks the script `outdated` (through a port called from the test-case save use case).
  4. Bundle builder: a zip with `package.json` (`@playwright/test` pinned), `playwright.config.ts` (base URL from the environment, the browsers and viewports of the run, `trace: 'retain-on-failure'`, `video: 'retain-on-failure'`, a JSON reporter), `tessio/data.ts` (reads `TESSIO_DATA_<KEY>` variables), `tessio/helpers/<shared step key>.ts`, and one spec per approved script.
  5. MCP `get_script_bundle(run_id)` returns a signed download link.
- **Tests:** review flow and permissions, outdated marking, stale save, bundle contents (unzip and assert files and config), isolation.
- **Spec:** new `docs/spec/scripts.md`.

### W12.T2 Script runs: server (F17a and F14, WBS 9.17 and 9.14)

- **Depends on:** W12.T1.
- **Server:**
  1. Migration 0032.
  2. `start_run(executor="script")`:
     - only cases with an approved script; the rest are returned as `unscripted_cases`;
     - `NO_SCRIPTED_CASES` when there are none;
     - plus the run token if S1 needs it.
  3. REST for `run_scripts.py` (token auth, only the run's owner or its run token):
     - `POST /api/runs/{run_id}/script-results`: the same validation as `record_case_result`, one call per case;
     - `POST /api/runs/{run_id}/artifact-upload` (screenshot, trace, video; 50 MB limit for trace and video);
     - `POST /api/runs/{run_id}/secrets` (audited like `resolve_data`, actor = the user, `via=script`).
  4. MCP `set_case_cause` for script results.
  5. `record_case_result` takes `repro_steps` (≤ 20 lines) on failed cases (F14).
  6. Job `files.delete_expired_evidence` deletes traces and videos after 30 days.
  7. Quarantine is not applied yet (W13.T4).
- **Tests:** the script route equals the MCP route's rules (shared use case), ownership, audit, size limits, expiry job.
- **Spec:** runs.md (script runs, evidence), scripts.md.

### W12.T3 Scripts: plugin (F8 and F17a, WBS 9.8 and 9.17)

- **Depends on:** W12.T1 and W12.T2 tool shapes; the S1 and S2 results.
- **Plugin:**
  1. `claude/scripts/run_scripts.py`, standard library only, Python 3.9:
     - downloads and unzips the bundle into a temporary folder;
     - checks `node` and `npx` and prints the install command if missing;
     - runs `npm ci` once per bundle hash (cached in `~/.cache/tessio/bundles/<hash>`);
     - fetches secrets into the child process's environment only;
     - runs `npx playwright test`;
     - parses the JSON report;
     - uploads results and artifacts;
     - prints a summary of 30 lines at most, with no secret values.
  2. Skills:
     - `automate-cases` (the proposal's five steps);
     - `run-scripts` (the proposal's five steps, linking `when-gaps-block.md`);
     - `repair-script` (replay, decide drift or bug, save a new version or keep the failure, set the cause).
  3. `execute-cases.md`: write `repro_steps` on failed cases (F14).
- **Tests:** unittest for `run_scripts.py` with a fake server (`http.server` in a thread) and a fake `npx` on `PATH`: upload order, secret never printed, missing Node message, Python 3.9 compatible syntax. Plugin file tests. `claude plugin validate`.

### W12.T4 Scripts: client (F8, F14, WBS 9.8 and 9.14)

- **Depends on:** W12.T1 and W12.T2.
- **Client:**
  - A *Script* tab on the case: status, versions, read-only source with syntax highlighting (a design-system code block), approve and reject, and "not automatable".
  - The case list gets an automation column and filter.
  - Run detail for `script` runs: an executor badge, unscripted cases listed with the Claude command.
  - Failure detail: video player, trace download with the trace viewer hint, steps to reproduce, the *Script out of date* cause and the `/tessio:repair-script TC-n` command.
- **Tests:** Vitest for each new state.

### W12.POST

- Run `export_openapi` and `generate:api`.
- Plugin version: minor bump.
- Add e2e `16-script-review.spec.ts`: save a script version through REST with a token, approve it, see the run detail of an imported script run. The plugin script is covered by its unit tests.
- Update the guide [claude-setup.md](../guides/claude-setup.md): Node and Playwright for script runs.
- Update the WBS and add M15 to the release plan.

## 10. Wave W13: matrix, checks and API steps

### W13.PRE

- Write migration 0033 completely (all columns for T1 to T3).
- Add error code `STEP_KIND_INVALID`.
- Add translation keys for browsers, viewports and accessibility impacts.

### W13.T1 Browsers and screen sizes (F15, WBS 9.15)

- **Server:**
  - `start_run` takes `browsers[]` and `viewports[]`. For script runs, it creates one run per combination with a shared `run_group_id`. Claude runs allow one `chrome` run with `desktop` or `tablet`.
  - The bundle config emits matching Playwright projects.
  - The latest result and AC status take the worst result across the group's configurations.
  - `GET …/run-groups/{id}` returns the matrix.
- **Client:** browser and viewport pickers when starting a manual or Claude run (shows the command), a matrix view (cases × configurations), and badges on the run list.
- **Plugin:** `run-scripts` accepts `browser` and `viewport` arguments. `execute-cases.md` resizes the window for `tablet`.
- **Tests:** group creation, worst-result rule, bundle projects.

### W13.T2 Accessibility and speed checks (F11, WBS 9.11)

- **Server:** `step_results.checks` validation (impacts, rule ids, LCP, CLS, TTFB). The project setting `accessibilityMode` (`warn` / `fail_on_critical`) turns a critical violation into a failed step. Report section.
- **Bundle:** `@axe-core/playwright` scan after each navigation in a fixture, plus navigation timing written into the JSON report attachments. `run_scripts.py` uploads them.
- **Plugin:** `execute-cases.md` reads navigation timing with a short `javascript_tool` snippet after each page load and sends it as `checks`.
- **Client:** checks panel on the step, report section, project setting.
- **Tests:** validation, fail rule, report rendering, `run_scripts.py` parsing.

### W13.T3 API steps (F16, WBS 9.16)

- **Server:** step `kind` in case versions. An API step holds method, URL template, headers, body, `expect.status` and `expect.json[]` (path, `equals` or `exists`), validated on save (`STEP_KIND_INVALID`). `get_story_context` returns it as is.
- **Bundle:** the generated helper runs API steps with Playwright's `request` context. A case with only API steps doesn't open a browser.
- **Plugin:** `execute-cases.md` explains running API steps with `curl`, secrets from `resolve_data` never echoed, and evidence as the masked response status and the first 500 characters. `automate-cases` writes API steps with `request`.
- **Client:** a step type switch in the editor, an API step form, and the step result showing request and response (masked).
- **Tests:** validation, masking of responses, editor.

### W13.T4 Quarantine in script runs (F13, WBS 9.13)

- **Server:** in script runs, a failed result on a quarantined case opens no failure and doesn't fail the run. The run report lists it under "Quarantined". Ten passes in a row lift quarantine (the W9.T4 rule now has script results to count).
- **Client:** a quarantined section in run detail and report.
- **Tests:** run status with quarantined failures, no failure opened, auto-release.

### W13.POST

- Run `export_openapi` and `generate:api`.
- Plugin version: minor bump.
- Add e2e `17-api-step.spec.ts` (editor and validation).
- Update the WBS and add M16 to the release plan.

## 11. Wave W14: exploration, picking and visual

### W14.PRE

- Stub migrations 0034 to 0036.
- Add capability `visual.review`.
- Add modules `exploratory` and `visual` with their contracts.
- Run spike S4.
- Add Pillow to the server dependencies.

### W14.T1 Exploratory sessions: server and client (F10, WBS 9.10)

- **Server:** module `exploratory`. Migration 0034. MCP `start_session`, `record_finding` (screenshot through the existing upload hook pattern, extended to `record_finding`) and `finish_session`. REST:
  - `GET …/stories/{jira_key}/sessions`;
  - `GET …/sessions/{id}`;
  - `POST …/findings/{id}/to-gap`, `/to-draft-case` and `/to-jira-bug` (uses W11's Jira job).
- **Client:** a *Sessions* tab on the story with the session list, findings with screenshots, and the convert actions.
- **Tests:** tools, conversions, permissions.
- **Spec:** new `docs/spec/exploratory-sessions.md`.

### W14.T2 Exploratory sessions: plugin (F10, WBS 9.10)

- **Depends on:** W14.T1 tool shapes.
- **Plugin:**
  - Skill `explore` with the charter and the 60-action limit.
  - Findings are recorded as they happen, and a summary closes the session.
  - The upload hook matcher is extended to `record_finding`.
- **Tests:** hook tests for the new matcher, plugin file tests.

### W14.T3 Picking regression cases (F12, WBS 9.12)

- **Server:**
  - Migration 0035.
  - Label paths REST: `PUT …/labels/{id}/paths`.
  - `POST …/selections` (changed paths → cases through globs, plus cases of stories with matching Jira components or labels).
  - MCP `list_cases(filter)` (story, label, priority, status, flaky, automated; paged by 100).
  - The Jira sync stores components and labels.
- **Plugin:** skill `pick-regression`:
  1. Runs `git diff --name-only main...HEAD`.
  2. Calls the selection route, then `list_cases`.
  3. Proposes the set with reasons.
  4. On confirmation, starts a Claude run, a script run or saves a suite.
- **Client:** a paths editor on labels.
- **Tests:** glob matching, sync mapping, tool paging.

### W14.T4 Screenshot comparison (F9, WBS 9.9)

- **Depends on:** W12 (script screenshots), W13.T1 (viewport and browser on runs).
- **Server:**
  - Module `visual`. Migration 0036.
  - After a screenshot upload completes for a run with comparison on (script runs by default), enqueue `visual.compare`. It loads the baseline for (case, step, environment, browser, viewport), applies masked regions, computes the diff ratio with Pillow, stores a diff image and sets `visual_status` (`no_baseline`, `same`, `changed`).
  - REST: `POST …/step-results/{id}/accept-baseline` (`visual.review`), `PUT …/visual-baselines/{id}/masks`, and the project setting `visualThreshold`.
  - A changed step never fails the case.
  - The first screenshot becomes the baseline only when QC accepts it.
- **Client:** a *Visual change* flag on steps, a review view (baseline, new image and diff, with a slider), accept or open failure, and a mask editor (draw rectangles).
- **Tests:** diff math on fixture images, masks, status per case, permissions.
- **Spec:** new `docs/spec/visual-comparison.md`.

### W14.POST

- Run `export_openapi` and `generate:api`.
- Plugin version: minor bump.
- Add e2e `18-visual-review.spec.ts` (accept a baseline on seeded images).
- Update the WBS and add M17 to the release plan.

## 12. Wave W15: company basics

Can run beside any wave from W10 on. It touches `auth`, `audit` and `failures` only.

### W15.PRE

- Stub migration 0037.
- Add workspace capabilities `audit.view` and `sso.manage`, and capability `failure.comment`.
- Run spike S5.

### W15.T1 Google and Microsoft sign-in (F7, WBS 9.7)

- **Server:**
  - `workspace_sso` (provider, client id, client secret encrypted, allowed email domains, enabled) and `user_identities`.
  - The OIDC code flow with PKCE and state.
  - **Invite-only stays:** an SSO sign-in works only for an existing active or invited user with the same verified email. An invited user becomes active on first SSO sign-in.
  - An SSO session counts as two-factor passed. Password sign-in stays available unless the workspace turns it off for non-admins.
- **Client:** SSO buttons on sign-in, the SSO settings card for workspace admins.
- **Tests:** a fake identity provider, email matching, unknown email refused, domain rule, rate limits as for sign-in.
- **Spec:** authentication-and-account.md.

### W15.T2 Full audit log (F7, WBS 9.7, covers 4.10)

- **Server:**
  - Widen `audit_events.action` to every write.
  - A small `AuditRecorder` port called by write use cases (start with users, members, roles, tokens, Jira connection, test data, environments, cases and runs).
  - `GET /api/audit-events` with filters (actor, project, action, date), `audit.view`.
- **Client:** an audit log page under workspace settings.
- **Tests:** each listed write records one event, filters, permissions.

### W15.T3 Failure comments (F7, WBS 9.7, covers 3.11.4)

- **Server:**
  - `failure_comments` and REST `GET/POST …/failures/{id}/comments`.
  - @mentions of project members send a `failure_mentioned` notification.
  - Comments appear in the failure timeline.
- **Client:** a comments box with mention autocomplete on the failure detail.
- **Tests:** mention parsing, notification, Viewer refused.

### W15.POST

- Run `export_openapi` and `generate:api`.
- Add e2e `19-failure-comment.spec.ts`.
- Update the WBS and add M18 to the release plan.

## 13. Risks

| Risk | Effect | Mitigation |
| --- | --- | --- |
| Making `runs.story_id` nullable (W10.T1) breaks a read model nobody listed | Wrong dashboard or traceability numbers | T1 greps every `story_id` use in `runs`, `insights`, `failures`, `notifications` and `run_logs`, with a test for each read model with a suite run present |
| Claude-written scripts are brittle (S2) | Script runs fail for no reason, and people stop trusting them | QC approval, `outdated` marking, flaky detection, quarantine, `repair-script` |
| Parallel sessions edit the same shared files | Lost changes | PRE reserves migrations, capabilities, error codes, events, namespaces and nav entries; tasks keep to their module folders; re-read before editing (CLAUDE.md) |
| Plugin bumps in every wave | Users must update often | One bump per wave, at POST only; the update command is in the `PLUGIN_OUTDATED` reply |
| Go-live work (M9 to M11) runs at the same time | Fixes for the pilot collide with W9 and W10 | Pilot fixes go first; W9 and W10 avoid `runs` changes until the pilot sprint is over, if they overlap |
| Server image grows (Pango, Pillow) | Slower builds and deploys | Measure the image size in W11.POST and W14.POST; slim packages only |

## 14. Definition of done for a feature

1. Every *Done when* item in its tasks is true.
2. The server, client and plugin checks pass (README "Checks"), and the OpenAPI drift check is clean.
3. The wave's e2e spec passes locally (`cd e2e && npm run stack:up && npm test`).
4. The feature's spec in `docs/spec/` describes what the code does, and the WBS row is ✅ (or 🚧 with what is missing).
5. Every new assumption is in the WBS "Assumptions & blockers".
6. Nothing is committed (CLAUDE.md).

# Glossary

**Status:** Draft · **Updated:** 2026-11-01

Mirrors the enums in `server/app/**/typing/enums`; change both together. Project roles and capabilities live in [server/app/shared/permissions](../../server/app/shared/permissions), and live event types in [live_event_type.py](../../server/app/shared/events/live_event_type.py). The UI words come from [client/src/lib/i18n/locales/en](../../client/src/lib/i18n/locales/en).

## People and access

| Term | Meaning | Code values |
| --- | --- | --- |
| **Workspace** | The one Tessio installation for the company. Not multi-tenant. | |
| **Workspace role** | A person's role across the workspace. The Owner and Workspace admins manage users, projects and the Jira connection. | `WorkspaceRole`: `owner`, `admin`, `member` |
| **Project role** | A person's one role inside one project. A workspace admin acts as `admin` in every project when signed in. | `ProjectRole`: `admin`, `pm`, `ba`, `qc`, `dev`, `viewer` |
| **Capability** | One permission a role grants, such as `test_case.edit`. Every API and MCP call checks one. See the [matrix](../spec/README.md#role--capability-matrix). | `Capability` (36 values), `WorkspaceCapability` (7 values) |
| **User status** | Where a person's account stands. Deactivated users keep their history but cannot sign in. | `UserStatus`: `invited`, `active`, `deactivated` |
| **Sign-in step** | What a session still needs after the password. | `SignInStep`: `two_factor_setup_required`, `two_factor_required`, `signed_in` |
| **Half session** | A session after the password and before the second factor, valid 10 minutes. | |
| **Recovery code** | One of 10 single-use codes that replace the authenticator app once. | |
| **API token** | A personal token for Claude, for one project, shown once, 90 days at most. It never does more than its owner's current role. | prefix `tsio_`; `ApiTokenStatus`: `active`, `expired`, `revoked` |
| **Archived project** | A project kept read-only: everything can be read, nothing changed. | `PROJECT_ARCHIVED` |
| **Audit event** | A record of who read a secret value, when, and through which token or run. | `AuditAction`: `secret.reveal`, `secret.resolve` |

## Stories and acceptance criteria

| Term | Meaning | Code values |
| --- | --- | --- |
| **Sprint** | A Jira sprint of the project's board, copied read-only. | `SprintState`: `active`, `future`, `closed` |
| **Story** | A Jira user story, copied read-only (title, description, Jira status). Tessio owns only its test status. | Jira key, for example `SHOP-12` |
| **Acceptance criterion (AC)** | One item of the AC list in the story's Jira description, numbered by position. A removed AC is kept for history. | code `AC1`, `AC2`…; `CriteriaSource`: `marked_list`, `first_list`, `none` |
| **Test status** | Tessio's testing state of a story. | `TestStatus`: `not_started`, `ready_for_test`, `in_test`, `passed`, `failed` |
| **Ready for test** | Dev's signal that the feature is done. It does not gate runs. | `ready_for_test` |
| **Sign-off** | QC marking a story Passed or Failed. Passed is refused while a failure is active or a run is running. | `story.sign_off`, `STORY_SIGN_OFF_BLOCKED` |
| **Sync** | Copying sprints, stories and AC from Jira, only when someone presses Sync from Jira. | `ProjectSyncStatus`: `never`, `queued`, `running`, `succeeded`, `failed` |
| **Traceability** | The AC × test case matrix of a story, with each AC's status. | |
| **AC status / AC impact** | An AC's status from its linked cases' latest results; in a run report, the same status for that run. | `CriterionStatus`: `uncovered`, `not_run`, `passed`, `failed`, `blocked` |

## Test design

| Term | Meaning | Code values |
| --- | --- | --- |
| **Test case** | Step-by-step check of one story, covering some of its AC. | code `TC-<n>`, numbered per project |
| **Priority** | How important a case is. | `TestCasePriority`: `critical`, `high`, `medium`, `low` |
| **Step** | One action and its expected result, numbered from 1. A case has at most 100. | |
| **Version** | A saved state of a case. Every save adds one; a run fixes the version it executes. | version number from 1 |
| **Review status** | Where a case is in review. Only `ready` cases run. | `TestCaseStatus`: `draft`, `in_review`, `ready`, `deprecated` |
| **Needs-review flag** | Set on linked cases when their AC change or disappear in Jira; cleared by Mark reviewed or Mark ready. | |
| **Test case file** | A file attached to a case under a key, versioned. Steps use it as `{{file.key}}`. | `StoredFileKind`: `test_file` |
| **Case import** | Creating Draft cases from an `.xlsx` (tab = Jira key) or `.csv` file. | `CaseImportFormat`: `xlsx`, `csv` |
| **Claude import / draft** | Claude, in Claude Code, turning any test plan file or a story's AC into cases, checked by Tessio and created as Draft only after the user confirms. | `/tessio:import-cases`, `/tessio:draft-cases`; MCP `check_draft_cases`, `create_draft_cases` |
| **Execution log** | Claude's visible notes and actions during one run, uploaded after `finish_run` and shown on the run's Log tab, grouped into setup, cases and wrap-up. | `run_log_entries`; `RunLogPhase`: `setup`, `case`, `wrap_up`; `RunLogEntryKind`: `note`, `action` |
| **Label** | A project-wide tag on test cases, such as `smoke`, with a colour from a fixed palette. Not versioned; filters the case list. | `LabelColor`: `gray`, `red`, `orange`, `yellow`, `green`, `teal`, `blue`, `violet` |
| **Flaky case** | A case whose last 10 passed or failed results on its current version flip between pass and fail 3 or more times. | `flakyScore`, `flakySince`; job `test_cases.recompute_flaky` |
| **Disagreeing case** | A case whose latest manual and latest automated result on the current version differ and are at most 24 hours apart. | `disagreedAt` |
| **Quarantine** | A flag (Admin, QC) for a case you don't trust yet, with a history. It changes nothing in runs until script runs (W13), and ends after 10 passes in a row. | `test_case.quarantine`; `QuarantineEventKind`: `quarantined`, `released`, `auto_released` |
| **Review comment** | A reviewer's note on a case version or one of its steps. An open comment blocks Mark ready. | `REVIEW_COMMENTS_OPEN` |
| **Separate reviewer** | Project setting: the person who saved the current version cannot mark the case Ready or reviewed. | `requireSeparateReviewer`, `REVIEWER_IS_AUTHOR` |
| **Suite** | A regression suite: a named, ordered, fixed list of cases from any stories of a project, filled one by one or once by filter (labels, priority, story, sprint). Can be archived. | `test_suites`, `suite.edit`; `SUITE_NAME_ALREADY_USED`, `SUITE_ARCHIVED` |
| **Plan** | A test plan: suites and stories for a release, with each case's latest result since the plan opened, its blockers and a sign-off refused while a failure on its cases is active. | `PlanStatus`: `open`, `signed_off`, `closed`; `plan.edit`, `plan.sign_off`; `PLAN_FAILURES_ACTIVE` |
| **Shared step** | Steps such as logging in, written once under a key and inserted into many cases. Versioned; a case always runs its latest version. | key such as `login_as_admin`; `shared_steps`, `shared_step_versions` |
| **Parameter / data row** | A named value a data-driven case uses as `{{param.name}}`, and one set of values for its parameters (at most 20 of each). Never a literal secret. | `parameters`, `dataRows`; `SECRET_IN_DATA_ROW` |

## Test data and environments

| Term | Meaning | Code values |
| --- | --- | --- |
| **Environment** | Where tests run: a name, a base URL and an optional health-check URL. Can be archived. | |
| **Default environment** | The environment a run uses when none is chosen. | project setting |
| **Test data item** | A key and value for the whole project or one environment. Steps use it as `{{data.key}}`. | `DataItemKind`: `variable`, `endpoint`, `secret` |
| **Effective data** | The values that apply in one environment: its own items plus the project items it does not override. | |
| **Secret** | A test data item whose value is encrypted and never listed. | `secret` |
| **Reveal** | An Admin or QC showing a secret value in the UI for 30 seconds; audited. | `secret.reveal` |
| **Resolve** | Claude getting secret values for its own running run through `resolve_data`; audited. | `secret.resolve` |
| **Masking** | Replacing every secret value of the run's environment with `••••` in results, summaries and reports. | `••••` |
| **Data import** | Loading a `.env`, JSON or YAML file into test data, with secret-looking keys marked `secret`. | `ImportFormat`: `dotenv`, `json`, `yaml` |

## Readiness review

| Term | Meaning | Code values |
| --- | --- | --- |
| **Gap** | A question about a story, an AC or a case that must be answered before a run. | `GapStatus`: `open`, `resolved` |
| **Gap type** | What is missing. | `GapType`: `missing_ac`, `unclear_goal`, `missing_step`, `missing_test_data`, `other` |
| **Gap target** | What the gap is about. | `GapTargetType`: `story`, `criterion`, `test_case` |
| **Severity** | How much the gap matters. | `GapSeverity`: `high`, `medium`, `low` |
| **Data scope** | For a data gap, whether the data belongs to the project or one environment. | `GapDataScope`: `project`, `environment` |
| **Routing** | Choosing who answers: AC and goal gaps → BA; steps → QC; data → QC, or Dev for environment data; other → Admin. One member gets it; several share a role queue; none falls back to Admin. | `assignee_role` |
| **Readiness** | A story is ready to run when it has no open gap. | `OPEN_GAPS_BLOCK_RUN` |
| **Gap inbox** | "My gaps": open gaps assigned to me or my role, across my projects. | `/gaps` |
| **Answer gaps with Claude** | Answering the gaps waiting for you in Claude Code: Claude suggests sourced answers, you confirm, and the answer shows "via Claude". | `/tessio:answer-gaps`; MCP `get_my_gaps`, `answer_gap`, `reassign_gap`; `isAnsweredViaClaude` |

## Execution

| Term | Meaning | Code values |
| --- | --- | --- |
| **Run** | One execution of a story's Ready cases on one environment. One running run per story. | `RunStatus`: `running`, `passed`, `failed`, `aborted` |
| **Suite run** | A run of a suite's Ready cases that don't need review; the others are skipped and listed. Blocked by open gaps on any of its stories, one running run per suite, and it never changes a story's test status. | `runs.test_suite_id`; `SkipReason`: `not_ready`, `needs_review`; `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY` |
| **Run snapshot** | The steps a run case runs, fixed at run start with shared steps expanded and renumbered. | `run_cases.steps` |
| **Iteration** | One data row of a data-driven case run as its own result, numbered from 0. The case's result in a run is its worst iteration. | `case_results.iteration`; `ITERATION_OUT_OF_RANGE` |
| **Executor** | Who runs the cases. | `RunExecutor`: `claude`, `manual` (the database also accepts `script` and `ci`, reserved for W12 and W11) |
| **Re-run / parent run** | A run of only the failed and blocked cases of a finished run, linked to it as its parent. | `parent_run_id` |
| **Case result** | The outcome of one case in a run, with its version and duration. Written once. | `ResultStatus`: `passed`, `failed`, `blocked`, `skipped` |
| **Step result** | The outcome of one step: status, actual result, error and screenshot or evidence. Unreported steps are `skipped`. | `ResultStatus` |
| **Abort reason** | Why a run ended `aborted`. | `RunAbortReason`: `no_results`, `inactive` |
| **Run report** | Built when a run finishes: counts, failed cases, AC impact, missing screenshots and the summary. | |
| **Latest result** | A case's newest result in any run; a `skipped` result counts only when there is no other. A run that does not report a case leaves it unchanged. | |
| **Screenshot** | The image Claude saves for each step; uploaded by the hook and kept forever. | `StoredFileKind`: `screenshot` |
| **Evidence** | An optional file a tester attaches to a manual step. | `StoredFileKind`: `evidence` |
| **Stored file** | Any file Tessio keeps in object storage, uploaded through a signed link. | `StoredFileKind`: `screenshot`, `test_file`, `evidence`, `import`, `avatar`, `report`; `StoredFileStatus`: `pending`, `uploaded`, `missing` |

## Failures

| Term | Meaning | Code values |
| --- | --- | --- |
| **Failure** | One failing test case, from its first failed result until QC verifies the fix. At most one active failure per case. | `FailureStatus`: `open`, `fixed`, `verified`, `reopened` |
| **Suspected cause** | Why a failed or blocked case most likely failed, set by Claude or the tester and correctable on the failure. | `SuspectedCause`: `app_bug`, `test_data`, `environment`, `test_case`, `unknown` |
| **Diagnosis** | What was seen at the failing step: page URL, console errors and failed requests. | `StepDiagnosis` |
| **Active failure** | A failure that is `open`, `fixed` or `reopened`. | |
| **Failure event** | One line of a failure's timeline. | `FailureEventKind`: `opened`, `failed_again`, `status_changed`, `assigned`, `unassigned` |
| **Assignee** | The project member who owns a failure or gap. New failures start unassigned. | `ASSIGNEE_NOT_ACTIVE_MEMBER` |

## Notifications and live updates

| Term | Meaning | Code values |
| --- | --- | --- |
| **Notification** | An in-app message to one person. | `NotificationKind`: `gap_assigned`, `failure_assigned`, `run_finished`, `suite_run_finished` |
| **Live event** | A message on the `/api/events` stream that makes open screens refetch. | `LiveEventType`: `run.started`, `run.case_recorded`, `run.finished`, `jira.sync_started`, `jira.sync_finished`, `jira.sync_failed`, `notification.created`, `project.members_changed`, `gap.changed`, `failure.changed`, `test_case.changed`, `story.changed` |
| **My work** | The dashboard list of items waiting for the caller's role. | `MyWorkSection`: `cases_to_write`, `failures_to_fix`, `gaps_to_answer` |

## Claude

| Term | Meaning | Code values |
| --- | --- | --- |
| **MCP** | The Model Context Protocol server at `/mcp` that Claude Code calls with an API token. | tools: `get_story_context`, `get_suite_context`, `get_open_gaps`, `raise_gaps`, `get_my_gaps`, `answer_gap`, `reassign_gap`, `set_test_data`, `start_run`, `resolve_data`, `get_test_file`, `record_case_result`, `finish_run`, `get_failed_cases` |
| **Plugin** | The Tessio Claude Code plugin: the MCP server entry, the upload hooks and seven skills. | skills: `run-story-tests`, `run-suite`, `rerun-failed`, `review-readiness`, `answer-gaps`, `import-cases`, `draft-cases` |
| **Upload hook** | A `PostToolUse` hook that runs after each `record_case_result` and uploads the step screenshots, retrying failed ones later. | [claude/hooks/upload_screenshots.py](../../claude/hooks/upload_screenshots.py) |
| **Health check** | Claude calling the environment's health-check URL before the first case; a down environment ends the run with no results. | |

# User flows and state diagrams

**Status:** Draft · **Updated:** 2026-11-01

WBS 2.5. The flows people follow through Tessio as the code works today, and the state machines behind them. Each flow has a diagram and a step table that links to the story in the [functional specs](../spec/README.md). Routes are client routes; `/api/…` paths and MCP tools are server calls.

## 1. Onboarding: invite, password, two-factor

A workspace admin invites a person; the person sets a password and sets up two-factor before seeing any project. The branches show a later sign-in and a forgotten password.

```mermaid
flowchart TD
  invite["Workspace admin: Invite user on /users"] --> mail["Invite email, link valid 7 days"]
  mail --> accept["/invite/[token]: set password"]
  accept -->|"invalid or expired link"| askNew["Ask the admin to resend the invite"]
  accept -->|"password accepted"| half1["Half session, nextStep two_factor_setup_required"]
  half1 --> setup["/two-factor/setup: scan QR code or enter the key"]
  setup --> confirm["Confirm with the first code"]
  confirm -->|"wrong code"| setup
  confirm -->|"right code"| codes["Save 10 recovery codes"]
  codes --> home["/ opens the first project, or /projects when not in a project yet"]

  signIn["/sign-in: email and password"] -->|"wrong, 5 times: locked 15 min"| signIn
  signIn -->|"password accepted"| half2["Half session, 10 min"]
  half2 -->|"two-factor set up"| twoFactor["/two-factor: code from the app"]
  half2 -->|"two-factor not set up or reset"| setup
  twoFactor -->|"Use a recovery code instead"| recovery["Recovery code, one use"]
  twoFactor -->|"code accepted"| home
  recovery -->|"code accepted"| home

  signIn -->|"Forgot password?"| forgot["/forgot-password: email"]
  forgot --> resetMail["Reset email, link valid 30 min"]
  resetMail --> reset["/reset-password/[token]: new password"]
  reset -->|"all sessions signed out"| signIn
```

| Step | Who | Screen route or MCP tool | Result | Spec story id |
| --- | --- | --- | --- | --- |
| 1 | Workspace admin | `/users` → Invite user (`POST /api/users`) | User `invited`, invite email sent | [USER-2](../spec/user-management.md#user-2-invite-a-user-wbs-33b1) |
| 2 | Invited person | `/invite/[token]` (`POST /api/auth/invites/{token}`) | User `active`, half session, `two_factor_setup_required` | [AUTH-3](../spec/authentication-and-account.md#auth-3-accept-an-invite-wbs-322) |
| 3 | Invited person | `/two-factor/setup` (`POST /api/auth/two-factor/setup`) | QR code and manual key | [AUTH-4](../spec/authentication-and-account.md#auth-4-set-up-two-factor-wbs-323) |
| 4 | Invited person | Confirm (`POST /api/auth/two-factor/confirm`) | Full session, 10 recovery codes shown once | [AUTH-4](../spec/authentication-and-account.md#auth-4-set-up-two-factor-wbs-323) |
| 5 | Invited person | Continue → `/` | First project's dashboard, or `/projects` | [SHELL-3](../spec/app-shell.md#shell-3-home-route-wbs-312) |
| 6 | User | `/sign-in` (`POST /api/auth/sign-in`) | Half session; `two_factor_required` or `two_factor_setup_required` | [AUTH-1](../spec/authentication-and-account.md#auth-1-sign-in-with-email-and-password-wbs-321) |
| 7 | User | `/two-factor` (`POST /api/auth/two-factor`) | Full session with a TOTP or recovery code | [AUTH-2](../spec/authentication-and-account.md#auth-2-two-factor-step-at-sign-in-wbs-321-323) |
| 8 | User | `/forgot-password` → email → `/reset-password/[token]` | New password; every session signed out | [AUTH-5](../spec/authentication-and-account.md#auth-5-forgot-and-reset-password-wbs-324) |

## 2. The sprint testing loop

From the Jira sync to QC sign-off. Every open gap blocks the run; a failure stays active until QC verifies it, and the story cannot be signed off as Passed while a failure is active.

```mermaid
flowchart TD
  sync["PM or BA: Sync from Jira"] --> stories["Sprints, stories and AC copied read-only"]
  stories --> write["QC writes test cases and links AC"]
  write --> review["Review: draft to in_review to ready"]
  review --> devReady["Dev: Mark ready for test"]
  devReady --> readiness["Claude: review-readiness, raise_gaps"]
  readiness --> route["Gaps routed: AC and goal to BA, steps to QC, data to QC or Dev, other to Admin"]
  route --> answer["Owners answer; answering resolves the gap"]
  answer --> gapCheck{"Any gap still open?"}
  gapCheck -->|"yes: OPEN_GAPS_BLOCK_RUN"| answer
  gapCheck -->|"no"| run["Run: Claude through MCP, or a manual run"]
  run --> finish["Finish run: status and report"]
  finish --> outcome{"Any failed case?"}
  outcome -->|"no"| signOff["QC: Mark passed"]
  outcome -->|"yes"| opened["Failure opens, unassigned"]
  opened --> assign["QC or Dev assigns it to a Dev"]
  assign --> fixed["Dev fixes the code, Mark fixed"]
  fixed --> rerun["Re-run failed only: child run of the failed and blocked cases"]
  rerun --> rerunOutcome{"Case passes?"}
  rerunOutcome -->|"fails again: reopened"| assign
  rerunOutcome -->|"passes"| verify["QC: Verify"]
  verify --> signOff
  signOff --> passed["Story test status: passed"]
```

| Step | Who | Screen route or MCP tool | Result | Spec story id |
| --- | --- | --- | --- | --- |
| 1 | PM or BA | `/projects/[projectKey]/stories` → Sync from Jira | `jira.sync_project` job; sprints, stories and AC updated | [STORY-4](../spec/sprints-and-stories.md#story-4-sync-from-jira-wbs-354), [STORY-5](../spec/sprints-and-stories.md#story-5-ac-parsed-from-the-description-wbs-353-374) |
| 2 | QC | `/projects/[projectKey]/test-cases/new` | Case `TC-<n>` in `draft`, linked to AC | [CASE-2](../spec/test-cases.md#case-2-write-a-test-case-wbs-362), [CASE-3](../spec/test-cases.md#case-3-link-cases-to-ac-wbs-363) |
| 3 | QC | Traceability tab of `/projects/[projectKey]/stories/[jiraKey]` | Uncovered AC warning until every AC has a case | [TRACE-2](../spec/traceability.md#trace-2-uncovered-ac-warning-wbs-372) |
| 4 | QC | `/projects/[projectKey]/test-cases/[caseCode]` → Submit for review → Mark ready | Case `ready` | [CASE-6](../spec/test-cases.md#case-6-review-workflow-wbs-365) |
| 5 | Dev | `/projects/[projectKey]/stories/[jiraKey]` → Mark ready for test | Story `ready_for_test` | [STORY-7](../spec/sprints-and-stories.md#story-7-dev-marks-a-story-ready-for-test-wbs-356) |
| 6 | Claude (started by a Dev) | MCP `get_story_context`, `get_open_gaps`, `raise_gaps` | Gaps `open`, routed, `gap_assigned` sent | [GAP-2](../spec/readiness-review.md#gap-2-raise-gaps-wbs-381-382), [GAP-3](../spec/readiness-review.md#gap-3-automatic-routing-wbs-382) |
| 7 | BA, QC, Dev, Admin | `/gaps` or the story's Gaps tab → Answer | Gap `resolved`; QC updates cases, BA updates AC in Jira and syncs | [GAP-4](../spec/readiness-review.md#gap-4-answer-and-resolve-wbs-383), [GAP-7](../spec/readiness-review.md#gap-7-gap-inbox-wbs-385) |
| 8 | Claude or QC | MCP `start_run`, or `/projects/[projectKey]/runs/new` | Run `running`, story `in_test` | [RUN-2](../spec/runs.md#run-2-start-a-claude-run-wbs-3103), [RUN-8](../spec/runs.md#run-8-manual-run-wbs-3104) |
| 9 | Claude or QC | MCP `finish_run`, or Finish run | Run `passed`, `failed` or `aborted`; report; `run_finished` | [RUN-6](../spec/runs.md#run-6-finish-a-run-and-build-the-report-wbs-3106) |
| 10 | Server | (on each `failed` result) | Failure `open`, unassigned | [FAIL-1](../spec/failures.md#fail-1-a-failed-result-opens-a-failure-wbs-3113) |
| 11 | QC or Dev | `/projects/[projectKey]/failures/[failureId]` → Assign | Assignee set, `failure_assigned` sent | [FAIL-5](../spec/failures.md#fail-5-assign-a-failure-wbs-3115) |
| 12 | Dev | Same page → Mark fixed | Failure `fixed` | [FAIL-4](../spec/failures.md#fail-4-mark-fixed-verify-reopen-wbs-3113) |
| 13 | Dev with Claude, or QC | MCP `get_failed_cases` + `start_run(parent_run_id)`, or Re-run failed | Child run of the failed and blocked cases still `ready` | [RUN-9](../spec/runs.md#run-9-re-run-failed-only-wbs-3105) |
| 14 | Server | (a `failed` result on a `fixed` failure) | Failure `reopened` automatically | [FAIL-1](../spec/failures.md#fail-1-a-failed-result-opens-a-failure-wbs-3113) |
| 15 | QC | Failure page → Verify | Failure `verified` | [FAIL-4](../spec/failures.md#fail-4-mark-fixed-verify-reopen-wbs-3113) |
| 16 | QC | Story page → Mark passed | Story `passed`; refused while a failure is active or a run is running | [STORY-6](../spec/sprints-and-stories.md#story-6-qc-sign-off-wbs-355) |

## 3. A Claude run

What happens when a Dev asks Claude Code to test a story with the `run-story-tests` skill. Claude drives the browser with Claude in Chrome; Tessio only stores what Claude sends. The screenshots go from the disk to storage through the plugin's hook, so the model never spends tokens on them.

```mermaid
sequenceDiagram
  actor Dev
  participant Claude as Claude Code
  participant Tessio as Tessio MCP
  participant Chrome as Claude in Chrome
  participant Env as Environment under test
  participant Hook as Upload hook
  participant Storage as Object storage

  Dev->>Claude: /tessio:run-story-tests SHOP-12
  Claude->>Tessio: get_story_context(story_key)
  Tessio-->>Claude: story, AC, Ready cases, data references, files, environments
  Claude->>Tessio: get_open_gaps(story_key)
  Tessio-->>Claude: open gaps and count
  alt gaps are open
    Claude-->>Dev: list the gaps and stop
  end
  Claude->>Tessio: start_run(story_key, environment)
  Tessio-->>Claude: run_id, base_url, health_check_url, cases with fixed versions
  Claude->>Env: curl health_check_url
  alt environment is down
    Claude->>Tessio: finish_run(run_id) with an Environment down summary
    Tessio-->>Claude: status aborted
  end
  loop each case in order
    Claude->>Tessio: resolve_data(run_id, keys) when a step needs a secret
    Tessio-->>Claude: values, audited as secret.resolve
    Claude->>Tessio: get_test_file(run_id, key) when a step needs a file
    Tessio-->>Claude: file name and 5-minute link
    Claude->>Chrome: run each step, save one full-size screenshot per step
    Claude->>Tessio: record_case_result(run_id, case_id, status, duration_ms, steps)
    Tessio-->>Claude: case_result_id
    Hook->>Tessio: POST /api/runs/RUN/case-results/RESULT/screenshot-upload
    Tessio-->>Hook: signed POST, valid 1 hour
    Hook->>Storage: upload one file per step
  end
  Claude->>Tessio: finish_run(run_id, summary)
  Tessio-->>Claude: status and missing_screenshots
  Claude-->>Dev: run status, missing screenshots
  Dev->>Claude: /tessio:rerun-failed RUN
  Claude->>Tessio: get_failed_cases(run_id)
  Tessio-->>Claude: story_key, environment, failed and blocked cases
  Claude->>Tessio: start_run(story_key, environment, parent_run_id)
```

| Step | Who | Screen route or MCP tool | Result | Spec story id |
| --- | --- | --- | --- | --- |
| 1 | Claude | `get_story_context(story_key)` | Story, active AC, Ready cases, data with secrets as `{{data.key}}`, files, environments | [RUN-11](../spec/runs.md#run-11-story-context-and-test-files-for-claude-wbs-3103) |
| 2 | Claude | `get_open_gaps(story_key)` | Stops when any gap is open | [GAP-6](../spec/readiness-review.md#gap-6-open-gaps-block-runs-wbs-384) |
| 3 | Claude | `start_run(story_key, environment?, case_ids?)` | Run `running`, story `in_test`, `run.started` | [RUN-2](../spec/runs.md#run-2-start-a-claude-run-wbs-3103) |
| 4 | Claude | `curl` on the health-check URL | Down: `finish_run` with no results, run `aborted` | [RUN-3](../spec/runs.md#run-3-health-check-before-the-run-wbs-3103) |
| 5 | Claude | `resolve_data(run_id, keys)` | Secret values for this run, each audited | [DATA-5](../spec/environments-and-test-data.md#data-5-secrets-during-a-run-wbs-394) |
| 6 | Claude | `get_test_file(run_id, key, case_id?)` | 5-minute download link; file version recorded | [RUN-11](../spec/runs.md#run-11-story-context-and-test-files-for-claude-wbs-3103) |
| 7 | Claude | `record_case_result(...)` once per case | Case and step results, masked; `run.case_recorded`; a failure if `failed` | [RUN-4](../spec/runs.md#run-4-record-a-case-result-wbs-3102-3103) |
| 8 | Upload hook | `POST /api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload` | One file per step in storage; failed uploads retried later | [RUN-5](../spec/runs.md#run-5-screenshot-upload-by-the-hook-wbs-3102) |
| 9 | Claude | `finish_run(run_id, summary)` | Status from the results, report, missing screenshots, `run_finished` | [RUN-6](../spec/runs.md#run-6-finish-a-run-and-build-the-report-wbs-3106) |
| 10 | Claude | `get_failed_cases(run_id)`, then `start_run(..., parent_run_id)` | Child run of the failed and blocked cases | [RUN-9](../spec/runs.md#run-9-re-run-failed-only-wbs-3105) |

## 4. A manual run

A QC runs the Ready cases by hand and records each step in the browser.

```mermaid
flowchart TD
  newRun["/projects/[projectKey]/runs/new"] --> pick["Pick story, environment and Ready cases"]
  pick --> start["Start manual run"]
  start -->|"open gaps, no Ready case, or a run already running"| refused["Refused with the error code"]
  start -->|"accepted"| record["/projects/[projectKey]/runs/[runId]/record"]
  record --> step["For each step: status, actual result, what went wrong, optional evidence"]
  step --> save["Save result: suggested case status, one save per case"]
  save --> more{"More cases?"}
  more -->|"yes"| step
  more -->|"no, or stop early"| finishRun["Finish run, optional summary"]
  finishRun --> detail["/projects/[projectKey]/runs/[runId]: status and report"]
```

| Step | Who | Screen route or MCP tool | Result | Spec story id |
| --- | --- | --- | --- | --- |
| 1 | QC or Admin | `/projects/[projectKey]/runs/new` (`POST /api/projects/{project_key}/runs`) | Manual run `running`, story `in_test` | [RUN-8](../spec/runs.md#run-8-manual-run-wbs-3104) |
| 2 | Same person | `/projects/[projectKey]/runs/[runId]/record`, evidence via `POST …/uploads` kind `evidence` | Evidence uploaded | [RUN-8](../spec/runs.md#run-8-manual-run-wbs-3104) |
| 3 | Same person | Save result (`PUT …/runs/{run_id}/cases/{test_case_id}`) | Case result, unmarked steps `skipped`, a failure if `failed` | [RUN-8](../spec/runs.md#run-8-manual-run-wbs-3104), [FAIL-1](../spec/failures.md#fail-1-a-failed-result-opens-a-failure-wbs-3113) |
| 4 | Same person | Finish run (`POST …/runs/{run_id}/finish`) | Run status and report; `run_finished` | [RUN-8](../spec/runs.md#run-8-manual-run-wbs-3104), [RUN-6](../spec/runs.md#run-6-finish-a-run-and-build-the-report-wbs-3106) |
| 5 | Anyone | `/projects/[projectKey]/runs/[runId]` | Results and Report tabs | [RUN-7](../spec/runs.md#run-7-run-detail-and-live-progress-wbs-3102-3103) |

## 5. Connect Claude

A developer creates a personal token and installs the Tessio plugin with it, once per project.

```mermaid
flowchart TD
  page["/connect-claude"] --> create["Create token: name, project, lifetime 7 to 90 days"]
  create -->|"10 active tokens already"| limit["TOKEN_LIMIT_REACHED: revoke one first"]
  create -->|"created"| shown["Token shown once inside the install command"]
  shown --> terminal["Run claude plugin install tessio with tessio_url and tessio_token"]
  terminal --> restart["Restart Claude Code or run /reload-plugins"]
  restart --> firstCall["First MCP call, for example get_story_context"]
  firstCall -->|"token valid, user active, still a member"| works["Tools answer in the token's project"]
  firstCall -->|"expired, revoked or not a member"| invalid["INVALID_API_TOKEN"]
```

| Step | Who | Screen route or MCP tool | Result | Spec story id |
| --- | --- | --- | --- | --- |
| 1 | Dev (any role) | `/connect-claude` → Create token (`POST /api/me/api-tokens`) | `tsio_…` token for one project, stored as a hash | [AUTH-10](../spec/authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326) |
| 2 | Dev | Terminal: `claude plugin install tessio --marketplace … --config tessio_url=… --config tessio_token=…` | Plugin with the MCP server, hook and skills | [AUTH-10](../spec/authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326) |
| 3 | Dev | Claude Code: any Tessio tool, for example `get_story_context` | Answer in the token's project, with the owner's current role | [RUN-11](../spec/runs.md#run-11-story-context-and-test-files-for-claude-wbs-3103) |
| 4 | Dev | `/connect-claude` → Revoke | Token stops working at once | [AUTH-11](../spec/authentication-and-account.md#auth-11-list-and-revoke-tokens-wbs-326) |

## State diagrams

Each diagram is built from the transition constant named under it.

### Story test status

`TEST_STATUS_TRANSITIONS` in [test_status.py](../../server/app/modules/stories/typing/constants/test_status.py). Spec: [STORY-6](../spec/sprints-and-stories.md#story-6-qc-sign-off-wbs-355), [STORY-7](../spec/sprints-and-stories.md#story-7-dev-marks-a-story-ready-for-test-wbs-356).

```mermaid
stateDiagram-v2
  [*] --> not_started: first sync
  not_started --> ready_for_test: Dev or Admin, Mark ready for test
  ready_for_test --> not_started: Dev or Admin, Move back to not started
  in_test --> passed: QC or Admin, Mark passed, no active failure or running run
  in_test --> failed: QC or Admin, Mark failed
  passed --> failed: QC or Admin, Mark failed
  failed --> passed: QC or Admin, Mark passed, no active failure or running run
  failed --> ready_for_test: Dev or Admin, after a fix
  not_started --> in_test: a run starts
  ready_for_test --> in_test: a run starts
  passed --> in_test: a run starts
  failed --> in_test: a run starts
```

### Test case status

`TEST_CASE_STATUS_TRANSITIONS` in [test_case_status.py](../../server/app/modules/test_cases/typing/constants/test_case_status.py). Spec: [CASE-6](../spec/test-cases.md#case-6-review-workflow-wbs-365).

```mermaid
stateDiagram-v2
  [*] --> draft: created or imported
  draft --> in_review: Submit for review
  draft --> deprecated: Deprecate
  in_review --> draft: Back to draft
  in_review --> ready: Mark ready, needs steps and known references
  in_review --> deprecated: Deprecate
  ready --> in_review: Back to review
  ready --> draft: Back to draft
  ready --> deprecated: Deprecate
  deprecated --> draft: Restore to draft
```

### Run status

`decide_run_status` and `resolve_finished_status` in [run_status.py](../../server/app/modules/runs/utils/run_status.py); the stale abort in [abort_stale_runs.py](../../server/app/modules/runs/usecases/abort_stale_runs.py). Spec: [RUN-6](../spec/runs.md#run-6-finish-a-run-and-build-the-report-wbs-3106), [RUN-10](../spec/runs.md#run-10-aborted-runs-wbs-3108).

```mermaid
stateDiagram-v2
  [*] --> running: start_run, manual run or re-run
  running --> passed: finish, every result passed or skipped
  running --> failed: finish, any result failed or blocked
  running --> aborted: finish with no results, reason no_results
  running --> aborted: no activity for 4 hours, reason inactive
  passed --> [*]
  failed --> [*]
  aborted --> [*]
```

### Failure status

`MANUAL_STATUS_TRANSITIONS` in [failure.py](../../server/app/modules/failures/typing/constants/failure.py) and the automatic moves in [apply_case_result.py](../../server/app/modules/failures/usecases/apply_case_result.py). Spec: [FAIL-1](../spec/failures.md#fail-1-a-failed-result-opens-a-failure-wbs-3113), [FAIL-4](../spec/failures.md#fail-4-mark-fixed-verify-reopen-wbs-3113).

```mermaid
stateDiagram-v2
  [*] --> open: a failed result, no active failure
  open --> fixed: Dev or Admin, Mark fixed
  reopened --> fixed: Dev or Admin, Mark fixed
  fixed --> verified: QC or Admin, Verify
  fixed --> reopened: QC or Admin, Reopen
  fixed --> reopened: a failed result, automatic
  verified --> [*]
```

### Gap status

`GapStatus` with the answer and reopen use cases in [server/app/modules/gaps/usecases](../../server/app/modules/gaps/usecases). Spec: [GAP-4](../spec/readiness-review.md#gap-4-answer-and-resolve-wbs-383), [GAP-5](../spec/readiness-review.md#gap-5-reopen-and-reassign-wbs-383).

```mermaid
stateDiagram-v2
  [*] --> open: raised, routed to a person or a role queue
  open --> open: reassigned
  open --> resolved: answered
  resolved --> open: reopened by the raiser, QC or Admin
```

### Sync status

`ProjectSyncStatus` with [request_jira_sync.py](../../server/app/modules/stories/usecases/request_jira_sync.py) and [sync_jira_project.py](../../server/app/modules/stories/usecases/sync_jira_project.py). Spec: [STORY-4](../spec/sprints-and-stories.md#story-4-sync-from-jira-wbs-354).

```mermaid
stateDiagram-v2
  [*] --> never
  never --> queued: Sync from Jira
  queued --> running: worker picks the job
  running --> succeeded: stories stored
  running --> failed: Jira error or archived project
  succeeded --> queued: Sync from Jira
  failed --> queued: Sync from Jira
  queued --> queued: requested again after 15 minutes stuck
  running --> queued: requested again after 15 minutes stuck
```

### User status

`UserStatus` with the invite, accept, deactivate and reactivate use cases in [server/app/modules/auth/usecases](../../server/app/modules/auth/usecases). Spec: [USER-2](../spec/user-management.md#user-2-invite-a-user-wbs-33b1), [USER-4](../spec/user-management.md#user-4-deactivate-and-reactivate-wbs-33b1).

```mermaid
stateDiagram-v2
  [*] --> invited: Invite user
  invited --> active: invite accepted, password set
  invited --> deactivated: Deactivate
  active --> deactivated: Deactivate
  deactivated --> active: Reactivate, had a password
  deactivated --> invited: Reactivate, never accepted, new invite sent
```

## Differences from the specs and proposals

- WBS 2.5 ends onboarding at the dashboard. In code, after the recovery codes the user goes to `/`, which opens the last or first project, or `/projects` when the user is in no project yet.
- The Claude run calls `record_case_result` once per case, not a step-by-step `record_step_result` as in the [workflow proposal §6](../discussions/testing-workflow-proposal.md#6-claude-integration-mcp-server).

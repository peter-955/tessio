# Sprint workflow

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page follows one sprint from planning to sign-off, step by step. It is the loop from §3 of the [testing workflow proposal](../../discussions/testing-workflow-proposal.md), as the app works today. The diagrams are in [user flows](../../design/user-flows.md).

Routes use `{KEY}` for the project key and `{STORY-KEY}` for the Jira key of a story.

## The 12 steps

| # | Step | Who | Where in Tessio | What Claude does |
| --- | --- | --- | --- | --- |
| 1 | Plan the sprint | PM | Plan the sprint and its stories in Jira. Then **Sync from Jira** on **Sprints** (`/projects/{KEY}/sprints`). | Nothing |
| 2 | Define AC | BA | Write the AC in Jira under "Acceptance criteria". Then **Sync from Jira** on **Stories** (`/projects/{KEY}/stories`). | Nothing |
| 3 | Design tests | QC | **New test case** on `/projects/{KEY}/test-cases`, or **Import** a sheet. Add data on **Test data**. Move cases to *Ready* with **Submit for review** and **Mark ready**. | Nothing yet |
| 4 | Check coverage | QC, BA | The story **Traceability** tab, and **AC without a test case** on the **Dashboard**. | Nothing |
| 5 | Feature ready | Dev | **Mark ready for test** on `/projects/{KEY}/stories/{STORY-KEY}`. | Nothing |
| 6 | Readiness review | Dev starts, Claude reviews | Gaps appear on the story **Gaps** tab and in each owner's **My gaps** (`/gaps`). | `/tessio:review-readiness <STORY-KEY>` reads the story, AC, cases and data, and files the gaps. |
| 7 | Resolve gaps | BA, QC, Dev | **Answer** then **Answer and resolve**. QC fixes cases in Tessio; BA changes AC in Jira and syncs again. Every gap must be answered before a run can start. | Each owner can run `/tessio:answer-gaps` to answer their gaps with suggested, sourced answers. Can be asked to review again. |
| 8 | Run | Dev starts, Claude runs; or QC by hand | Claude run: follow it on `/projects/{KEY}/runs/{run-id}`. Manual run: **New manual run** on `/projects/{KEY}/runs/new`. The story moves to *In test*. | `/tessio:run-story-tests <STORY-KEY> [environment]` records each step with a screenshot. |
| 9 | Report | Claude, or the tester | The **Report** tab of the run: summary, failed cases, **Acceptance criteria impact**. | Writes the summary when it finishes the run. |
| 10 | Fix | Dev | **Failures** (`/projects/{KEY}/failures`), filter **Assigned to me**. Fix the code, then **Mark fixed**. | Nothing |
| 11 | Re-run failed | Dev; or QC by hand | **Re-run failed** on the run. For a manual run, **Start re-run**. | `/tessio:rerun-failed <run-id>` runs only the failed and blocked cases in a child run. |
| 12 | Verify and close | QC | **Verify** or **Reopen** each failure. Then **Mark passed** or **Mark failed** on the story. | Nothing |

## Where the loop stops

| Situation | What you see | What to do |
| --- | --- | --- |
| No runs yet | **No runs yet** on **Runs** and the dashboard | Start a run (step 8). |
| Open gaps | "Open gaps must be answered before a run can start." | Answer every gap (step 7). |
| No *Ready* cases | "There are no ready test cases to run." | Mark cases ready (step 3). |
| A run is already running | "A run is already in progress for this story." | Wait, or finish the run. A run with no activity for 4 hours is aborted. |
| Sign-off blocked | "Resolve active failures and wait for running runs before marking it passed." | Verify every failure and let runs finish (steps 11 and 12). |
| Token limit reached | "You have 10 active tokens. Revoke one to create another." | Revoke an old token on **Connect Claude**. |
| Archived project | **This project is archived** | Nothing can change. Ask a workspace admin to unarchive. |

## When a story fails

1. QC selects **Mark failed** on the story.
2. Dev fixes the code and marks the failures fixed.
3. Dev selects **Mark ready for test** again, and the loop restarts at step 6.

## Role pages

- [PM and BA](pm-ba.md): steps 1, 2, 4 and 7
- [QC](qc.md): steps 3, 4, 7, 8, 11 and 12
- [Dev](dev.md): steps 5 to 11
- [Project admin](project-admin.md): setting the project up before step 1

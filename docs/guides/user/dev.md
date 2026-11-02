# Dev guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for *Dev*. You tell QC when a feature is ready, run the tests with Claude Code, and fix what fails. Project Admins can do all of this too.

## Rules

| Rule | Detail |
| --- | --- |
| Open gaps block the start | Every gap on the story must be answered before a run can start. |
| One run per story | A story can have only one running run at a time. |
| Only *Ready* cases run | Draft, in-review and deprecated cases are left out. |
| Inactive runs end | A run with no activity for 4 hours is aborted. |
| Not reported | A case Claude did not report shows as *Not reported* and keeps its previous result. |
| Secrets | Claude reads secrets during a run. You cannot reveal them in the browser. |
| Tokens | At most 10 active tokens per person, each valid for up to 90 days. |

## Mark a story ready for test

1. Open the story (`/projects/{KEY}/stories/{STORY-KEY}`).
2. Select **Mark ready for test**. The story moves from *Not started* to *Ready for test*.
3. Marked it too early? Select **Move back to not started**.

When a run starts, the story moves to *In test*. After QC marks a story *Failed*, fix it and select **Mark ready for test** again.

> Screenshot to add: story-mark-ready.png: the story header with Mark ready for test and the test status.

## Connect Claude

You need a personal token for each project. Full setup, including installing the plugin: [Claude setup](../claude-setup.md).

1. Open **Connect Claude** from the user menu (`/connect-claude`).
2. Enter a name (for example "My laptop"), pick the project and how long the token lasts, then select **Create token**.
3. Copy the command shown and run it in your terminal. The token is shown only once.
4. Restart Claude Code, or run `/reload-plugins`.

Your tokens are listed under **Your tokens**. Select **Revoke** on a token you no longer use; Claude stops working with it at once.

If you already have 10 active tokens, the page says "You have 10 active tokens. Revoke one to create another." A Viewer's token can read but not record results.

> Screenshot to add: connect-claude.png: the token form and the one-time command after Create token.

## Claude Code skills

Run these in Claude Code with the Tessio plugin. Claude drives the browser with Claude in Chrome.

| Skill | What it does |
| --- | --- |
| `/tessio:review-readiness <STORY-KEY>` | Reads the story, its AC, cases and test data, and files the gaps it finds in Tessio. |
| `/tessio:answer-gaps [STORY-KEY \| mine]` | Works through the gaps waiting for you: suggests answers with their sources (including your product code, file and line, when you run Claude Code in the product's repository), and saves only what you confirm. A missing plain value is also saved to **Test data**. |
| `/tessio:run-story-tests <STORY-KEY> [environment] [case codes]` | Checks for open gaps (and if there are any, lists them by who must answer them and offers `/tessio:answer-gaps` for yours), starts the run, and records a result per case with a screenshot for every step. Without an environment, it uses the only one or asks. |
| `/tessio:run-suite <suite> [environment] [case codes]` | Runs a regression suite built by QC (name in quotes when it has spaces, or the suite id, as copied from the suite page). Lists the skipped cases, runs the rest in runs of at most 50 cases one after the other, and reports per story. Open gaps on any of the suite's stories block it, as for a story run. |
| `/tessio:rerun-failed <run-id>` | Makes a child run of the failed and blocked cases of a finished run, and runs them (a story run or a suite run). |

## Run the tests

1. Run `/tessio:review-readiness SHOP-12` (your story key).
2. Wait for the gaps to be answered. Each person sees theirs in **My gaps**, or answers them with `/tessio:answer-gaps`. A banner on the story **Gaps** tab says how many open gaps block runs.
3. Run `/tessio:run-story-tests SHOP-12 staging`.
4. Follow the run live at `/projects/{KEY}/runs/{run-id}`. Results appear case by case.

On a step, a screenshot can show **Uploading screenshot…** while it uploads, or **Screenshot missing** if it never arrived. When the run finishes, the **Report** tab has the summary, the failed cases and the **Acceptance criteria impact**.

If the start fails, Claude tells you why: open gaps, no *Ready* cases, or a run already running on the story.

> Screenshot to add: run-detail-live.png: a running Claude run with results arriving and step screenshots.

## Fix failures

1. Open **Failures** (`/projects/{KEY}/failures`) and filter by **Assigned to me**.
2. Open a failure. Read the failed step, the actual result, the error and the screenshot. **Open run** shows the whole run.
3. Fix the code.
4. Select **Mark fixed**.
5. Re-run with `/tessio:rerun-failed <run-id>`, or select **Re-run failed** on the run to copy the command.
6. QC then selects **Verify** or **Reopen**.

If the re-run fails again, the failure is reopened on its own. You can **Assign** a failure to someone else on the team.

> Screenshot to add: failures-assigned-to-me.png: the failures list filtered by Assigned to me.

## Gaps for Dev

*Missing test data* gaps about environment data come to you. Add the value in **Test data**, then select **Answer** and **Answer and resolve**. You can also raise and reassign gaps.

Or run `/tessio:answer-gaps` in Claude Code. For each gap Claude suggests answers with their sources, and when you run it in the product's repository it can cite the code (file and line). You pick with one key press, and after you confirm, Claude saves the answer and the plain value in **Test data**. Claude never asks for a secret: it gives you the **Test data** link, and a QC or Admin adds it.

## Environments and test data

You can manage environments and edit variables and endpoints on **Test data** (`/projects/{KEY}/test-data`). Secrets are saved and revealed by QC or Admin only. Claude still uses them in your runs.

## Next

- [Sprint workflow](sprint-workflow.md)
- [QC guide](qc.md)

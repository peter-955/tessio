# QC guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for *QC*: test cases, test data, manual runs, verifying fixes and sign-off. Project Admins can do all of this too.

## Rules

| Rule | Detail |
| --- | --- |
| Only *Ready* cases run | A case needs at least one step and no unknown references to become *Ready*. |
| Open gaps block runs | Any open gap on a story stops every run on it. |
| One run at a time | A story can have only one running run. |
| Secrets | Only Admin and QC can save and reveal secret values. |
| Sign-off | **Mark passed** is blocked while the story has an active failure (*Open*, *Fixed* or *Reopened*) or a running run. |
| Archived project | Everything is read-only. |

## Test cases

Open **Test cases** (`/projects/{KEY}/test-cases`). Filter by story, status, priority, AC, or **Needs review only**.

### Write a case

1. Select **New test case** (`/projects/{KEY}/test-cases/new`).
2. Pick the story. Enter the title, priority, business value and preconditions.
3. In **Covers acceptance criteria**, pick the AC this case checks.
4. Add steps with **Add step**. Each step has an **Action** and an **Expected result**.
5. Refer to test data as `{{data.key}}` and to test files as `{{file.key}}`. Type `{{data.` or `{{file.` to get suggestions.
6. Select **Create test case**. The case gets a code such as TC-12.

> Screenshot to add: test-case-editor.png: the case editor with AC picked, two steps and the reference suggestions open.

### Statuses

| From | Button | To |
| --- | --- | --- |
| *Draft* | **Submit for review** | *In review* |
| *In review* | **Mark ready** | *Ready* |
| *In review* | **Back to draft** | *Draft* |
| *Ready* | **Back to review** or **Back to draft** | *In review* or *Draft* |
| Any | **Deprecate** | *Deprecated*: left out of runs, cannot be edited |
| *Deprecated* | **Restore to draft** | *Draft* |

A *Ready* case stays *Ready* when you edit it, as long as it still has a step and no unknown references.

### Changes in Jira

When an AC changes or is removed in Jira, every case that covers it is flagged *Needs review*. Open the case, check the steps against the new AC, edit if needed, then select **Mark reviewed**.

### Versions and files

- Every save makes a new version. On the **History** tab, pick two versions and use **Compare versions** to see what changed. A run keeps the version it ran.
- On the **Files** tab, select **Add file** and give it a key, for example `invoice`. Use it in steps as `{{file.invoice}}`. Files can be up to 20 MB and must be an allowed file type.
- To replace a file, use **New version**. Older versions stay; **Versions** lists them.

## Import cases from a spreadsheet

1. On **Test cases**, select **Import**.
2. Drop an .xlsx file with one tab per story (the tab name is the Jira key), or a .csv file with a Story column. Up to 5 MB.
3. Check the preview. Rows with problems, such as "Story not found", are marked.
4. Choose the rows to keep and select **Import**.

Accepted column headers, in any case:

| Field | Headers |
| --- | --- |
| Story (needed in .csv) | story, story key, jira key |
| Title | title, test case, name |
| Priority | priority |
| Business value | business value |
| Preconditions | preconditions, precondition |
| Step action | step, steps, action |
| Expected result | expected, expected result, expected results |
| AC | covers ac, ac, acceptance criteria (for example "AC1, AC3") |

Imported cases start as *Draft*. The format is provisional until it has been tried on a real sheet of the team (WBS 3.6.7). The project must allow .xlsx and .csv files.

> Screenshot to add: test-case-import.png: the import preview with included rows and one Story not found row.

## Test data

Open **Test data** (`/projects/{KEY}/test-data`).

| Kind | Use | Who edits |
| --- | --- | --- |
| *Variable* | Plain values, such as a user name | Admin, QC, Dev |
| *Endpoint* | URLs, such as a health API | Admin, QC, Dev |
| *Secret* | Passwords and tokens. Hidden by default. | Admin, QC |

- The **All environments** column holds the value used everywhere. A value in an environment column overrides it for that environment only.
- **Reveal** shows a secret value. It is hidden again after 30 seconds. Every reveal is recorded.
- Claude uses secrets during a run. Dev can start those runs but cannot reveal secrets.

### Import a data file

1. Select **Import** on the **Data** tab.
2. Pick where to import (**All environments** or one environment), and drop a .env, JSON or YAML file of up to 1 MB.
3. Check the rows. Keys that look like passwords, tokens or API keys are marked *Secret*. Change the kind if needed.
4. Select **Import selected**.

The project must allow `text/plain` or `application/json`.

### Environments

On the **Environments** tab (`/projects/{KEY}/test-data?tab=environments`), use **Add environment** with a name, a base URL and an optional health-check URL. You can **Archive** an environment, or **Delete** it when no run uses it. Deleting also removes its environment-specific test data.

> Screenshot to add: test-data-grid.png: the data grid with All environments, two environment columns and a hidden secret.

## Coverage

- The story **Traceability** tab shows each AC against each case. *Uncovered* means no case covers that AC.
- **My work** on the dashboard lists **AC without a test case** and **My draft cases**.

## Gaps

Gaps of type *Missing step* and *Missing test data* come to QC. *Missing test data* about environment data goes to Dev.

1. Open **My gaps** (`/gaps`) or the story **Gaps** tab.
2. Fix the case or the data, then select **Answer**, write what you changed, and select **Answer and resolve**.
3. If an answer from someone else does not hold up, select **Reopen** on the answered gap. The person who raised the gap, QC and Admin can reopen it.

Any open gap blocks every run on the story.

## Manual runs

1. Open **Runs** and select **New manual run** (`/projects/{KEY}/runs/new`).
2. Pick the story, the environment and the *Ready* cases, then select **Start manual run**. The story moves to *In test*.
3. For each case, mark each step *Passed*, *Failed*, *Blocked* or *Skipped*. Add the actual result, and an optional evidence file.
4. Pick the case result (use the suggested one), then select **Save result**. A saved result cannot be changed. Steps you did not mark are saved as skipped.
5. When done, select **Finish run**. Cases left unrecorded show as *Not reported*. If no case has a result, the run is aborted.

Only the person who started the run can record it. A run with no activity for 4 hours is aborted.

If the start fails, the reason is shown: open gaps, no *Ready* cases, or a run already running.

> Screenshot to add: manual-run-record.png: the recording page with step statuses, evidence and the suggested case result.

## Failures

Open **Failures** (`/projects/{KEY}/failures`). A *Failed* case result opens a failure. A *Blocked* result does not.

| Status | Next step |
| --- | --- |
| *Open* | **Assign** it to a Dev. |
| *Fixed* | The Dev marked it fixed. Re-run, then **Verify** or **Reopen**. |
| *Reopened* | Back with the Dev. |
| *Verified* | Closed. A later failure of the same case opens a new failure. |

- A new failed result on a *Fixed* failure reopens it automatically.
- A passing re-run does not verify a failure for you. Select **Verify** yourself.

> Screenshot to add: failure-detail.png: a failure with the failed step, its screenshot, history and timeline.

## Re-run failed cases

On a finished run, select **Re-run failed**.

- For a Claude run, Tessio shows the command `/tessio:rerun-failed <run-id>` for a Dev to run in Claude Code. You can select **Re-run manually instead**.
- For a manual run, confirm with **Start re-run**. The new run has the failed and blocked cases that are still *Ready*.

## Sign the story off

On the story page, when the story is *In test*:

1. Check that every failure is *Verified* and no run is running.
2. Select **Mark passed** or **Mark failed** and confirm.

You can also switch a story between *Passed* and *Failed*. **Mark passed** shows "Resolve active failures and wait for running runs before marking it passed." while it is blocked. A *Failed* story goes back to the Dev, who marks it *Ready for test* again after the fix.

> Screenshot to add: story-sign-off.png: a story In test with Mark passed and Mark failed.

## Next

- [Sprint workflow](sprint-workflow.md)
- [Dev guide](dev.md)

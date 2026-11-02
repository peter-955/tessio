# QC guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for *QC*: test cases, test data, manual runs, verifying fixes and sign-off. Project Admins can do all of this too.

## Rules

| Rule | Detail |
| --- | --- |
| Only *Ready* cases run | A case needs at least one step and no unknown references to become *Ready*. |
| Open gaps block runs | Any open gap on a story stops every run on it. |
| One run at a time | A story can have only one running run, and so can a suite. |
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

### Review comments and Compare

- On the case page, the **Compare** tab shows two versions side by side. Pick them in **From version** and **To version**. Changed rows are marked, removed words are struck through and added words underlined. **Show only changes** hides the rows that are the same.
- On the **Review** tab, pick **Comment on** (the whole case or one step), write the comment, then select **Add comment**. It is saved on the current version. The author fixes the case and you select **Resolve**. Any Admin or QC can resolve a comment.
- While a comment is open, **Mark ready** is disabled. Resolve the open comments first.
- If an Admin turns on **Reviewer must not be the author** (project settings, **Review** card), the person who saved the current version can't mark it Ready or reviewed. Another QC or Admin must do it.

### Labels

- On the case page, **Details** tab, select **Edit labels** to pick labels, or type a new name and select **Create and add**. Then select **Save labels**. Labels aren't part of the case version, so they work in any status.
- On **Test cases**, the label chips show under each title. Use the **Labels** filter to list the cases that carry every chosen label.
- An Admin renames, recolours and deletes labels in project settings (**Labels** card). Deleting a label removes it from every case.

### Flaky, disagreeing and quarantined cases

- **Flaky**: in the last 10 passed or failed results on this version, the case flipped between pass and fail 3 or more times. Saving a new version starts the count again.
- **Disagreeing**: the latest manual result and the latest Claude result on this version differ, and are at most 24 hours apart. Check which one is right.
- **Quarantine** a case you don't trust yet: on the case page, select **Quarantine** and give an optional reason. **Release quarantine** takes it out. The case also leaves quarantine by itself after 10 passes in a row. Today quarantine is only a flag with a history (History tab): the case still runs and still opens failures.
- On **Test cases**, the badges show in the Status column, and **Flaky only**, **Disagreeing only** and **Quarantined only** filter the list.

### Shared steps

- Open **Shared steps** (`/projects/{KEY}/shared-steps`) and select **New shared step**. Give it a title, a key (letters, digits and `_`, starting with a letter; it can't change later) and its steps. Each save adds a version.
- In the case editor, select **Insert shared step** under the steps and pick one. The case shows it collapsed; **Show steps** opens its steps read-only. The case always runs the shared step's latest version, so editing it changes every case that uses it from the next run on. A run already started keeps the steps it started with.
- The shared step page shows **Used by N cases** and lists them. **Archive** stops it being inserted into more cases; cases that already use it keep running it. **Restore** brings it back.
- A shared step can't contain another shared step. Importing cases from a spreadsheet or from Claude gives plain steps only; insert shared steps afterwards in the editor.

### Data rows (one case, several sets of values)

- In the case editor, **Parameters and data rows**: select **Add parameter** to name a value (for example `card`), then **Add data row** for each set of values. Use the parameter as `{{param.card}}` in the preconditions and steps.
- Each row runs the case once, as one *iteration*. At most 20 parameters and 20 rows. A value may be a test data reference such as `{{data.card_number}}`; never type a secret in a row (it is refused).
- The case's result in a run is its worst iteration: *Failed* before *Blocked* before *Passed* before *Skipped*.

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

You can also answer your gaps in Claude Code with `/tessio:answer-gaps` (one story: `/tessio:answer-gaps SHOP-12`). Claude suggests answers with their sources, you pick or write your own, reassign or skip, and nothing is saved until you confirm. A missing plain value is saved to **Test data** too; for a secret, Claude gives the **Test data** link and you add it there. Claude doesn't edit cases: at the end it lists the cases the answers suggest updating, for you to edit.

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

A data-driven case shows one block per iteration on the run page and on the recording page. When you record it by hand, save each iteration with **Save iteration n**; the case counts as recorded once every iteration has a result.

## Regression suites

A suite groups cases from many stories, such as a checkout regression run every sprint.

1. Open **Suites** (`/projects/{KEY}/suites`) and select **New suite**. Names are unique in the project.
2. On the suite page, add cases with **Add cases** (pick them) or **Add by filter** (labels, priorities, story, sprint). The filter runs once: the matches are added at the end, and the suite keeps them as a fixed list.
3. Reorder by dragging the handle (or focus it and use the arrow keys), or with the row menu. Remove a case from the same menu.
4. Run it by hand with **Start manual run**, or copy the **Run with Claude** command (`/tessio:run-suite "<name>"`) for Claude Code.

Rules:
- Only *Ready* cases that don't need review run. The others are skipped and listed in the run.
- Any open gap on a story with a case in the suite blocks the suite run. Answer the gaps first (or with `/tessio:answer-gaps`).
- A suite has one running run at a time.
- A suite run never changes a story's test status. Its run page and report group the results by story, and each failure opens on the case's own story.
- **Archive** keeps the suite's cases and runs, but nobody can change or run it again.

## Test plans

A test plan tracks a release's suites and stories up to sign-off. PM and QC create plans; only QC and Admin sign them off.

1. Open **Plans** (`/projects/{KEY}/plans`) and select **New plan**. A target date and an environment are optional; with an environment, only runs on it count.
2. Select **Choose suites and stories** to pick what the plan covers.
3. The plan page shows the progress bar, the cases by status (the latest result since the plan was created), and the blockers: active failures and open gaps.
4. Select **Sign off** when you are satisfied. It is refused while any failure on the plan's cases is active. Cases not run yet and open gaps are shown as warnings but don't block. After sign-off, the numbers stop moving.
5. **Close plan** ends it, signed off or not. Closing is final.

## Sign the story off

On the story page, when the story is *In test*:

1. Check that every failure is *Verified* and no run is running.
2. Select **Mark passed** or **Mark failed** and confirm.

You can also switch a story between *Passed* and *Failed*. **Mark passed** shows "Resolve active failures and wait for running runs before marking it passed." while it is blocked. A *Failed* story goes back to the Dev, who marks it *Ready for test* again after the fix.

> Screenshot to add: story-sign-off.png: a story In test with Mark passed and Mark failed.

## Next

- [Sprint workflow](sprint-workflow.md)
- [Dev guide](dev.md)

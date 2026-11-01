# PM and BA guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for *PM* and *BA*. Both roles have the same rights in Tessio. You keep stories and AC in Jira, bring them into Tessio, follow testing progress and answer the gaps routed to you.

## Rules

| Rule | Detail |
| --- | --- |
| Jira is the source | Stories and AC are read-only in Tessio. Change them in Jira, then sync. |
| AC format | Write the AC as a list under a heading or line "Acceptance criteria" in the Jira description. Without that heading, the first list is used. Items become AC1, AC2 and so on. |
| Sync scope | Active and future sprints of the project's board, plus sprints closed in the last 30 days. |
| Answers stay in Tessio | Gap answers are not written back to Jira. |
| Gaps block runs | Any open gap on a story stops every run on it, by Claude or by hand. |

## Sync from Jira

Sync runs only when someone starts it.

1. Open **Stories** (`/projects/{KEY}/stories`) or **Sprints** (`/projects/{KEY}/sprints`).
2. Select **Sync from Jira**.
3. Watch the state next to the button:

| State | Meaning |
| --- | --- |
| **Never synced** | Nobody has synced this project yet. |
| **Sync queued…** | The sync is waiting to start. |
| **Syncing…** | Tessio is reading Jira. |
| **Last synced** | Done. The date shows when. |
| **Last sync failed** | Jira refused or could not be reached. The reason follows. Try again, or ask a workspace admin to check the **Jira connection**. |

After a sync:

- A story that left the synced sprints shows **No longer in Jira scope**. Its test cases, runs and history stay.
- An AC removed in Jira shows as removed, with the date. Cases that covered it keep the link, and QC sees them as *Needs review*.
- A changed AC flags the cases that cover it as *Needs review* for QC.

> Screenshot to add: stories-sync.png: the stories list with Sync from Jira and the Last synced state.

## Read progress

| Where | What you see |
| --- | --- |
| **Dashboard** (`/projects/{KEY}`) | **Current sprint** stats, **Stories by test status**, **AC coverage** and **Recent runs**. |
| Story **Traceability** tab (`/projects/{KEY}/stories/{STORY-KEY}`) | Each AC against each test case, with the AC status. |
| **Runs** report | Open a run, then the **Report** tab. **Acceptance criteria impact** shows each AC after that run. |

AC status on the **Traceability** tab:

| Status | Meaning |
| --- | --- |
| *Uncovered* | No test case covers this AC. Ask QC to write one. |
| *Not run* | Cases exist, but at least one has no result yet or was skipped, and none failed or was blocked. |
| *Passed* | Every covering case passed in its latest result. Deprecated cases do not count. |
| *Failed* | At least one covering case failed. |
| *Blocked* | A covering case was blocked in its latest result, for example by missing data, and none failed. |

> Screenshot to add: story-traceability.png: the Traceability tab with AC rows, case columns and AC status.

> Screenshot to add: run-report.png: the Report tab of a run with Acceptance criteria impact.

## Answer gaps

A gap is a question about a story, an AC or a test case. Claude files gaps during the readiness review, and people can raise them with **Raise gap**. Gaps are routed by type:

| Gap type | Goes to |
| --- | --- |
| *Missing AC* | BA |
| *Unclear goal* | BA |
| *Missing step* | QC |
| *Missing test data* | QC, or Dev for environment data |
| *Other* | Admin |

To answer:

1. Open **My gaps** from the user menu (`/gaps`), or the story **Gaps** tab.
2. Read the question. The badge "via Claude" marks gaps that Claude filed.
3. Select **Answer**, write your answer and select **Answer and resolve**.
4. If the answer changes the AC, edit them in Jira and select **Sync from Jira** again.

If the gap is not for you, select **Reassign** and pick a person or a role. A gap whose assignee was deactivated shows a *Deactivated* badge: reassign it.

The person who raised a gap, QC and Admin can reopen an answered gap. A reopened gap blocks runs again.

> Screenshot to add: gap-inbox.png: My gaps with open gaps from two stories.

## Next

- [Sprint workflow](sprint-workflow.md)
- [User flows](../../design/user-flows.md)

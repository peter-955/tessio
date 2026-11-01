# Viewer guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

This page is for *Viewer*. You can follow testing in a project but not change it. Stakeholders, managers and people from other teams usually get this role.

## What you can see

| Page | What it shows |
| --- | --- |
| **Dashboard** (`/projects/{KEY}`) | **Current sprint** stats, **Stories by test status**, **AC coverage** and **Recent runs**. **My work** says **Nothing is assigned to your role.** |
| **Sprints** and **Stories** | The sprints and stories synced from Jira, with their test status. |
| Story page | The AC, test cases, gaps, runs and the **Traceability** tab. |
| **Test cases** | Every case with its steps, versions and files. |
| **Runs** | Each run, with results, screenshots and the **Report** tab. |
| **Failures** | Every failure with its failed step, history and timeline. |
| **Test data** | Keys and values. Secret values stay hidden: you see that a secret exists, not its value. |
| **Members** | Who is in the project and with which role. |

You cannot sync, write cases, answer gaps, start runs or sign stories off. Buttons for these are hidden or disabled for you.

> Screenshot to add: viewer-story.png: a story page as a Viewer, with no action buttons.

## Use Claude to read

You can create a Claude token for the project, as in the [Dev guide](dev.md#connect-claude).

1. Open **Connect Claude** from the user menu (`/connect-claude`).
2. Pick the project and select **Create token**. The page reminds you that as a Viewer, Claude can read but not record results.
3. Run the command shown, then restart Claude Code.

Claude can then read stories, cases and results for you. It cannot start runs or record results.

## Ask for another role

1. Find the project Admin on **Members** (`/projects/{KEY}/members`).
2. Ask them for the role you need: QC to write cases, Dev to run tests, PM or BA to answer gaps.
3. The new role applies as soon as they save it. Reload the page.

If you are not in the project at all, ask a workspace admin to add you.

## Next

- [Getting started](getting-started.md)
- [Permission matrix](README.md#permission-matrix)

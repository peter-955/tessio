# Tessio user guide

**Status:** Draft, written 2026-11-01 for the build after W6. Screenshots to add.

Tessio holds the test cases, test data, runs, reports and failures of a sprint. User stories and acceptance criteria (AC) stay in Jira, and Tessio syncs them. Claude Code reads and writes through Tessio while it runs tests.

This guide is in English. The app itself is in English, French and Vietnamese.

## Who reads what

| You are | Read |
| --- | --- |
| Everyone, on the first day | [Getting started](getting-started.md) |
| Workspace owner or workspace admin | [Workspace admin](workspace-admin.md) |
| Project Admin | [Project admin](project-admin.md), then [QC](qc.md) and [Dev](dev.md) |
| PM or BA | [PM and BA](pm-ba.md) |
| QC | [QC](qc.md) |
| Dev | [Dev](dev.md) |
| Viewer | [Viewer](viewer.md) |
| Anyone who wants the whole sprint on one page | [Sprint workflow](sprint-workflow.md) |

The flows behind each page are drawn in [user flows](../../design/user-flows.md).

## Workspace roles

Every person has one workspace role.

| Workspace role | What it allows |
| --- | --- |
| *Owner* | Everything. Only the owner can change workspace roles or invite workspace admins. |
| *Workspace admin* | Users, the Jira connection, creating and archiving projects. Acts as project Admin in every project in the browser. A Claude token keeps only the person's real project role. |
| *Member* | No workspace rights. Project roles decide the rest. |

| Workspace right | Owner | Workspace admin | Member |
| --- | --- | --- | --- |
| Invite, deactivate and reset users | Yes | Yes | No |
| See each user's project access | Yes | Yes | No |
| Set up the Jira connection | Yes | Yes | No |
| Create, archive and unarchive projects | Yes | Yes | No |
| Open every project | Yes | Yes | No |
| Change workspace roles, invite workspace admins | Yes | No | No |

## Project roles

A person has one role in each project they belong to: Admin, PM, BA, QC, Dev or Viewer. A person can be QC in one project and Viewer in another.

## Permission matrix

A = Admin. "Yes" means the role can do it.

| Action | A | PM | BA | QC | Dev | Viewer |
| --- | --- | --- | --- | --- | --- | --- |
| View everything except secret values | Yes | Yes | Yes | Yes | Yes | Yes |
| Create a Claude token (a Viewer's token can only read) | Yes | Yes | Yes | Yes | Yes | Yes |
| **Sync from Jira** | Yes | Yes | Yes | No | No | No |
| Mark a story *Ready for test*, or move it back to *Not started* | Yes | No | No | No | Yes | No |
| Mark a story *Passed* or *Failed* | Yes | No | No | Yes | No | No |
| Write, edit and import test cases; attach test files | Yes | No | No | Yes | No | No |
| Manage environments; edit variables and endpoints | Yes | No | No | Yes | Yes | No |
| Save and reveal secret values | Yes | No | No | Yes | No | No |
| Use secrets in Claude runs | Yes | No | No | Yes | Yes | No |
| Raise, answer and reassign gaps | Yes | Yes | Yes | Yes | Yes | No |
| Reopen any answered gap | Yes | No | No | Yes | No | No |
| Reopen an answered gap you raised | Yes | Yes | Yes | Yes | Yes | No |
| Start Claude runs | Yes | No | No | Yes | Yes | No |
| Start and record manual runs | Yes | No | No | Yes | No | No |
| Finish another person's run | Yes | No | No | No | No | No |
| Assign failures | Yes | No | No | Yes | Yes | No |
| **Mark fixed** on a failure | Yes | No | No | No | Yes | No |
| **Verify** and **Reopen** a failure | Yes | No | No | Yes | No | No |
| Members and project settings | Yes | No | No | No | No | No |

PM and BA have the same rights, so they share one page.

### Archived projects

An archived project is read-only for everyone, workspace admins included. The banner **This project is archived** shows on every page. Revealing a secret still works there.

## Glossary

The full list is in the [product glossary](../../product/glossary.md).

| Term | Meaning |
| --- | --- |
| Story | A Jira user story, synced into Tessio. Read-only here. |
| AC | An acceptance criterion of a story, numbered AC1, AC2 and so on. |
| Test case | Steps with expected results that cover one or more AC. Code TC-1, TC-2 and so on. |
| Gap | A question about a story, AC or test case that must be answered before a run. |
| Run | One go through the *Ready* cases of a story, by Claude or by hand. |
| Case result | The outcome of one case in a run: *Passed*, *Failed*, *Blocked* or *Skipped*. |
| Failure | A failed case that a Dev fixes and a QC verifies. |
| Environment | Where tests run: a base URL and an optional health-check URL. |
| Test data | Variables, endpoints and secrets that steps refer to as `{{data.key}}`. |

## Screenshots to add

Images go in `docs/guides/user/images/` later. Each page marks the spot with "Screenshot to add".

| File | Page |
| --- | --- |
| accept-invite.png | [Getting started](getting-started.md) |
| two-factor-setup.png | [Getting started](getting-started.md) |
| recovery-codes.png | [Getting started](getting-started.md) |
| sign-in.png | [Getting started](getting-started.md) |
| app-shell.png | [Getting started](getting-started.md) |
| dashboard.png | [Getting started](getting-started.md) |
| profile.png | [Getting started](getting-started.md) |
| users-list.png | [Workspace admin](workspace-admin.md) |
| jira-connection.png | [Workspace admin](workspace-admin.md) |
| new-project.png | [Workspace admin](workspace-admin.md) |
| project-members.png | [Project admin](project-admin.md) |
| project-settings.png | [Project admin](project-admin.md) |
| stories-sync.png | [PM and BA](pm-ba.md) |
| story-traceability.png | [PM and BA](pm-ba.md) |
| gap-inbox.png | [PM and BA](pm-ba.md) |
| run-report.png | [PM and BA](pm-ba.md) |
| test-case-editor.png | [QC](qc.md) |
| test-case-import.png | [QC](qc.md) |
| test-data-grid.png | [QC](qc.md) |
| manual-run-record.png | [QC](qc.md) |
| failure-detail.png | [QC](qc.md) |
| story-sign-off.png | [QC](qc.md) |
| story-mark-ready.png | [Dev](dev.md) |
| connect-claude.png | [Dev](dev.md) |
| run-detail-live.png | [Dev](dev.md) |
| failures-assigned-to-me.png | [Dev](dev.md) |
| viewer-story.png | [Viewer](viewer.md) |

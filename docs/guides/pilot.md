# Pilot checklist

**Status:** Draft, written 2026-11-01. Pilot not started; WBS 8.4 is open.

The pilot moves one team from Google Sheets and the shared data file to Tessio. Tick each item as it is done. The user guide is in [user/README.md](user/README.md), and the flows are in [user flows](../design/user-flows.md).

## Goal and scope

- [ ] One project and one sprint run in Tessio and in Google Sheets side by side.
- [ ] At the end of the sprint, the team decides with the exit criteria below.
- [ ] If the criteria are met, the sheet and the data file are retired.

Pilot project: ______ · Sprint: ______ · Start date: ______ · End date: ______

## People

- [ ] A named pilot lead, who runs this checklist and the weekly comparison: ______
- [ ] The workspace owner: ______
- [ ] At least one PM or BA: ______
- [ ] At least one QC: ______
- [ ] At least one Dev with Claude Code: ______

## Go-live gates

These are open today. All must be done before setup starts.

- [ ] VPS, domain, DNS and TLS are in place.
- [ ] The production SMTP provider is chosen and invite and reset emails arrive.
- [ ] The object storage bucket exists, with CORS for browser uploads from the Tessio domain. A screenshot upload and an import upload work in the browser.
- [ ] `https://<Tessio>/api/plugin/marketplace.json` answers on the production address, and the install command from the Connect Claude page works on a pilot laptop.
- [ ] A daily Postgres dump runs and one restore has been tried. Automated backups (WBS 7.5) are Later, so a manual daily dump is the minimum.
- [ ] The AC format has been checked on real stories of a real Jira Cloud site (WBS 1.7.4).
- [ ] The case import has been tried on a real sample sheet of the team (WBS 3.6.7).
- [ ] The W7 security and accessibility fixes are merged.
- [ ] The end-to-end suite is green (W8.T1).

## Setup

Follow the [workspace admin guide](user/workspace-admin.md) and the [project admin guide](user/project-admin.md).

- [ ] The owner accepts the invite and sets up two-factor.
- [ ] The Jira connection is saved with **Test and save**.
- [ ] The pilot project is created and linked to the Jira project and board.
- [ ] Everyone is invited and has a project role.
- [ ] The environments are added, and the **Default environment** is set.
- [ ] **Allowed file types** include .xlsx, .csv, `text/plain` and `application/json`.
- [ ] The shared data file is imported into **Test data**.
- [ ] Every password, token and API key in it is marked *Secret*.
- [ ] The sheet tabs are imported as test cases.
- [ ] The case count per story matches the sheet. Differences are written down.
- [ ] The imported cases are reviewed and moved to *Ready*.
- [ ] Each Dev connects Claude, as in [Claude setup](claude-setup.md).

## During the sprint

For each story of the sprint:

- [ ] Sync from Jira after the AC are written.
- [ ] Coverage check: no AC is *Uncovered*.
- [ ] Readiness review with `/tessio:review-readiness`.
- [ ] Gaps answered in Tessio, not in chat.
- [ ] Run with Claude or by hand.
- [ ] Failures assigned, fixed and marked fixed.
- [ ] Failed cases re-run.
- [ ] Failures verified and the story signed off.
- [ ] The sheet is still updated in parallel.

## Weekly comparison

Fill one row per week for Tessio and one for the sheet.

- [ ] Number of cases and steps per story.
- [ ] AC coverage.
- [ ] Result per case.
- [ ] Failures found and fixed.
- [ ] Gaps captured (Tessio) against questions asked in chat.
- [ ] Time per role spent on testing admin.
- [ ] Claude tokens per run (WBS 5.7).
- [ ] Data found only in the sheet or the data file.

| Week | Source | Cases | Steps | AC covered | Failures | Gaps | Time per role | Claude tokens per run | Only in this source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Tessio | | | | | | | | |
| 1 | Sheet | | | | | | | | |

## Feedback log

- [ ] Every problem the team meets is logged here the same day.
- [ ] The pilot lead reviews the log every week.

| Date | Who | Screen | Problem | Severity (high, medium, low) |
| --- | --- | --- | --- | --- |
| | | | | |

## Exit criteria

The sheet is retired only when all of these are true.

- [ ] Every story of the sprint is signed off in Tessio.
- [ ] No data is left only in the sheet or the data file.
- [ ] No high-severity feedback is still open.
- [ ] The team agrees.

## Retire the sheet

- [ ] Make the sheet read-only.
- [ ] Add a link to Tessio at the top of the sheet.
- [ ] Archive the sheet. Do not delete it.
- [ ] Move the old data file out of shared drives.
- [ ] Check that every secret from the data file is in Tessio.
- [ ] Set a date to delete the data file: ______
- [ ] Delete the data file on that date.

## Rollback

If the exit criteria are not met:

- [ ] Keep the sheet live as the source.
- [ ] Record why in the feedback log.
- [ ] Plan a second pilot, with a date: ______

## Sign-off

- [ ] Every role below has signed.

| Role | Name | Date |
| --- | --- | --- |
| Pilot lead | | |
| Workspace owner | | |
| PM or BA | | |
| QC | | |
| Dev | | |

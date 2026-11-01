# Release plan

**Status:** Draft, written 2026-11-01. Dates are TBD until the VPS, SMTP provider and pilot team are known.

Tessio ships as one MVP, after a pilot sprint. There is no public beta and no staged feature rollout. The build ran in eight waves (W1 to W8), each one a set of work packages from the [WBS](../wbs/wbs.md). Nothing is committed yet: Peter commits when everything is done, so CI has no history so far. The open items that stand between the build and go-live are the [blockers](../wbs/wbs.md#blockers) in the WBS.

## Milestones

| Milestone | Scope | WBS | State | Target date |
| --- | --- | --- | --- | --- |
| M1 W1 Foundations | Permissions, projects, live events, jobs, files, secrets, OpenAPI, design system, CI and deploy files, Claude plugin | 2.4, 2.8, 3.14.1, 3.14.2, 4.1, 4.2b, 4.3, 4.5, 4.6, 4.6b, 4.8, 4.11, 5.3, 5.4, 5.5, 5.7, 6.1, 6.3, 7.1, 7.2, 7.3, 7.3b, 7.4 | Built 2026-11-01, uncommitted | TBD |
| M2 W2 Accounts | API tokens, accounts, Jira connection, test data server; auth screens, app shell, uploads | 3.1.1, 3.1.2, 3.1.4, 3.1.6, 3.2.1, 3.2.2, 3.2.3, 3.2.4, 3.2.7, 3.3.3, 3.3b.2, 3.3b.3, 3.9.4, 3.13.2, 3.14.3, 3.14.4, 3.14.6, 4.2c, 5.2 | Built 2026-11-01, uncommitted | TBD |
| M3 W3 Jira sync | Jira sync, notifications server; users, account, project and test data screens | 1.7.4, 3.1.5, 3.2.5, 3.2.6, 3.3.1, 3.3.2, 3.3.4, 3.3b.1, 3.3b.4, 3.9.1, 3.9.2, 3.9.3, 3.9.5, 3.13.1, 3.13.4, 4.4, 4.9 | Built 2026-11-01, uncommitted | TBD |
| M4 W4 Test cases | Test cases and gaps server; story and notification screens | 3.5.1, 3.5.2, 3.5.3, 3.5.4, 3.5.5, 3.5.6, 3.6.5, 3.6.6, 3.7.4, 3.8.2, 3.8.4, 3.12.1 | Built 2026-11-01, uncommitted | TBD |
| M5 W5 Runs | Runs, MCP tools, failures, read models; test case and gap screens | 3.6.1, 3.6.2, 3.6.3, 3.6.4, 3.6.4b, 3.6.7, 3.7.3, 3.8.1, 3.8.3, 3.8.5, 3.11.3, 4.7, 4.12, 5.1 | Built 2026-11-01, uncommitted | TBD |
| M6 W6 Run screens | Run, manual run, failure, traceability and dashboard screens; mock data removed | 3.4.1, 3.4.2, 3.4.3, 3.7.1, 3.7.2, 3.10.1, 3.10.2, 3.10.3, 3.10.4, 3.10.5, 3.10.6, 3.10.8, 3.11.1, 3.11.2, 3.11.5 | Built 2026-11-01, uncommitted | TBD |
| M7 W7 Hardening | Security and accessibility hardening; specs, NFRs, user flows, user guide, pilot checklist | 1.3, 1.4, 2.5, 6.4, 6.5, 8.1, 8.4 | Built 2026-11-01, uncommitted | TBD |
| M8 W8 Release prep | End-to-end tests, Claude setup guide, developer docs, this release plan and the WBS update | 1.6, 6.2, 8.2, 8.3 | Built 2026-11-01, uncommitted | TBD |
| M9 Production ready | First commit and CI green, images rebuilt, VPS + DNS + TLS, SMTP, bucket CORS, daily dump, real Jira check, real import sheet, manual browser pass (the blockers that gate go-live, see below) | 1.7.4, 3.6.7, 3.9.5, 4.6, 4.6b, 7.1, 7.2, 7.3, 7.3b, 7.4 | Not started | TBD |
| M10 Pilot | One sprint side by side with the sheet ([pilot.md](../guides/pilot.md)) | 8.4 | Not started | TBD |
| M11 MVP go-live | Pilot exit criteria met, sheet retired | 8.4 | Not started | TBD |
| Later | Every `Later` row of the WBS | 3.1.3, 3.2.8, 3.4.4, 3.6.8, 3.9.6, 3.10.7, 3.11.4, 3.12.2, 3.13.3, 4.10, 7.5 | Not planned | TBD |

## Go-live gates

M9 is done when every box below is ticked. Each item points to its blocker in the WBS, where the current assumption and what is needed are written down.

- [ ] B-1: a git remote, the first commit and one green run of CI and the e2e workflow ([blockers](../wbs/wbs.md#blockers)).
- [ ] B-2: production images rebuilt from the committed tree, and the worker started once with the expected job schedulers.
- [ ] B-3: a VPS, domain, DNS and TLS, one deploy with `deploy/deploy.sh`, and rate limits checked behind Caddy.
- [ ] B-4: an SMTP provider chosen; invite and reset emails arrive.
- [ ] B-5: production object storage decided, with bucket CORS for the Tessio domain.
- [ ] B-6: `python -m app.commands.jira_probe` run on a real Jira Cloud site, and the AC format confirmed.
- [ ] B-7 and B-9: the case import tried on a real sample sheet, and the column format confirmed.
- [ ] B-8: the data import tried on the real shared data file.
- [ ] B-11: the plugin marketplace host chosen, and `NEXT_PUBLIC_TESSIO_PLUGIN_MARKETPLACE` set at client build time.
- [ ] B-13: one manual pass in a real browser against the running stack.
- [ ] B-15: a daily Postgres dump running, and one restore tried.
- [ ] Every item under [Go-live gates in the pilot checklist](../guides/pilot.md#go-live-gates) is ticked.

These blockers do not gate go-live: B-10 is the pilot itself (M10), B-12 (the original team skills) can follow because the new skills cover the workflow, B-14 (final brand) is accepted as is for MVP, and B-16 (Mermaid parsing) only affects the docs.

## Exit criteria per milestone

- **M8:** the e2e suite is green locally, and the W8 docs are merged into the tree.
- **M9:** every go-live gate above is ticked.
- **M10:** the pilot sprint ends and the team decides with the [pilot exit criteria](../guides/pilot.md#exit-criteria).
- **M11:** the [pilot exit criteria](../guides/pilot.md#exit-criteria) are all true, and the sheet and the data file are [retired](../guides/pilot.md#retire-the-sheet).

## Risks

- **Jira AC format (B-6):** the AC parser has only seen mock Jira documents. If real stories write AC differently, sync, traceability and coverage are wrong until the parser is adjusted.
- **Import formats (B-7, B-8, B-9):** the case import columns and the data file format are guesses. A different real format means rework before the team can move off the sheet.
- **No CI history (B-1):** every check so far ran by hand in one working tree. The first CI run may surface environment differences, and the workflows themselves are untested.
- **No manual browser pass (B-13):** all screens are covered by jsdom tests, and the Playwright e2e suite checks in Chromium that 17 screens have no horizontal scroll at 375 px and that the focused-input border has enough contrast. 200 % zoom, the skip link, screen readers, a real QR scan, real uploads and live updates are still unchecked and may show defects.
- **Single VPS without backups (B-3, B-15):** Postgres, Redis and file storage share one machine, and automated backups are Later. A disk failure before the daily dump is in place loses data.

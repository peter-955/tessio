# Product vision

**Status:** Draft · **Updated:** 2026-11-01

## One-liner

Tessio is the single home for a team's sprint testing. Jira user stories and their acceptance criteria (AC) are synced read-only. Test cases, test data, runs and failures live in Tessio. Claude executes runs on the developer's machine through Tessio's MCP server.

## Problem

Today the testing work of one sprint is spread over five places ([testing workflow proposal §1](../discussions/testing-workflow-proposal.md#1-how-we-work-today)):

| Where | What lives there |
| --- | --- |
| Google Sheets | The test plan: one tab per story, step-by-step cases, each covering some AC |
| A shared data file | Usernames, passwords, site URLs and health-check APIs, in plain text |
| Chat sessions | Claude's pre-run questions about gaps and their answers, lost afterwards |
| Report files | Claude's run reports and the re-run reports |
| Claude config | The skills, commands and hooks pointed at a sheet URL |

What hurts:

- No traceability: nobody can easily see which AC are covered, which fail, or a case's history across re-runs.
- Answers to gap questions never reach the test cases, so the same gaps come back.
- Credentials sit in a plain file with no access control or audit.
- PM and BA must open sheets and report files to know where testing stands.

## Who it's for

Each person has one role per project, and one workspace role ([capability matrix](../spec/README.md#role--capability-matrix)).

| Project role | What they do in Tessio |
| --- | --- |
| Admin | Manages the project and its members; can do everything in it |
| PM | Follows sprint progress; syncs from Jira; answers gaps |
| BA | Owns the AC in Jira; syncs; answers AC and goal gaps |
| QC | Writes and reviews test cases, manages test data and secrets, runs manual tests, assigns and verifies failures, signs stories off |
| Dev | Marks stories Ready for test, runs Claude, answers data gaps for environments, fixes failures |
| Viewer | Reads everything except secret values |

| Workspace role | What they do |
| --- | --- |
| Owner | Everything a workspace admin does, plus managing workspace admins and roles |
| Workspace admin | Invites and manages users, creates and archives projects, sets the Jira connection; acts as Admin in every project |
| Member | Sees only the projects they belong to |

## MVP goals

- One place per story for the AC, the test cases, the gaps, the runs, the screenshots and the failures.
- Every AC covered by at least one case, with a pass or fail status from the latest results ([traceability](../spec/traceability.md)).
- No run while a question is open: gaps are routed to the right role and answered in Tessio ([readiness review](../spec/readiness-review.md)).
- Claude runs Ready cases in the developer's browser and records one result per case, with a screenshot for every step ([runs](../spec/runs.md)).
- Secrets encrypted, revealed only to Admin and QC, handed to Claude only for its own run, masked in every report, and every access audited.
- Failures tracked from the first failed result to QC verification, then the story signed off ([failures](../spec/failures.md)).

## Success measures

| Measure | Target | Where it is tracked |
| --- | --- | --- |
| Pilot | One sprint run in Tessio in parallel with Google Sheets, then the sheet is retired | WBS 8.4 (open) |
| Claude cost | Tokens per test case measured on a pilot story, before and after `scale: 0.5` for navigation screenshots | WBS 5.7 (open) |
| Coverage | Every AC of the pilot sprint has a Ready case before its run | dashboard "AC covered" |
| Gap reuse | No gap asked twice for the same story in the pilot | gap list per story |

## Non-goals

- **The server never runs a browser.** Claude runs on the developer's machine; testers run manual cases. Tessio stores and reports.
- **No writes to Jira.** Stories, AC and sprints are read-only copies; gap answers stay in Tessio.
- **No external bug tracker.** Failures live only in Tessio.
- **No public sign-up.** People join by invite only.
- **One workspace.** Tessio serves one company with many projects; it is not a multi-tenant SaaS.
- **Not a CI runner.** Tessio does not run framework test code or collect CI results.

## Answered questions

| Question | Answer |
| --- | --- |
| Does Tessio execute tests itself, or ingest results from CI? | Neither. Claude executes on the developer's machine and Tessio orchestrates through MCP; testers record manual runs ([open questions #1](../discussions/open-questions.md)). |
| Where do user stories live? | In Jira. Tessio syncs sprints, stories and AC read-only when someone presses Sync from Jira. Test cases, test data, runs and failures live only in Tessio. |
| Is there manual testing? | Yes, in special cases. A tester runs a case by hand and records each step in Tessio (executor `manual`). |

## Where to read more

- What is built, by module: [features.md](features.md).
- The words we use: [glossary.md](glossary.md).
- The full functional spec: [../spec/README.md](../spec/README.md).
- The flows and state diagrams: [../design/user-flows.md](../design/user-flows.md).

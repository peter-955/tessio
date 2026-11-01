# Features

**Status:** Draft · **Updated:** 2026-11-01

The MVP features of [WBS section 3](../wbs/wbs.md#3-client-application-feature-modules), what the code does today (waves W1–W6), and where each one is specified. The test-suite prototype model was superseded on 2026-10-31 by the story and AC model below.

**Status values:** **built** = server, client and tests exist · **partly** = built, but a named part is missing or unverified · **blocked** = waits on something outside the code. No screen has been checked by hand in a browser against a running stack yet; the pilot checklist covers that.

## MVP features

### 3.1 App shell and navigation · [spec](../spec/app-shell.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.1.1 | Project sidebar by capability, workspace items for workspace admins | every `/projects/[projectKey]/*` page | built |
| 3.1.2 | Top bar: project switcher, search placeholder, notification bell, account menu | every signed-in page | built (search is a disabled placeholder, see Later) |
| 3.1.4 | Responsive layout with a drawer below `md` | every signed-in page | partly: 375 px not checked in a browser |
| 3.1.5 | Light, dark and system theme saved to the profile | sidebar, `/profile` | built |
| 3.1.6 | Not-found, project-not-found and error pages | any unknown route, `error.tsx`, `global-error.tsx` | built |

### 3.2 Authentication and account · [spec](../spec/authentication-and-account.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.2.1 | Sign in with email and password, then a second factor | `/sign-in`, `/two-factor` | built |
| 3.2.2 | Accept an invite and set a password | `/invite/[token]` | built |
| 3.2.3 | Required two-factor setup and 10 recovery codes | `/two-factor/setup` | built |
| 3.2.4 | Forgot and reset password | `/forgot-password`, `/reset-password/[token]` | built |
| 3.2.5 | Profile: name, avatar, password, recovery codes, own authenticator reset, theme, language | `/profile` | built |
| 3.2.6 | Connect Claude: personal API tokens and the plugin install command | `/connect-claude` | partly: the plugin marketplace host is undecided |
| 3.2.7 | Sign out of all devices | account menu | built |

### 3.3 Projects · [spec](../spec/projects.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.3.1 | Create a project linked to a Jira project and board | `/projects/new` | built |
| 3.3.2 | Edit, archive and unarchive a project (archived = read-only) | `/projects`, `/projects/[projectKey]/settings` | built |
| 3.3.3 | Project switcher | top bar | built |
| 3.3.4 | Project members with one role each | `/projects/[projectKey]/members` | built |

### 3.3b User management · [spec](../spec/user-management.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.3b.1 | User directory: invite, resend, deactivate, reactivate | `/users` | built |
| 3.3b.2 | Workspace roles: Owner, Workspace admin, Member | `/users` | built (no owner transfer) |
| 3.3b.3 | Reset a user's two-factor | `/users` | built |
| 3.3b.4 | Per-user project access | `/users/[userId]` | built |

### 3.4 Dashboard · [spec](../spec/dashboard.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.4.1 | Current sprint: stories by test status, open gaps, active failures, AC coverage | `/projects/[projectKey]` | built |
| 3.4.2 | Recent runs | `/projects/[projectKey]` | built |
| 3.4.3 | My work per role, plus the unassigned failure count | `/projects/[projectKey]` | built |

### 3.5 Sprints and user stories · [spec](../spec/sprints-and-stories.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.5.1 | Sprint list and sprint detail | `/projects/[projectKey]/sprints`, `/sprints/[sprintId]` | built |
| 3.5.2 | Story list with test status, Jira link and progress columns | `/projects/[projectKey]/stories` | built |
| 3.5.3 | Story detail: description, AC, Test cases, Gaps, Runs and Traceability tabs | `/projects/[projectKey]/stories/[jiraKey]` | built |
| 3.5.4 | Sync from Jira on demand, with live status | stories and sprints pages | partly: not tried on a real Jira site (spike 1.7.4) |
| 3.5.5 | QC sign-off: Mark passed or failed | story detail | built |
| 3.5.6 | Dev marks a story Ready for test | story detail | built |

### 3.6 Test cases · [spec](../spec/test-cases.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.6.1 | Case list with filters and latest result | `/projects/[projectKey]/test-cases` | built |
| 3.6.2 | Case editor: business value, preconditions, steps, expected results | `/test-cases/new`, `/test-cases/[caseCode]` | built |
| 3.6.3 | Link cases to AC | case editor | built |
| 3.6.4 | `{{data.key}}` references with suggestions | case editor | built |
| 3.6.4b | Case files under a key, versioned, `{{file.key}}` | case editor, Files tab | built |
| 3.6.5 | Review workflow: Draft, In review, Ready, Deprecated | case editor | built |
| 3.6.6 | Version history with compare; each run keeps the version it ran | case editor, History tab | built |
| 3.6.7 | Import from `.xlsx` or `.csv` | Import dialog on the case list | blocked: no sample of the team's sheet, so the columns are a guess |

### 3.7 Traceability · [spec](../spec/traceability.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.7.1 | AC × test case matrix per story | story detail, Traceability tab | built |
| 3.7.2 | Uncovered-AC warning | Traceability tab | built |
| 3.7.3 | AC status from each case's latest result | Traceability tab, dashboard | built |
| 3.7.4 | "AC changed, review" flag; removed AC kept | case list and editor | built |

### 3.8 Readiness review · [spec](../spec/readiness-review.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.8.1 | Gap list per story | story detail, Gaps tab | built |
| 3.8.2 | Automatic routing by type | (server) | built |
| 3.8.3 | Answer (resolves), reopen and reassign | Gaps tab, `/gaps` | built |
| 3.8.4 | Runs blocked while any gap is open | (server), Gaps tab banner | built |
| 3.8.5 | Gap inbox per user | `/gaps` | built |

### 3.9 Environments and test data · [spec](../spec/environments-and-test-data.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.9.1 | Environment list with base URL and health-check URL | `/projects/[projectKey]/test-data`, Environments tab | built |
| 3.9.2 | Create, edit, archive and delete environments | Environments tab | built |
| 3.9.3 | Variables, endpoints and secrets, per project and per environment | Data tab | built |
| 3.9.4 | Secret masking, role-based reveal, audited use in runs | Data tab, MCP `resolve_data` | built |
| 3.9.5 | Import the shared data file (`.env`, JSON, YAML) | Import dialog on the Data tab | blocked: no sample of the team's file, so the format is assumed |

### 3.10 Runs · [spec](../spec/runs.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.10.1 | Run list with status and story filters | `/projects/[projectKey]/runs` | built |
| 3.10.2 | Run detail with per-step results and screenshots, "Screenshot missing" state | `/projects/[projectKey]/runs/[runId]` | built |
| 3.10.3 | Claude runs through MCP with live progress per case | run detail; MCP tools | partly: tokens per case not measured yet (WBS 5.7) |
| 3.10.4 | Manual run with step results and evidence | `/runs/new`, `/runs/[runId]/record` | built |
| 3.10.5 | Re-run failed only, linked to the original run | run detail | built |
| 3.10.6 | Run report: counts, failed cases, AC impact, missing screenshots, summary | run detail, Report tab | built |
| 3.10.8 | Aborted runs after 4 hours without activity | run list and filter | built |

### 3.11 Failures · [spec](../spec/failures.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.11.1 | Failure list with status, assignee (including Unassigned) and story filters | `/projects/[projectKey]/failures` | built |
| 3.11.2 | Failure detail: failed step, screenshot, error, history, timeline | `/projects/[projectKey]/failures/[failureId]` | built |
| 3.11.3 | Mark fixed, verify, reopen; automatic reopen on a new failed result | failure detail | built |
| 3.11.5 | Assign and reassign; new failures start unassigned | failure detail | built |

### 3.12 Notifications · [spec](../spec/notifications.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.12.1 | In-app notifications: gap assigned, failure assigned, run finished | bell in the top bar | built |

### 3.13 Settings · [spec](../spec/settings.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.13.1 | Project settings: name, description, Jira board, default environment | `/projects/[projectKey]/settings` | built |
| 3.13.2 | Workspace Jira connection | `/settings` | partly: not tried on a real Jira Cloud site |
| 3.13.4 | Allowed file types per project | `/projects/[projectKey]/settings` | built |

### 3.14 Client ↔ API · [spec](../spec/client-api.md)

| WBS | Feature | Client route | Status |
| --- | --- | --- | --- |
| 3.14.1 | API types generated from the server's OpenAPI file | (build) | built |
| 3.14.2 | Data-fetching layer; mock data removed | every page | built |
| 3.14.3 | Session handling: sign-in, two-factor step, expired session | every page | built |
| 3.14.4 | Live events refresh the affected data | every page | built |
| 3.14.5 | `/api` and `/mcp` forwarded in local development | (dev server) | built |
| 3.14.6 | Uploads and downloads through signed links | uploads in cases, runs, imports, avatar | partly: no end-to-end browser upload to RustFS run yet |

## Later

From the Later rows of the [WBS](../wbs/wbs.md):

| WBS | Feature |
| --- | --- |
| 3.1.3 | Global search (stories, test cases, runs) |
| 3.2.8 | SSO (Google, Microsoft, Atlassian) |
| 3.4.4 | Trend charts across sprints |
| 3.6.8 | Claude drafts test cases from AC for QC to review |
| 3.9.6 | "Where used" list for each data key |
| 3.10.7 | Export the run report (PDF, Markdown) |
| 3.11.4 | Comments on a failure |
| 3.12.2 | Email and Slack notifications |
| 3.13.3 | Notification settings |
| 4.10 | Full audit log (secret access is already audited) |
| 7.5 | Backups and disaster recovery |

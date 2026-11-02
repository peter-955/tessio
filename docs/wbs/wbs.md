# Work Breakdown Structure (WBS)

**Status:** Draft, build status updated 2026-11-02 after waves W9 and W10 (2026-11-01 after waves W1–W7 and W8), updated 2026-10-31 for the accepted [testing workflow proposal](../discussions/testing-workflow-proposal.md), the [server proposal](../discussions/server-proposal.md) and [ADR 0004](../decisions/0004-backend-stack.md).

A deliverable-oriented breakdown of everything needed to ship Tessio. Each lowest-level item is a **work package**: small enough to design, estimate and assign.

**Legend**

- **Phase:** `MVP` = first usable version · `Later` = after MVP · `?` = depends on an [open question](../discussions/open-questions.md)
- **Status** (last checked 2026-11-01):
  - ✅ done: the real thing, working on real data or final UI
  - 🚧 partly done: the note says what exists and what is missing
  - 🧪 mock only: the screen exists in `client/` with mock data, no server yet
  - ♻️ mock on the old "test suite" model: exists, needs rework
  - 🟡 placeholder only
  - blank: not started
- Nothing is committed yet and no screen has been checked by hand in a browser against a running stack; see [Assumptions & blockers](#assumptions--blockers).

## Build progress

✅ means built, wired into the base app and covered by passing automated tests: server `pytest` (2362 tests), client `vitest` (1392 tests in 238 files), the plugin unit tests (59) and the Playwright e2e suite (37 tests), as of W10 POST on 2026-11-02. The missing manual browser pass is a release gate (B-13), not a 🚧 on every screen. 🚧 means part of the package is missing or it waits on an outside resource.

| Area | ✅ Done | 🚧 Partly done | Mock or placeholder | Next gap |
| --- | --- | --- | --- | --- |
| 1–2 Planning & design | 1.1, 1.2, 1.3, 1.4, 1.5, 1.7.1, 1.7.2, 1.7.3, 2.1, 2.3, 2.4, 2.4b, 2.5, 2.8 | 1.6, 1.7.4, 2.2 | | Real Jira check (1.7.4); release dates (1.6); final brand, wireframes and mockups (2.2, 2.6, 2.7) |
| 3 Client | 3.1.1, 3.1.2, 3.1.4–3.1.6, 3.2.1–3.2.7, 3.3.1–3.3.5, 3.3b.1–3.3b.4, 3.4.1–3.4.3, 3.5.1–3.5.7, 3.6.1–3.6.6 (with 3.6.4b), 3.6.10, 3.7.1–3.7.4, 3.8.1–3.8.5, 3.9.1–3.9.4, 3.9.7, 3.10.1–3.10.6, 3.10.8, 3.10.9, 3.10.11, 3.11.1–3.11.3, 3.11.5, 3.11.6, 3.12.1, 3.13.1, 3.13.2, 3.13.4, 3.14.1–3.14.6 | 3.6.7, 3.6.8, 3.6.9, 3.9.5, 3.10.10 | | Real import samples (3.6.7, 3.6.9, 3.9.5); manual browser pass (B-13) |
| 4 Server | 4.0, 4.1, 4.2, 4.2b, 4.2c, 4.3, 4.4, 4.5, 4.7, 4.8, 4.9, 4.11, 4.12, 4.13, 4.14 | 4.6, 4.6b | | VPS + SMTP (7.3, 4.6b); production object storage (4.6) |
| 5 Claude integration | 5.1, 5.2, 5.4, 5.5, 5.6, 5.8, 5.10, 5.11, 5.12, 5.15 | 5.3, 5.7, 5.9, 5.13, 5.14 | | Original team skills (5.3); token measurement in the pilot (5.7); first real Claude import (5.9); first real failing run with diagnosis (5.14) |
| 6 QA | 6.1, 6.2, 6.3, 6.5 | 6.4 | | Manual keyboard and screen-reader pass (6.4); first e2e run in CI (B-1) |
| 7 DevOps | 7.1b | 7.1, 7.2, 7.3, 7.3b, 7.4 | | First commit and CI run (7.1, 7.2); VPS + SMTP (7.3, 4.6b) |
| 8 Docs & rollout | 8.2, 8.3 | 8.1, 8.4 | | Pilot (8.4) |
| 9 Competitive features (W9 and W10 so far) | 9.1, 9.2, 9.3 | 9.13, 9.18 | | `/tessio:answer-gaps` dry run in a real Claude session (9.18); quarantine in script runs (9.13, W13); `/tessio:run-suite` and per-iteration recording not yet tried in a real Claude session (9.1, 9.2) |

---

## 1. Discovery & planning

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 1.1 | Product vision and target users ([vision.md](../product/vision.md)) | MVP | ✅ [vision.md](../product/vision.md) written |
| 1.2 | Testing workflow and roles ([proposal](../discussions/testing-workflow-proposal.md)) | MVP | ✅ proposal accepted |
| 1.3 | Functional spec per feature module (section 3) | MVP | ✅ [docs/spec/](../spec/README.md), one spec per feature module |
| 1.4 | Non-functional requirements (security, storage growth, performance) | MVP | ✅ [non-functional-requirements.md](../spec/non-functional-requirements.md); performance and browser rows are [ASSUME], unmeasured |
| 1.5 | Server stack decision ([ADR 0004](../decisions/0004-backend-stack.md): Python + FastAPI) | MVP | ✅ ADR accepted |
| 1.6 | Release plan and milestones | MVP | 🚧 milestones in [release-plan.md](../product/release-plan.md), dates TBD |
| 1.7.1 | Spike: invite → password → required TOTP → recovery-code sign-in, end to end ([server proposal §16](../discussions/server-proposal.md#16-spikes-before-building)) | MVP | ✅ server only, covered by `server/tests/api/auth/test_sign_in_flow.py` |
| 1.7.2 | Spike: screenshot upload hook (Claude in Chrome's `save_to_disk` path, the MCP tool response inside the hook, saved file size when `scale` is below 1) | MVP | ✅ hook tested end to end with a headless Claude session (the model sees a 92-character result); Chrome saves JPEGs (1400 × 845, about 46 KB), `scale: 0.5` halves both sides |
| 1.7.3 | Spike: server-sent events through Next.js `rewrites` in local development | MVP | ✅ events arrive every second through the rewrite, also with browser-like `Accept-Encoding`, once the stream sends `Cache-Control: no-transform` (without it Next.js gzips the stream and holds every event back) |
| 1.7.4 | Spike: Jira `/rest/api/3/search/jql` and AC parsing on a real story | MVP | 🚧 `python -m app.commands.jira_probe` built, not run on a real site (B-6) |

## 2. UX / UI design

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 2.1 | Collect Mobbin references ([mobbin-references.md](../design/mobbin-references.md)) | MVP | ✅ |
| 2.2 | Brand: blue palette and logo ([design/brand/](../design/brand/)) | MVP | 🚧 logo drafted; current `DSLogo` and blue accepted for MVP (B-14) |
| 2.3 | Mantine 9 setup with the Tessio theme (blue, Geist, sizes), light/dark switch ([ADR 0002](../decisions/0002-ui-library.md)) | MVP | ✅ |
| 2.4 | Custom components Mantine lacks: step editor, traceability matrix, run step timeline, empty states | MVP | ✅ `DSStepEditor`, `DSStepTimeline` (also numbered steps for the case page, editor and manual recording, 2026-11-02), `DSTraceabilityMatrix`, `DSEmptyState` |
| 2.4b | Translations EN / FR / VI with language switcher ([ADR 0003](../decisions/0003-translations.md)) | MVP | ✅ |
| 2.5 | User flows: invite → set password → set up 2FA; sync sprint → write test cases → readiness review → run → assign failure → fix → re-run failed → QC sign-off | MVP | ✅ [user-flows.md](../design/user-flows.md); Mermaid checked by a structural script only (B-16) |
| 2.6 | Wireframes for every screen in section 3 | MVP | |
| 2.7 | High-fidelity mockups (light + dark, desktop + mobile) | MVP | |
| 2.8 | Empty, loading and error states | MVP | ✅ `DSEmptyState`, `DSErrorState`, `DSSkeleton` |

## 3. Client application (feature modules)

### 3.1 App shell & navigation

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.1.1 | Sidebar: Dashboard · Sprints · Stories · Test cases · Runs · Failures · Test data · Members · Settings | MVP | ✅ 9-item project sidebar under `/projects/[projectKey]/…`, items shown by capability |
| 3.1.2 | Top bar: project switcher, search, user menu | MVP | ✅ switcher, notification bell, user menu; search is 3.1.3 (Later) |
| 3.1.3 | Global search (stories, test cases, runs) | Later | |
| 3.1.4 | Responsive / mobile layout | MVP | ✅ sidebar becomes a drawer below tablet |
| 3.1.5 | Light / dark theme switch, choice saved in the profile | MVP | ✅ the Profile page's Preferences card saves `colorScheme` and `language` to `PATCH /api/me`; `SavedPreferencesSync` applies the saved values after sign-in |
| 3.1.6 | Not-found and error pages | MVP | ✅ `client/src/app/not-found.tsx`, `error.tsx`, `global-error.tsx` and the project not-found view (W2.T5). Correction: the earlier ✅ was set while error.tsx and global-error.tsx were still missing |

### 3.2 Authentication & account

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.2.1 | Sign in with email + password (no public sign-up) | MVP | ✅ `/sign-in`; rate limited per IP (SEC-3) |
| 3.2.2 | Accept invite: set password | MVP | ✅ `/invite/[token]`; rate limited per IP (SEC-3) |
| 3.2.3 | Two-factor setup (authenticator app) and recovery codes, required for all | MVP | ✅ `/two-factor/setup` and `/two-factor`, 10 recovery codes; rate limited per IP (SEC-3) |
| 3.2.4 | Forgot / reset password | MVP | ✅ `/forgot-password`, `/reset-password/[token]`; rate limited per IP and per email (SEC-3) |
| 3.2.5 | Profile: name, avatar, password, two-factor (reset own authenticator, regenerate recovery codes), theme, language | MVP | ✅ `/profile`: name, avatar (auto-cropped to a centred square, at most 512 px), password, recovery codes and authenticator reset (both ask for the password; reset goes to `/two-factor/setup?next=%2Fprofile`), theme, language |
| 3.2.6 | "Connect Claude" page: create a personal API token (one project each, shown once, expire within 90 days, revocable) and show the one terminal command that installs the Tessio Claude plugin with it | MVP | ✅ `/connect-claude`: lifetimes 7/30/60/90 days (30 default), the token is shown once inside `claude plugin install tessio --marketplace … --config tessio_url=… --config tessio_token=…` and never stored in the query cache; the marketplace is `<origin>/api/plugin/marketplace.json`, served by the API (ADR 0010), with an HTTPS-only hint on other addresses; revoked and expired tokens stay listed |
| 3.2.7 | Sign out of all devices | MVP | ✅ user menu → confirm → `POST /api/auth/sign-out-all`, clears the query cache and goes to `/sign-in` |
| 3.2.8 | SSO (Google, Microsoft, Atlassian) | Later | |

### 3.3 Projects

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.3.1 | Create project (workspace admins only): name, key, linked Jira project (one-to-one) and Jira board, both picked from dropdowns filled from the Jira connection | MVP | ✅ `/projects/new`; Jira key and board not checked against Jira |
| 3.3.2 | Edit / archive project (archived = read-only, history kept) | MVP | ✅ `/projects/[projectKey]/settings`; archive only for workspace admins |
| 3.3.3 | Project switcher (only projects the user belongs to) | MVP | ✅ top-bar switcher, remembers the last project |
| 3.3.4 | Project members: add workspace users, one role each (Admin, PM, BA, QC, Dev, Viewer) | MVP | ✅ `/projects/[projectKey]/members`; the last Admin cannot be removed or demoted |
| 3.3.5 | Project without Jira: create a project whose stories are written in Tessio, also when no Jira connection is set ([proposal](../discussions/projects-without-jira-proposal.md)) | MVP | ✅ migration 0017; create form choice; `tests/api/stories/test_written_stories.py` |

### 3.3b User management (workspace)

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.3b.1 | User directory: invite, resend invite, deactivate, reactivate | MVP | ✅ `/users` |
| 3.3b.2 | Workspace roles: Owner, Workspace admin, Member | MVP | ✅ `/users` role change; only the Owner manages admins |
| 3.3b.3 | Reset a user's two-factor | MVP | ✅ `/users` row action |
| 3.3b.4 | Per-user view of project access and roles | MVP | ✅ `/users/[userId]`; access lists real memberships only |

### 3.4 Dashboard

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.4.1 | Current sprint: stories by test status, open gaps, open failures | MVP | ✅ `/projects/[projectKey]` with a sprint picker |
| 3.4.2 | Recent runs | MVP | ✅ `/projects/[projectKey]` recent runs table |
| 3.4.3 | "My work" per role (QC: cases to write, Dev: failures to fix, BA: gaps to answer), plus a count of unassigned failures | MVP | ✅ `/projects/[projectKey]` My work panel |
| 3.4.4 | Trend charts across sprints | Later | |

### 3.5 Sprints & user stories (synced from Jira)

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.5.1 | Sprint list and sprint detail | MVP | ✅ `/projects/[projectKey]/sprints` and `/sprints/[sprintId]` |
| 3.5.2 | Story list with test status and Jira link | MVP | ✅ `/projects/[projectKey]/stories` |
| 3.5.3 | Story detail: description and AC (read-only), test cases, gaps, runs | MVP | ✅ `/stories/[jiraKey]` with Overview, Test cases, Gaps, Runs and Traceability tabs |
| 3.5.4 | *Sync from Jira* button, the only time Tessio calls Jira (no automatic sync): last-sync time, "Never synced" and "Syncing…" states | MVP | ✅ sync control on the stories page, `jira.sync_project` job |
| 3.5.5 | QC sign-off: mark story *Passed* / *Failed* | MVP | ✅ story detail; *Passed* refused while failures are active or a run is running |
| 3.5.6 | Dev marks story *Ready for test* | MVP | ✅ story detail, Dev and Admin |
| 3.5.7 | Stories and AC written in Tessio in a project without Jira: create, edit, delete; keys `<KEY>-<n>`; `story.edit` for Admin, PM, BA, QC ([proposal](../discussions/projects-without-jira-proposal.md)) | MVP | ✅ story editor, edit and delete on the story page |

### 3.6 Test cases

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.6.1 | Test case list per story, with filters (status, priority, AC) | MVP | ✅ `/projects/[projectKey]/test-cases` and the story Test cases tab |
| 3.6.2 | Test case editor: business value, preconditions, steps, expected results | MVP | ✅ `/test-cases/new` and `/test-cases/[caseCode]` with `DSStepEditor` |
| 3.6.3 | Link test cases to AC (many-to-many) | MVP | ✅ AC picker in the editor |
| 3.6.4 | Insert test data references (`{{data.key}}`) into steps | MVP | ✅ suggestions in `DSReferenceTextarea`; *Ready* needs known keys |
| 3.6.4b | Test case files: upload, reference in steps (`{{file.name}}`), versioned | MVP | ✅ Files tab; a new file version adds a case version |
| 3.6.5 | Review workflow: Draft → In review → Ready → Deprecated; only *Ready* cases can run | MVP | ✅ status actions in the editor, QC and Admin |
| 3.6.6 | Version history (every save adds a version); each run records the version it executed | MVP | ✅ History tab with *Compare versions*; `run_cases` keep the version |
| 3.6.7 | Import from Google Sheets / CSV (tab = Jira story key) | MVP | 🚧 .xlsx tab = Jira key or .csv with a Story column; column format a guess; no Google Sheets API (B-7, B-9) |
| 3.6.8 | Claude drafts test cases from AC for QC to review (`/tessio:draft-cases`, [proposal](../discussions/claude-drafts-cases-proposal.md)) | Later | 🚧 built ahead of plan: skill `draft-cases` on the 5.8 tools; not tried in a real Claude session |
| 3.6.9 | Claude imports test cases from any file (xlsx, csv, docx, pdf, text, images) as Draft (`/tessio:import-cases`, [proposal](../discussions/claude-drafts-cases-proposal.md)) | MVP | 🚧 skill `import-cases`, `extract_file.py` and the 5.8 tools built and tested; not tried in a real Claude session or on a real QC file (B-7, B-9) |
| 3.6.10 | Read view of a test case for everyone, values shown for `{{data.key}}`, *Edit* switches to the form ([proposal](../discussions/readable-cases-proposal.md)) | MVP | ✅ read view in the Details tab with *Edit*; `/test-data/effective` for values |

### 3.7 Traceability

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.7.1 | AC × test case matrix per story | MVP | ✅ story Traceability tab with `DSTraceabilityMatrix` |
| 3.7.2 | Uncovered-AC warning | MVP | ✅ warning banner on the Traceability tab |
| 3.7.3 | AC pass / fail status from each linked case's latest result (a run without a result for a case keeps the previous one) | MVP | ✅ `/traceability` and `/case-latest-results` read models |
| 3.7.4 | "AC changed, review" flag on linked test cases after a Jira edit; AC removed from Jira kept for history | MVP | ✅ needs-review flag set by the sync, *Mark reviewed* in the editor |

### 3.8 Readiness review (gap questions)

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.8.1 | Gap list per story: type, target (story / AC / case), severity, assignee | MVP | ✅ story Gaps tab |
| 3.8.2 | Automatic routing by type (AC/goal → BA, steps → QC, data → QC/Dev) | MVP | ✅ one member or a role queue, Admin fallback |
| 3.8.3 | Answer and resolve a gap | MVP | ✅ answering resolves; the raiser, QC or Admin can reopen |
| 3.8.4 | Run blocked while any gap is open | MVP | ✅ `OPEN_GAPS_BLOCK_RUN` on every run start |
| 3.8.5 | Gap inbox per user | MVP | ✅ `/gaps` inbox |

### 3.9 Environments & test data

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.9.1 | Environment list (Dev, Staging…) with base URL and health-check URL | MVP | ✅ Environments tab on the Test data page `/projects/[projectKey]/test-data` |
| 3.9.2 | Create / edit environment | MVP | ✅ environment modal on the Test data page, Admin, QC and Dev |
| 3.9.3 | Test data: variables, endpoints, secrets, per project and per environment | MVP | ✅ data grid with project and environment columns |
| 3.9.4 | Secret masking and role-based reveal | MVP | ✅ masked values, reveal with `secret.reveal`, audited |
| 3.9.5 | Import the existing shared data file | MVP | 🚧 .env/JSON/YAML import (B-8) |
| 3.9.6 | "Where used" list for each data key | Later | |
| 3.9.7 | Test data: one description per key, a Secret checkbox instead of three kinds (`endpoint` removed), descriptions shown in suggestions and to Claude ([proposal](../discussions/test-data-descriptions-proposal.md)) | MVP | ✅ migration 0015, `test_data_descriptions`; Secret checkbox and description in the form, grid and import preview; `tests/api/test_data/test_data_descriptions.py` |

### 3.10 Runs

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.10.1 | Run list with status filter | MVP | ✅ `/projects/[projectKey]/runs` |
| 3.10.2 | Run detail: per-case and per-step results with a screenshot for each step, and a "screenshot missing" state | MVP | ✅ `/runs/[runId]` |
| 3.10.3 | Live progress of a Claude run (one update per test case) | MVP | ✅ `/runs/[runId]` refreshed by `run.case_recorded` events |
| 3.10.4 | Manual run: tester records step results and optional screenshots | MVP | ✅ `/runs/new` and `/runs/[runId]/record` with evidence uploads |
| 3.10.5 | Re-run failed only, with link to the original run | MVP | ✅ *Re-run failed* with `parentRunId`; Claude runs show `/tessio:rerun-failed` |
| 3.10.6 | Generated run report (summary, failures, AC impact) | MVP | ✅ Report tab, secrets masked |
| 3.10.7 | Export report (PDF / Markdown) | Later | |
| 3.10.8 | Aborted runs (no activity for 4 hours): shown in the list and the status filter; cases the run never reported keep their previous result | MVP | ✅ `runs.abort_stale` every 15 minutes; *Aborted* in the status filter |
| 3.10.9 | Readable case sheet in runs: preconditions, AC, test data values and the environment URL on the manual recording screen and the run detail; audited secret reveal in a manual run ([proposal](../discussions/readable-cases-proposal.md)) | MVP | ✅ `components/case-sheet` on `/runs/[runId]/record` and `/runs/[runId]`; `POST …/runs/{run_id}/resolve-data` |
| 3.10.10 | Execution log on the run page: Claude's notes and actions per case, input and output, timings and token counts ([proposal](../discussions/execution-log-proposal.md)) | MVP | 🚧 Log tab on Claude runs (`modules/run-log`); not seen on a real Claude run yet |
| 3.10.11 | Why it failed: suspected cause on each failed or blocked case, and a panel with page URL, failed requests and console errors on the failing step; cause in the report and in manual runs ([proposal](../discussions/failure-diagnosis-proposal.md)) | MVP | ✅ `components/step-diagnosis`, `components/suspected-cause`; cause picker on `/runs/[runId]/record` |

### 3.11 Failures

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.11.1 | Failure list: open / fixed / verified / reopened, filter by assignee (including *Unassigned*) | MVP | ✅ `/projects/[projectKey]/failures` |
| 3.11.2 | Failure detail: failed step, screenshot, error, history across re-runs | MVP | ✅ `/failures/[failureId]` with a timeline |
| 3.11.3 | Dev marks *Fixed*; QC marks *Verified* or *Reopened*; a failed result on a *Fixed* failure reopens it automatically | MVP | ✅ status actions on the failure detail; automatic reopen |
| 3.11.4 | Comments on a failure | Later | |
| 3.11.5 | Assign / reassign a failure: Admin, QC or Dev, to any project member; new failures start unassigned | MVP | ✅ assign modal on the list and the detail |
| 3.11.6 | Suspected cause on the failure: shown with the failing step's diagnosis, changeable by Admin, QC or Dev, recorded in the timeline ([proposal](../discussions/failure-diagnosis-proposal.md)) | MVP | ✅ *Suspected cause* card with *Change* on `/failures/[failureId]` |

### 3.12 Notifications

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.12.1 | In-app notifications: gap assigned, failure assigned, run finished | MVP | ✅ notification bell in the top bar, live unread count |
| 3.12.2 | Email / Slack notifications | Later | |

### 3.13 Settings

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.13.1 | Project settings (name, Jira project, defaults) | MVP | ✅ `/projects/[projectKey]/settings`: name, description, board, default environment |
| 3.13.2 | Jira connection, workspace-wide (workspace admins): site URL, a Jira user's email and personal API token (no Jira admin rights needed) | MVP | ✅ `/settings`; no disconnect; tested with mocks only (B-6) |
| 3.13.3 | Notification settings | Later | |
| 3.13.4 | Allowed file types per project | MVP | ✅ allowed file types card in project settings |

### 3.14 Client ↔ API

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 3.14.1 | API types generated from the server's OpenAPI spec (`openapi-typescript`) | MVP | ✅ `export_openapi` + `npm run generate:api` |
| 3.14.2 | Data-fetching layer; replace the mock data in `client/src/shared/data/` | MVP | ✅ react-query hooks on `apiClient`; mock data removed |
| 3.14.3 | Session handling: redirect to sign-in, two-factor step, expired session | MVP | ✅ `SessionGuard` with `next` and `reason=expired` |
| 3.14.4 | Live events client: `/api/events` → refetch the affected data | MVP | ✅ `useLiveEvents` + `LIVE_EVENT_QUERY_KEYS` |
| 3.14.5 | Forward `/api` and `/mcp` to the server in local development (`rewrites` in `next.config.ts`) | MVP | ✅ `client/next.config.ts`; server address from `TESSIO_SERVER_URL` (default `http://localhost:3202`); cookies, JSON errors, SSE and `/mcp` checked through it |
| 3.14.6 | File uploads through signed links (test case files, manual-run screenshots, imports, avatars) | MVP | ✅ `client/src/lib/uploads` (useSignedUpload, useAvatarUpload, runSignedUpload). Bucket CORS is set by the `rustfs-bucket` service with `s3api put-bucket-cors` (dev preflight from `http://localhost:3201` returns Access-Control-Allow-Origin), and compose.prod.yml sets the `https://$TESSIO_DOMAIN` origin (not yet checked on a server). No end-to-end browser upload yet |

## 4. Server (Python + FastAPI, [ADR 0004](../decisions/0004-backend-stack.md), details in the [server proposal](../discussions/server-proposal.md))

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 4.0 | Server skeleton in `server/`: `uv`, `ruff`, `mypy --strict`, `pytest`, `import-linter`, settings, `container.py`, Dockerfile | MVP | ✅ `ruff`, `mypy --strict`, `lint-imports` and `pytest` pass |
| 4.1 | Database schema as SQLAlchemy tables + Alembic migrations ([server proposal §6](../discussions/server-proposal.md#6-database)) | MVP | ✅ migrations `0001`–`0014`, `alembic check` clean |
| 4.2 | Authentication: Argon2id passwords with a breached-password check, required TOTP 2FA and recovery codes, server-side sessions, CSRF (`Origin` check), lockout, invite and reset links | MVP | ✅ all parts in the API, tested on a real Postgres; breached-password check also tried against the real HaveIBeenPwned API; reset flow tried through Next.js, the Redis worker and Mailpit; per-IP rate limits (SEC-3) |
| 4.2b | Authorization: workspace + project roles from one permission table in code, checked on every API and MCP call | MVP | ✅ `app/shared/permissions`, route catalog in `tests/api/security/` |
| 4.2c | MCP API tokens: stored hashed, one project each, 90-day maximum, the owner's current role checked on every call | MVP | ✅ `tsio_` tokens, sha256, 30-day default, 90 max, 10 active |
| 4.3 | REST API for all section 3 modules, with a published OpenAPI spec ([server proposal §7](../discussions/server-proposal.md#7-rest-api)) | MVP | ✅ 108 REST routes + `/mcp`, spec in `client/src/lib/api/openapi.json` |
| 4.4 | Jira sync (read-only, on demand from the *Sync* button): Jira Cloud REST API v3 + Agile API, a Jira user's personal API token, AC parsed from the description document, retry on rate limits | MVP | ✅ `jira.sync_project` job; tested with mocks and a fake Jira only, see 1.7.4 |
| 4.5 | Secret storage: AES-256-GCM encryption, masking in reports and results, access audit log | MVP | ✅ AES-256-GCM v1 with key id, masking, `audit_events` for reveal and resolve |
| 4.6 | File storage via S3 API: RustFS locally ([ADR 0005](../decisions/0005-local-object-storage.md)), production storage to choose ([ADR 0007](../decisions/0007-hosting-vps-docker.md)); signed POST uploads (S3 enforces 20 MB and the type); 5-minute signed downloads; screenshots kept forever, moved to a cheaper storage class after 90 days | MVP | 🚧 `stored_files`, signed POST and 5-minute GET, orphan cleanup; no 90-day lifecycle rule, production storage open (B-5) |
| 4.6b | Email sending (`aiosmtplib`, through the `email.send` job): Mailpit locally, an SMTP provider in production (to choose) | MVP | 🚧 SMTP login + STARTTLS; provider not chosen (B-4) |
| 4.7 | Report generation from run data plus Claude's summary, with secret masking | MVP | ✅ report built on every finish and stale abort, masked with the environment's secret values |
| 4.8 | Real-time updates: server-sent events fed by Redis pub/sub | MVP | ✅ `tessio:events`, filtered per user |
| 4.9 | Notification service | MVP | ✅ `notifications` table, `notification.created` live event |
| 4.10 | Full audit log (secret access is already logged in 4.5) | Later | |
| 4.11 | Background jobs (Redis + BullMQ worker, [ADR 0006](../decisions/0006-background-jobs-redis-bullmq.md)): Jira sync, email, closing stale runs, deleting orphan uploads and expired sessions | MVP | ✅ queues `email`, `jira`, `maintenance`; `runs.abort_stale` every 15 min, `files.delete_orphans` and `sessions.delete_expired` nightly |
| 4.12 | Run and failure rules: open gaps block a run; only *Ready* cases run; a case keeps its previous result when a newer run has none; runs idle for 4 hours are aborted; failures start unassigned and reopen automatically | MVP | ✅ run start gate, one running run per story, stale abort, failure rules in `app/modules/failures` |
| 4.13 | Run log storage: `POST /api/runs/{run_id}/log` after finish, masked again, entries assigned to cases, `run_log_entries` table ([proposal §4](../discussions/execution-log-proposal.md#4-server-wbs-413)) | MVP | ✅ module `run_logs`, migration 0018; `tests/api/runs/test_run_log.py` |
| 4.14 | Failure diagnosis storage: `step_results.diagnosis`, the case result's suspected cause, the failure's cause, `PUT …/failures/{failure_id}/cause` ([proposal](../discussions/failure-diagnosis-proposal.md)) | MVP | ✅ migration `0016`; masked, query strings dropped |

## 5. Claude integration

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 5.1 | Tessio MCP server: story context, gaps, runs, case results (`record_case_result`, one call per case), test data, test case files (`get_test_file`) ([server proposal §8](../discussions/server-proposal.md#8-mcp-tools)) | MVP | ✅ the 9 tools: `start_run`, `record_case_result`, `finish_run`, `get_failed_cases`, `get_story_context`, `resolve_data`, `get_test_file`, `raise_gaps`, `get_open_gaps` |
| 5.2 | Token auth for MCP, scoped to project and role (see 4.2c) | MVP | ✅ `tsio_` bearer token on `/mcp`, project and current role checked per call |
| 5.3 | Migrate existing skills, commands and hooks to call Tessio MCP | MVP | 🚧 new skills `run-story-tests`, `review-readiness`, `rerun-failed`; original team skills not in the repo (B-12) |
| 5.4 | Health check before each run: Claude calls the environment's health-check URL itself (returned by `start_run`) | MVP | ✅ `start_run` returns the health-check URL; `run-story-tests` calls it first |
| 5.5 | Tessio Claude plugin: MCP server, screenshot upload hook and skills in one install; the developer adds only their token | MVP | ✅ `claude/`, served by the API (5.10); the root `.claude-plugin/marketplace.json` stays for local checkouts |
| 5.6 | Screenshot upload hook: after `record_case_result`, fetch one signed upload per case, upload Claude in Chrome's JPEGs as they are (other formats compressed with `sips` / `cwebp`), keep a retry list | MVP | ✅ [claude/hooks/upload_screenshots.py](../../claude/hooks/upload_screenshots.py), setup in [claude-setup.md](../guides/claude-setup.md) |
| 5.7 | Measure tokens per test case on a pilot story, before and after `scale: 0.5` for navigation screenshots | MVP | 🚧 `claude/scripts/measure-tokens.sh` and procedure only (B-10) |
| 5.8 | MCP tools `check_draft_cases` and `create_draft_cases`: the import preview checks on cases Claude sends, then create them as Draft (`test_case.edit`, 100 per call, all or nothing) ([proposal §3](../discussions/claude-drafts-cases-proposal.md#3-mcp-tools-wbs-58)) | MVP | ✅ `modules/test_cases/mcp_tools.py`; `tests/api/test_cases/test_draft_case_tools.py` |
| 5.10 | The API serves the plugin: `GET /api/plugin/marketplace.json` and the zip it points at, built from `claude/` at start-up ([ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)) | MVP | ✅ `modules/plugin`; `tests/api/plugin/`, `tests/unit/plugin/`; served `marketplace.json` and unpacked zip pass `claude plugin validate --strict`; not installed from a real HTTPS host yet (B-3) |
| 5.11 | One plugin version for everyone: the plugin sends `X-Tessio-Plugin-Version` and MCP refuses a missing or older version with `PLUGIN_OUTDATED` | MVP | ✅ checked in `AuthenticateApiTokenUseCase.execute_for_mcp` after the token, once the sent version is saved on it (5.15); plugin 0.2.0 |
| 5.12 | Project rules for Claude in the repository, so every developer's Claude follows the same decisions | MVP | ✅ [CLAUDE.md](../../CLAUDE.md) |
| 5.9 | Plugin skills `import-cases` and `draft-cases`, plus `claude/scripts/extract_file.py` (stdlib xlsx and docx to text) ([proposal §4](../discussions/claude-drafts-cases-proposal.md#4-skills-wbs-59)) | MVP | 🚧 skills and script with unit tests (`test_extract_file.py`, `test_plugin_files.py`); not tried in a real Claude session (B-7, B-9) |
| 5.13 | Log upload hook: after `finish_run`, read the run's slice of Claude Code's session log, mask secrets, drop images, upload once ([proposal §3](../discussions/execution-log-proposal.md#3-the-hook-wbs-513)) | MVP | 🚧 `claude/hooks/upload_run_log.py` with unit tests on a synthetic session log; not tried on a real session; plugin 0.3.0 |
| 5.14 | `run-story-tests` diagnoses the failing step: page URL, console errors, failed requests, suspected cause ([proposal](../discussions/failure-diagnosis-proposal.md)) | MVP | 🚧 skill and `record_case_result` fields built and tested; not tried in a real Claude in Chrome run |
| 5.15 | AI Harness page `/ai-harness` for every signed-in user: the plugin's skills, commands, hooks, MCP server and tools, the server and plugin versions, and the plugin version each of the user's tokens last sent ([proposal](../discussions/ai-harness-proposal.md)) | MVP | ✅ `modules/ai_harness` (`GET /api/ai-harness`), `api_tokens.plugin_version` (migration 0019), capability in each MCP tool's `_meta`; client `modules/ai-harness` and a Plugin column on Connect Claude; [spec](../spec/ai-harness.md); not checked in a real browser (B-13) |

## 6. Quality assurance of Tessio

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 6.1 | Unit tests: client; server with `pytest` and a real Postgres in a test container | MVP | ✅ server `pytest` 1861 tests; client `vitest` 1103 tests in 190 files; plugin hook unit tests |
| 6.2 | End-to-end tests of Tessio | MVP | ✅ Playwright suite in `e2e/` passes locally; `.github/workflows/e2e.yml` never ran (B-1) |
| 6.3 | Permission tests, generated from the permission table: each role (including Viewer) sees and edits only what the matrix allows | MVP | ✅ `tests/permissions/`, `tests/api/security/` |
| 6.4 | Accessibility review | MVP | 🚧 WCAG 2.2 AA fixes, `vitest-axe`; manual keyboard, 200 % zoom and screen-reader passes open (B-13) |
| 6.5 | Security review (secrets, tokens, project isolation) | MVP | ✅ [findings table](#65-security-review-findings-w7t1): 17 fixed, 7 parked |

### 6.5 Security review findings (W7.T1)

| ID | Area | Severity | Finding | Status | Test |
| --- | --- | --- | --- | --- | --- |
| SEC-1 | files | high | Any member, a Viewer included, could get a download link for an import file (for example a .env with secrets) or an avatar. The download route now serves only screenshots, test files, evidence and reports; other kinds give 404. | fixed | `tests/api/files/test_download_kinds.py` |
| SEC-2 | test_data, test_cases | medium | A member with edit rights could preview or commit another member's import file by its id. Imports are now read only by their uploader. | fixed | `tests/api/test_data/test_import_ownership.py`, `tests/api/test_cases/test_import_ownership.py` |
| SEC-3 | auth | high | Sign-in, 2FA, one-time links and forgot-password had no IP rate limit, and reset emails had no cap per address. Fixed-window limits now apply (sign-in, 2FA and links 20 per 15 min, forgot 10 per hour per IP and 3 per hour per email), with 429 `RATE_LIMITED` and `Retry-After`. | fixed | `tests/api/auth/test_rate_limits.py`, `tests/unit/shared/rate_limit/test_redis_rate_limiter.py` |
| SEC-4 | observability | medium | Sentry could receive request bodies (passwords, secret values) and stack locals (decrypted secrets). It now sends neither. | fixed | `tests/unit/shared/logging/test_configure_logging.py` |
| SEC-5 | api | medium | A NUL character in a body, path or query gave 500. Request and tool models now refuse NUL with 422, and the database error 22021 becomes 422 `INVALID_REQUEST`. | fixed | `tests/api/test_cases/test_nul_characters.py`, `tests/api/app/test_nul_in_path.py`, `tests/api/runs/test_tool_nul_characters.py`, `tests/api/app/test_database_errors.py` |
| SEC-6 | test_data | low | A test-data import file with NUL gave 500 on preview or commit. NUL is now stripped on decode, like the case import. | fixed | `tests/api/test_data/test_parsers.py` |
| SEC-7 | runs, api | medium | Two run starts racing on one story gave 500. The race now gives `RUN_ALREADY_RUNNING` (REST and MCP), and any other unique violation gives 409 `CONFLICT`. | fixed | `tests/api/runs/test_concurrent_run_starts.py`, `tests/api/app/test_database_errors.py` |
| SEC-8 | failures | medium | Two failed results for one case racing gave 500. Applying a result now takes a per-case advisory lock first. | fixed | `tests/api/failures/test_concurrent_failed_results.py` |
| SEC-9 | users | medium | Saving a user merged the whole row, so a stale copy could overwrite concurrent changes. Updates now write only the changed columns. | fixed | `tests/api/users/test_user_repository.py` |
| SEC-10 | runs | low | A stale abort and a manual finish did not verify screenshots, so they stayed pending and the report listed none missing. Both now verify inside the locked transaction. | fixed | `tests/api/runs/test_screenshots_on_every_finish.py` |
| SEC-11 | files | low | Completing an upload looked the file up before checking the capability, so a Viewer or an archived project got 404 instead of 403 or 409. The capability is now checked first. | fixed | `tests/api/security/test_viewer_writes.py`, `tests/api/security/test_archived_writes.py`, `tests/permissions/test_require_any.py` |
| SEC-12 | stories | low | Changing a story's test status looked the story up before checking the capability (404 instead of 403 or 409). The capability is now checked first. | fixed | `tests/api/security/test_viewer_writes.py`, `tests/api/security/test_archived_writes.py` |
| SEC-13 | tests | low | A gaps test was flaky because seeded story keys could collide. Seed keys now come from a counter. | fixed | three runs of `tests/api/gaps` |
| SEC-14 | logging | low | Running Alembic in-process disabled every existing logger, which silenced app warnings. Existing loggers now stay on. | fixed | `tests/unit/shared/rate_limit/test_redis_rate_limiter.py` |
| SEC-15 | api | medium | Every REST route (108) and `/mcp` is now classified with its access class and capability, and a test fails on any route nobody classified. Sweeps cover 401, non-member 404, Viewer 403 and archived 409, plus all 9 MCP tools with Viewer, archived, revoked and expired tokens. | fixed | `tests/api/security/` |
| SEC-16 | secrets | medium | Checked that a secret used in results, errors and summaries never shows in plaintext in any response or log. | fixed | `tests/api/security/test_secret_exposure.py` |
| SEC-17 | auth, api_tokens | low | Checked, no change needed: reveal and `resolve_data` are audited, tokens are hashed and re-checked against the current role, the session rotates after 2FA, cookies are HttpOnly, Secure and SameSite=Lax, and the `Origin` check covers every write. | fixed | existing tests in `tests/api/test_data/`, `tests/api/story_context/`, `tests/api/users/`, `tests/api/app/test_origin_check.py` |
| SEC-18 | gaps | medium | Gap text from `raise_gaps` is not masked, because there is no run context. | parked | none |
| SEC-19 | mcp | low | A NUL in a plain string MCP argument (for example the `finish_run` summary) reaches the database and gives a generic tool error with a logged traceback. | parked | none |
| SEC-20 | runs | low | A run that is still running when its project is archived stays running until the stale abort. | parked | none |
| SEC-21 | api_tokens | low | The 10-token limit can be exceeded by one if two creates race. | parked | none |
| SEC-22 | test_data | low | Two environment names that differ only in case, created at the same moment, can both succeed. An exact duplicate now gives 409. | parked | none |
| SEC-23 | jira | low | Jira text containing NUL would fail the sync job at the database, because Jira payloads are not stripped. | parked | none |
| SEC-24 | api | low | A foreign-key violation from a race (23503) still gives 500; only 23505 and 22021 are translated. | parked | none |

## 7. DevOps & deployment

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 7.1 | Git repository and branching strategy | MVP | 🚧 repo, commitlint, [ADR 0008](../decisions/0008-branching-strategy.md) trunk-based; no commits yet (B-1) |
| 7.1b | Docker Compose for local services: Postgres, Redis, Bull Board, RustFS (+ a bucket setup container), Mailpit | MVP | ✅ all five start with `docker compose up -d`; Bull Board at http://localhost:3205; pinned images |
| 7.2 | CI pipeline: server `ruff`, `mypy`, `lint-imports`, `pytest`; client lint, type-check, build | MVP | 🚧 `ci.yml` jobs server, client, commitlint, claude-plugin, docker, deploy; never ran (B-1) |
| 7.3 | Hosting on a rented VPS with Docker Compose (dev, staging, prod; [ADR 0007](../decisions/0007-hosting-vps-docker.md)): `client`, `api`, `worker`, `postgres`, `redis`, a reverse proxy sending `/api` and `/mcp` to `api` | MVP | 🚧 `compose.prod.yml`, `deploy/Caddyfile`, `deploy/deploy.sh`; no VPS (B-3) |
| 7.3b | Database migrations as a one-off `docker compose run` before each deploy | MVP | 🚧 `deploy.sh` runs `alembic upgrade head` one-off; not run on a server |
| 7.4 | Monitoring, logging, error tracking | MVP | 🚧 JSON logs, optional `SENTRY_DSN` without bodies or locals, `/api/health` and `/api/health/ready`; uptime and error-tracking services not chosen |
| 7.5 | Backups and disaster recovery | Later | |

## 8. Documentation & rollout

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 8.1 | User guide per role | MVP | 🚧 [guides/user/](../guides/user/README.md), 27 screenshots missing |
| 8.2 | MCP / Claude setup guide for developers: create a token, `claude mcp add`, install the upload hook and the compression tool | MVP | ✅ [claude-setup.md](../guides/claude-setup.md) |
| 8.3 | Developer docs (this `docs/` folder) | MVP | ✅ stale paths, stack names and SP column names fixed (W8.T4) |
| 8.4 | Pilot: one sprint in parallel with Google Sheets, then retire the sheet | MVP | 🚧 checklist in [pilot.md](../guides/pilot.md); pilot not started (B-10) |

## 9. Competitive features

Accepted by Peter on 2026-11-02: [competitive features proposal](../discussions/competitive-features-proposal.md). Build order, tasks and checks: [build plan](../discussions/competitive-features-plan.md), waves W9 to W15. The proposal's phase is in brackets. W9 starts now, in parallel with go-live. Claude always runs in a person's terminal through Tessio MCP, and there is no runner.

| ID | Work package | Phase | Status |
| --- | --- | --- | --- |
| 9.1 | F1 Regression suites, test plans with sign-off, labels on test cases; open gaps block suite runs (proposal phase 1) | Later | ✅ Labels in W9.T3 ([CASE-13](../spec/test-cases.md#case-13-labels-wbs-91), [SET-5](../spec/settings.md#set-5-labels-wbs-91)). Suites, suite runs and test plans in W10.T1 to W10.T4: modules `suites` and `plans`, migrations 0024 and 0025, suite and plan routes, `start_run(suite=…)` and MCP `get_suite_context`, open gaps on any of the suite's stories block it (`OPEN_GAPS_BLOCK_RUN`), one running run per suite, results by story, plan progress and sign-off (`PLAN_FAILURES_ACTIVE`), the Suites and Plans screens, `/tessio:run-suite`, plugin 0.5.0, e2e `13-suite-run` ([suites-and-plans.md](../spec/suites-and-plans.md)). Not verified: `/tessio:run-suite` in a real Claude Code session; browser pass waits on B-13 |
| 9.2 | F2 Shared steps and data-driven cases (proposal phase 1) | Later | ✅ W10.T5 and W10.T6: module `shared_steps`, migration 0026, shared step routes with versions and usage, `{sharedStepKey}` case steps, parameters and data rows (no literal secrets), the `run_cases.steps` snapshot with shared steps expanded, `iteration` on results (worst iteration counts), the shared step library, the case editor parts, iteration blocks on run detail and manual recording, one `record_case_result` per iteration in the plugin ([CASE-16](../spec/test-cases.md#case-16-shared-steps-and-data-driven-cases-wbs-92), [RUN-14](../spec/runs.md#run-14-shared-steps-and-iterations-in-a-run-wbs-92)). Not verified: a data-driven case run in a real Claude Code session; browser pass waits on B-13 |
| 9.3 | F3 Version compare, review comments, "reviewer must not be the author" setting (proposal phase 1) | Later | ✅ W9.T5: migration 0023, review comment routes, `REVIEW_COMMENTS_OPEN` and `REVIEWER_IS_AUTHOR`, the Review and Compare tabs, the Review settings card ([CASE-15](../spec/test-cases.md#case-15-version-compare-and-review-comments-wbs-93), [SET-4](../spec/settings.md#set-4-reviewer-must-not-be-the-author-wbs-93)). Browser pass waits on B-13 |
| 9.4 | F4 Two-way Jira: Jira bug from a failure, results posted on the story (proposal phase 1) | Later | |
| 9.5 | F5 Insights page and report export to Markdown and PDF; covers 3.10.7 (proposal phase 1) | Later | |
| 9.6 | F6 Email, Slack and Teams notifications, outbound webhooks, `api` token scope, JUnit result import; covers 3.12.2 and 3.13.3 (proposal phase 1) | Later | |
| 9.7 | F7 Google and Microsoft sign-in, full audit log, failure comments; covers 4.10 and 3.11.4 (proposal: any time) | Later | |
| 9.8 | F8 Playwright scripts written by Claude from passing runs, reviewed by QC, repaired with `/tessio:repair-script` (proposal phase 2) | Later | |
| 9.9 | F9 Screenshot comparison against approved baselines (proposal phase 3) | Later | |
| 9.10 | F10 Exploratory sessions run by Claude, with findings (proposal phase 3) | Later | |
| 9.11 | F11 Accessibility and page-speed checks during runs (proposal phase 2) | Later | |
| 9.12 | F12 Picking regression cases from a code diff or labels (proposal phase 3) | Later | |
| 9.13 | F13 Flaky-case detection and quarantine (proposal phase 1) | Later | 🚧 W9.T4: migration 0022, flaky and disagreement recompute (job `test_cases.recompute_flaky` after each result, nightly `test_cases.sweep_flaky`), quarantine routes with history, auto-release after 10 passes, badges, filters and actions ([CASE-14](../spec/test-cases.md#case-14-flaky-cases-and-quarantine-wbs-913)). Missing: quarantine changes nothing in runs until script runs (W13.T4); the nightly schedule never fired on a real worker |
| 9.14 | F14 Steps to reproduce from Claude; Playwright trace and video on failure (proposal phase 2) | Later | |
| 9.15 | F15 Browser and screen-size matrix (proposal phase 2) | Later | |
| 9.16 | F16 API steps in test cases (proposal phase 2) | Later | |
| 9.17 | F17a Script runs started by a person from Claude Code (`/tessio:run-scripts`), with results uploaded by a plugin script (proposal phase 2) | Later | |
| 9.18 | F18 `/tessio:answer-gaps`: Claude helps the person who must answer clear open gaps, with suggested answers and sources; MCP `get_my_gaps`, `answer_gap`, `reassign_gap`, `set_test_data` (proposal phase 1) | Later | 🚧 W9.T1 and W9.T2: migration 0020, the four MCP tools, "via Claude" on answered gaps, the `/tessio:answer-gaps` skill and the shared blocked-run procedure, plugin 0.4.0, e2e `12-answer-gaps` ([GAP-8](../spec/readiness-review.md#gap-8-answer-gaps-with-claude-wbs-918), [DATA-7](../spec/environments-and-test-data.md#data-7-save-missing-test-data-from-claude-wbs-918)). Missing: the dry run in a real Claude Code session (answer two gaps, reassign one, skip one) |

---

## Assumptions & blockers

An assumption is the common real-world default chosen where the spec was silent. A blocker needs a person, account, decision or file from outside the repo.

### Blockers

| ID | Blocker | WBS | What the build assumes now | Needs |
| --- | --- | --- | --- | --- |
| B-1 | CI has never run: there is no git remote and nothing is committed, by decision | 7.1, 7.2, 6.2 | `ci.yml` and `e2e.yml` are written but never ran; every check was run by hand in the shared tree | A remote, the first commit (Peter commits when everything is done) and one green CI run |
| B-2 | Production images not rebuilt since the W1 scratch check | 7.2, 7.3, 4.11 | The api, worker and client Dockerfiles build as checked in W1; the worker scheduler count was not checked on a running worker | Rebuild the images and start the worker once, then check `bull:maintenance:repeat*` |
| B-3 | No VPS, domain, DNS or TLS | 7.3, 7.3b, 7.4 | The deploy job is gated by `vars.DEPLOY_ENABLED`; the production bucket CORS has only been rendered with `docker compose config`; rate limits rely on uvicorn `--proxy-headers --forwarded-allow-ips *` behind Caddy with `api` not published (config checked, not run); staging placement is open | A VPS, a domain and DNS, then one deploy |
| B-4 | SMTP provider not chosen | 4.6b | Generic SMTP with STARTTLS on 587 and a login; Mailpit locally | A provider and its credentials |
| B-5 | Production object storage and the 90-day screenshot rule undecided ([ADR 0007](../decisions/0007-hosting-vps-docker.md)) | 4.6 | RustFS on the VPS, screenshots kept forever, no lifecycle rule | A storage decision and a lifecycle rule |
| B-6 | No real Jira Cloud site checked | 1.7.4, 4.4, 3.13.2 | AC are the first list after an AC heading; all Jira calls tested with mocks and a fake Jira only; on a real site an unknown key gives 400, which maps to `JIRA_UNREACHABLE` | A Jira Cloud site with real stories and a token, then `python -m app.commands.jira_probe` |
| B-7 | No Google Sheets sample | 3.6.7 | Teams download the sheet as .xlsx (tab = Jira key) or .csv with a Story column; no Google Sheets API | A real sample sheet from the team |
| B-8 | No sample of the shared data file | 3.9.5 | The file is .env, JSON or YAML; secret-looking keys become secrets | The real shared data file (with dummy secrets) |
| B-9 | The xlsx case-import column format is a guess | 3.6.7 | A header row with title and action columns, plus optional columns | A sample sheet to confirm the columns |
| B-10 | No pilot people and no pilot sprint | 8.4, 5.7, 8.1, 1.4 | The pilot checklist, the token measurement script and the user guide exist; the 27 guide screenshots and the NFR [ASSUME] measurements wait for the pilot | A pilot lead, a team and one sprint |
| B-11 | Closed on 2026-11-01: the API serves the plugin itself ([ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)) | 5.5, 5.10, 3.2.6 | The install command uses `<origin>/api/plugin/marketplace.json` | Only the production HTTPS address (B-3) |
| B-12 | The original team skills are not in the repo | 5.3 | New skills written from the server proposal (`run-story-tests`, `review-readiness`, `rerun-failed`) | The old skills, to migrate their wording |
| B-13 | No manual pass in a real browser against a running stack | 6.4, section 3 | Automated tests (jsdom, axe) cover the screens, and the Playwright e2e suite checks in Chromium that 17 screens have no horizontal scroll at 375 px and that the focused-input border has enough contrast in light and dark; not checked: 200 % zoom, the skip link, VoiceOver and NVDA, a real QR scan, real uploads to RustFS, live SSE updates | One full manual pass on a running stack |
| B-14 | Final brand, wireframes and mockups | 2.2, 2.6, 2.7 | The current `DSLogo` and Tessio blue are accepted for MVP | A designer's final brand and screens |
| B-15 | No backups | 7.5 | Backups are Later; a manual daily Postgres dump is the minimum before go-live | A dump job and one restore test |
| B-16 | Mermaid diagrams not parsed by mermaid-cli | 2.5 | The diagrams in user-flows.md pass a structural script only | One run of `@mermaid-js/mermaid-cli` |

### Planning assumptions

| WBS | Question | Assumption |
| --- | --- | --- |
| **1.7.4** | The AC format on real stories is not verified. | AC are the first list after an AC heading, matched by position, so an AC inserted in the middle flags the later ones. The `jira_probe` command is built and must be run on a real site (B-6). |
| **2.2** | The brand is marked "logo drafted". | The current `DSLogo` and `TESSIO_BLUE` are accepted for MVP; the final brand is pending (B-14). |
| **3.1.6** | The row was marked ✅ while `error.tsx` and `global-error.tsx` were missing. | Both were built in W2.T5 and the status was corrected. |
| **3.2.3** | Which QR library to use, and how to use `@mantine/form`. | `qrcode.react` wrapped as `DSQrCode`; `@mantine/form` only through the DS `useDSForm`. |
| **3.2.5** | Avatar limits and where avatars are stored. | PNG, JPEG or WebP up to 2 MB, cropped square on the client, uploaded through the files module (`POST /api/me/avatar-upload`) under `users/{id}/avatar/{fileId}`. |
| **3.2.6** | Token defaults and the plugin marketplace source. | 30 days by default, 90 at most, 10 active per user, membership checked at create, Viewer tokens read-only; the marketplace is the one the API serves (ADR 0010, which closed B-11). |
| **3.3.1** | The project key format, and creating a project without Jira. | The key matches `^[A-Z][A-Z0-9]{1,9}$` and never changes. Without a Jira connection, create is refused with a call to action. The Jira dropdowns call Jira directly. |
| **3.3.4** | The last project admin, and who the member picker lists. | The last Admin cannot be removed or demoted. The picker lists active and invited workspace users. |
| **3.3b.2** | Who manages admins, and ownership transfer. | Only the Owner manages admins. Nobody can deactivate the Owner or themselves. Ownership transfer is Later. |
| **3.4.1** | Several sprints can be active at once. | The dashboard shows the one with the latest start and offers a sprint picker. |
| **3.4.3** | Test cases have no assignee. | QC "to write" means uncovered AC plus the user's own draft and in-review cases. |
| **3.5.7** | How to store a story written in Tessio in a table built for Jira stories. | The `jira_*` columns stay required and get placeholders (`jira_id` = `tessio:<id>`, empty URL and status, issue type "Story"), and `source` says where the story came from. This differs from the proposal (nullable columns) and keeps every reader, MCP tool and screen working unchanged. The description is stored as a one-paragraph-per-line document so the existing renderer shows it. A story with test cases, runs or gaps cannot be deleted. |
| **3.10.10, 4.13, 5.13** | Where the log lives, how entries map to cases, and where failed uploads wait. | A separate module and tables (`run_logs`, `run_log_entries`) instead of new `runs` columns, so the runs code is untouched. Setup ends at the first browser action; each case ends at its `record_case_result`. Failed uploads wait in their own folder `~/.tessio/pending-run-logs/`, because the screenshot hook rewrites `pending-uploads.jsonl` with only its own lines. The run page shows the log in a Log tab grouped by case, not under each case's steps. |
| **3.5.4** | The permission table leaves QC and Dev out of sync. | Follow the table: Admin, PM and BA can sync. |
| **3.5.5** | The sign-off rules. | QC or Admin signs off from *In test*, or switches between *Passed* and *Failed*. *Passed* is refused while failures are active or a run is running. A new run resets the story to *In test*. |
| **3.5.6** | Whether *Ready for test* gates runs. | It does not. Dev and Admin can set it. |
| **3.6.2** | Priority values, the case code format and code concurrency. | Priorities are critical, high, medium and low. Codes are `TC-<n>` per project from a counter table. A case belongs to one story. |
| **3.6.4b** | The scope of a file key. | Unique per case. A new file version adds a case version. |
| **3.6.5** | The review rules. | Any QC or Admin can review, their own cases included. Editing keeps the status. *Ready* needs steps and known references. |
| **3.6.7** | The Google Sheets format is unknown, and there is no Google sign-in. | An uploaded .xlsx (tab = Jira key) or a .csv with a Story column (B-7, B-9). |
| **3.6.8, 3.6.9** | Where Claude drafts or imports cases, and how far it is trusted. (Decided with Peter on 2026-11-01.) | In Claude Code through the plugin, never on the server (no API key). Every created case is Draft, so QC reviews it. The server re-checks every case with the import preview rules. The web import stays. 3.6.9 is MVP because it takes the guessed column format off the pilot's path; 3.6.8 stays Later. |
| **5.8** | Batch size and partial failure for `create_draft_cases`. | 100 cases per call, all or nothing: one case with a problem refuses the call. Duplicates are allowed once the user confirms them, as in the web import. |
| **5.9** | Reading xlsx and docx in Claude Code, and secrets found in a file. | A standard-library script turns xlsx and docx into text, because Claude Code reads PDF, images and text but not Office files. Secret-looking values become `{{data.key}}` and are never sent to Tessio. |
| **3.8.2** | Routing when several members or none match, and deactivated users. | Several matches go to a role queue, none goes to Admin, and deactivated users are never assigned. Claude passes `dataScope=environment` for data gaps. |
| **3.8.3** | Answering versus resolving. | Answering resolves the gap. The raiser, QC or Admin can reopen it. Every role except Viewer can raise gaps in the UI. Severity is high, medium or low. |
| **3.9.1** | Who manages environments. | Admin, QC and Dev, on the Test data page. |
| **3.9.5** | The shared data file format is unknown. | .env, JSON or YAML; secret-looking keys become secrets (B-8). |
| **3.11.3** | Verify from open, blocked results, and a failure after verify. | Verify only from *Fixed*. A blocked result opens no failure. After *Verified*, a new failed result opens a new failure; a pass changes nothing. |
| **3.12.1** | Who gets *run finished*. | The person who started the run plus the project's QC members. |
| **3.13.4** | The default allowed file types differ between reports. | PNG, JPEG, WebP, GIF, PDF, TXT, CSV, JSON, DOCX and XLSX; screenshots are always allowed. |
| **3.14.1** | There was no published OpenAPI spec, and error codes were missing from the schema. | An export command writes `openapi.json` with `ErrorResponse` and `ErrorCode` added; `openapi-typescript` generates the client types from that file. |
| **4.2b** | Workspace admins' rights inside projects are not defined. | They act as project Admin everywhere, secret reveal included; this was flagged for the security review (6.5). |
| **4.2b** | The layers make tokens, permissions and users depend on each other. | One layer order: users, auth, projects, then files, audit and notifications, then api_tokens, jira and test_data, then stories, test_cases, gaps, runs, failures, then story_context and insights, then live_events and health. User management lives in auth. |
| **4.4** | The sync scope and the sync status values. | Active and future sprints plus sprints closed in the last 30 days, without epics and sub-tasks. Sync states are never, queued, running, succeeded and failed. |
| **4.5** | The ciphertext had no key id. | A version byte, key id, nonce and ciphertext; dev data was re-created. |
| **4.6** | Production storage and the 90-day rule are undecided ([ADR 0007](../decisions/0007-hosting-vps-docker.md)). | RustFS on the VPS with no lifecycle rule; screenshots under `projects/{pid}/screenshot/{caseResultId}/` (B-5). |
| **4.6b** | No SMTP provider is chosen. | Generic SMTP with STARTTLS on 587 and a login (B-4). |
| **4.7** | What masking covers. | Mask against every secret value of the run's environment, which also covers manual runs. |
| **4.12** | Concurrent runs, skipped and blocked steps, and runs with zero results. | One running run per story. Unreported steps count as skipped. All skipped counts as passed. A skipped result does not replace the latest result. A run with zero results ends aborted. |
| **4.12** | Columns and tables missing from the server proposal's schema. | Added `run_cases`, `run_files`, `runs.last_activity_at` and `abort_reason`, the `needs_review_*` columns, `gaps.assignee_role`, `stories.jira_missing_at`, `project_sync_states` and `test_case_counters`. |
| **5.1** | Where `get_test_file` records the file version. | In a `run_files` table (run, test file version, key). |
| **5.3** | The original team skills are not in the repo. | New skills written from the server proposal (§8, §10); the old wording is migrated later (B-12). |
| **5.7** | Measuring needs a pilot story and Claude in Chrome. | Only the procedure and `measure-tokens.sh` exist; the row stays open (B-10). |
| **6.1** | The client had no test runner. | vitest with Testing Library; the e2e suite uses Playwright in its own `e2e/package.json`. |
| **7.1** | No branching strategy written, and no commits. | Trunk-based with `feat/<wbs-id>-<slug>` branches and squash merges ([ADR 0008](../decisions/0008-branching-strategy.md)); no commits until Peter says the build is done (B-1). |
| **7.2** | There is no GitHub remote. | GitHub Actions workflows are written but never ran (B-1). |
| **7.3** | No VPS, domain or remote. | `compose.prod.yml` and Caddy checked locally; the deploy job is gated; Bull Board is not public (B-3). |
| **8.4** | The pilot needs people and a sprint. | Only the checklist exists; the row stays open (B-10). |
| **9.1–9.18** | Which competitive features to build, and how. | Peter, 2026-11-02: all of them, except the runner (dropped). The [proposal](../discussions/competitive-features-proposal.md) holds the design and the [build plan](../discussions/competitive-features-plan.md) the order. Tessio stays one company, one workspace. Claude stays in a person's terminal, because Peter tried unattended Claude with an API key and with a plan token and neither worked as expected. A suite run is blocked by any open gap on its stories. |

### Implementation assumptions

Each bullet is one behaviour, rule, limit, default, permission, error code or data format chosen during the build, with the task that chose it. "PRE", "POST" and "fix" mark the wave integrator and fixer steps.

#### 1.3 Functional spec per feature module

- Where the code and the proposals differ, the specs follow the code: a case holds at most 100 steps, a recorded case takes at most 200 step results, QC and Admin can call `resolve_data` too, and onboarding ends at `/`. (W7.T3)

#### 1.4 Non-functional requirements

- NFR-PERF-01 and NFR-PERF-02 [ASSUME]: at pilot scale, API reads have a p95 under 300 ms and writes under 800 ms (Jira calls excluded); not measured. (W7.T3)
- NFR-PERF-03 and NFR-PERF-04 [ASSUME]: a live event reaches open browsers within 2 s, and the `record_case_result` reply is about 30 tokens with images sent as file paths; not measured (5.7). (W7.T3)
- NFR-COMPAT-01 [ASSUME]: Tessio supports the latest two versions of Chrome, Edge, Firefox and Safari. (W7.T3)
- The accessibility target is WCAG 2.2 AA. (W7.T3)
- Storage estimate [ASSUME]: with the 46 KB screenshot from spike 1.7.2, a pilot team (10 stories × 6 cases × 8 steps × 2 runs) adds about 44 MB per sprint and a larger team (30 × 10 × 10 × 3) about 414 MB per sprint, at 26 sprints a year. (W7.T3)

#### 1.7.4 Spike: Jira search and AC parsing

- `jira_probe` reports a search that finds no issue with that exact key as `NOT_FOUND`; on a real site an unknown key gives HTTP 400, which the Jira client maps to `JIRA_UNREACHABLE`. (W3.T1)

#### 2.4 Custom components

- A clearable `DSSelect` also shows the clear button. (W1.T5a)
- `DSQrCode` is one labelled image at error level M with a 2-module white quiet zone; it has not been scanned with a real authenticator app (B-13). (W1.T5a)
- `DSCopyButton` shows Copy and Copied on hover and on keyboard focus, and announces the copied state through a hidden status text. (W1.T5a, W1 fix)
- Each digit of `DSPinInput` is named "{label}, digit {n} of {total}" in EN, FR and VI. (W1 fix)
- `DSStepEditor` stacks into one column on narrow screens and limits each text to 5000 characters. (W5.T5)
- `DSReferenceTextarea` keeps the textbox role with list autocompletion, because axe forbids a combobox role on a textarea. (W5.T5)

#### 2.4b Translations EN / FR / VI

- The FR and VI texts for `errors.api.*` and the navigation labels are the integrator's own translations. (W1 PRE)
- An error code the client does not know shows the generic error text, never a raw key. (W1.T4)

#### 2.8 Empty, loading and error states

- `DSAlert`, `DSErrorState` and `DSImage` require an accessible label exactly when their close, retry or zoom control is shown. (W1.T5b)
- Danger menu items use the danger text token, because Mantine's red-6 text is below 4.5:1 on white. (W1.T5b)
- Drawers are 320, 480 or 720 px wide, full width below tablet, with a sticky footer. (W1.T5b)
- `DSErrorState` is announced as an alert, and loading wrappers use `role="status"` with `aria-busy`. (W1.T5b, W2.T5)

#### 3.1.1 Sidebar

- The 9 sidebar items are Dashboard, Sprints, Stories, Test cases, Runs, Failures, Test data, Members and Settings, shown by capability. (W1 PRE)
- The sidebar holds navigation only; language and theme live on the Profile page's Preferences card (reached from the user menu), not on the admin-only workspace Settings page, so every role can change them. (fix)

#### 3.1.2 Top bar

- The search box is a disabled placeholder until global search (3.1.3, Later). (W2.T5)

#### 3.1.6 Not-found and error pages

- An unknown project key always shows the project not-found view; any other error shows the error state only when no project is cached, so a failed background refetch keeps the page. (W2.T5)

#### 3.2.1 Sign in with email + password

- A `next` redirect target with ASCII control characters is refused, because browsers would turn it into an open redirect. (W2.T4)
- A `/me` error other than 401 shows a retryable error state instead of an endless loader. (W2.T4)
- A half-signed-in session gets 200 from `/api/auth/me` with `nextStep` set to `two_factor_setup_required` or `two_factor_required`. (W1 PRE)

#### 3.2.2 Accept invite: set password

- After the invite is accepted the user goes to `/two-factor/setup`, with no `next=/` parameter. (W2.T4)

#### 3.2.3 Two-factor setup and recovery codes

- The setup page never redirects away while the recovery codes are on screen. (W2.T4)
- `TWO_FACTOR_SETUP_NOT_STARTED` on confirm restarts setup with a new QR code; a lost session goes to sign-in with `reason=expired`. (W2.T4)

#### 3.2.5 Profile

- The avatar is cropped to a centred square of at most 512 px in its source format. (W3.T4)
- Own-account writes re-read and lock the user row; if the user was deactivated in the meantime, the write fails with 401. (W2 fix)
- Change password checks the current password against the session's copy of the user, then writes only the new hash. (W2 fix)

#### 3.2.6 Connect Claude page

- The install command quotes only the values for the shell, and `tessio_url` is the browser's origin. (W3.T4)
- The project picker lists non-archived projects only, and a Viewer sees a read-only hint. (W3.T4)
- New tokens and recovery codes leave the mutation cache as soon as the dialog resets. (W3.T4)

#### 3.2.7 Sign out of all devices

- Sign out clears the query cache and goes to `/sign-in`, also when the session had already ended (401). (W2.T4)

#### 3.3.1 Create project

- A non-admin without a role on the linked project gets 403 on the boards list, and an archived project gives `PROJECT_ARCHIVED`. (W2.T3)

#### 3.3.2 Edit / archive project

- Name and description are trimmed; a blank description is stored as empty, PATCH with `""` clears it, and an omitted or null field leaves it unchanged. (W1.T1)
- Archive and unarchive are idempotent; archiving again keeps the original `archived_at`. (W1.T1)
- The archive card shows only to workspace admins, because archiving needs `project.archive`. (W7.T4)

#### 3.3.3 Project switcher

- Switching project keeps the current section; sections outside the project sidebar go to the new project's overview. (W2.T5)

#### 3.3.4 Project members

- A deactivated user cannot be added or have their role changed (`USER_DEACTIVATED`), but can be removed. (W1.T1)
- The member picker searches name and email with LIKE wildcards escaped, sorted by name then email, 20 results at most. (W1.T1)
- The role select shows the chosen role while saving, then the server's value; on an error it falls back to the server's value. (W3.T5)
- A member change publishes `project.members_changed`, so open streams refresh their project access at once. (W1 POST)

#### 3.3b.1 User directory

- The invite form uses the server's email pattern (a dot in the domain is required) with a 320-character limit. (W3.T3)
- User search escapes LIKE wildcards, a blank query means no filter, and the search text is cut at 100 characters. (W2.T2, W3.T3)
- Resending an invite to a user who already accepted gives `USER_NOT_INVITED`. (W2.T2)
- Reactivating a user who never accepted expires any leftover invite links before a new one is sent. (W2.T2)
- Deactivating a user revokes all their API tokens at once. (W2.T2)

#### 3.3b.2 Workspace roles

- Nobody can be invited as Owner or promoted to Owner (`OWNER_ONLY`); ownership transfer is Later. (W2.T2)

#### 3.3b.4 Per-user view of project access

- A non-admin on `/users/[userId]` sends no requests, and a 404 shows only the not-found state with a link back to `/users`. (W3.T3)

#### 3.4.1 Current sprint

- The dashboard sprint scope leaves out stories that are missing from Jira. (W5.T4)
- An unknown or foreign sprint id gives 404 on the dashboard, My work and story progress. (W5.T4)

#### 3.4.3 "My work" per role

- Draft cases, failures to fix and gaps to answer are project-wide; uncovered AC come from the current or chosen sprint, and the list is empty without a sprint. (W5.T4)
- "View all" shows only when a list has items; failures link to the project's failures and gaps to `/gaps`. (W6.T5)

#### 3.5.1 Sprint list and sprint detail

- A sprint id that is not a UUID sends no request and shows the not-found view, like a 404 or 422. (W4.T3)

#### 3.5.2 Story list

- The story list includes stories missing from Jira, while sprint story counts leave them out. (W3.T1)
- When the URL changes from outside the page while the search box holds unsent text, the URL wins for the other filters. (W4 fix)

#### 3.5.3 Story detail

- Jira heading levels are ranked from the top level down, so a description that starts at level 2 still has a valid heading order. (W4.T3)

#### 3.5.4 Sync from Jira button

- A queued or running sync with no start or queue time counts as stale and can be requested again. (W4.T3)
- The sync status refetches every 5 s while a sync runs. (W4.T3)

#### 3.5.5 QC sign-off

- Only *Mark passed* is blocked by active failures (Open, Fixed or Reopened) or a running run; *Mark failed* is not, so a *Fixed* failure must be verified before *Mark passed*. (W7.T4)
- A test status change needs the target status's capability even when the status does not change. (W7.T1)

#### 3.5.6 Dev marks story Ready for test

- Starting any run moves the story to *In test* from any status; a *Failed* story returns to *Ready for test* through *Mark ready for test*. (W7.T4)

#### 3.6.1 Test case list

- The story filter is upper-cased and trimmed; a query shaped like `TC-<n>` filters by number, anything else matches the title. (W4.T1)

#### 3.6.2 Test case editor

- A case's code is `TC-<number>`, built from the per-project number; no code column is stored. (W4 PRE)
- Title, story key and step action are trimmed, and a blank value gives 422 `INVALID_REQUEST`. (W4 fix)
- Clearing business value or preconditions sends an empty string; null means no change. (W4.T1, W5.T5)
- A step's order is always rewritten to its list position. (W4.T1)
- There is no leave-page guard; switching tabs keeps unsaved edits, and saving on top of a newer version gives `CONFLICT` with a reload alert. (W5.T5)

#### 3.6.3 Link test cases to AC

- AC codes match case-insensitively against the story's current AC. (W4.T1)
- `INVALID_REQUEST` without field errors on save shows "This AC cannot be linked". (W5.T5)

#### 3.6.4b Test case files

- Attaching a file is blocked while the Details form has unsaved edits. (W5 fix)
- An oversized test file reaches the upload check and shows "file too large" instead of being dropped silently. (W5.T5)

#### 3.6.7 Import from Google Sheets / CSV

- A sheet needs a title column and an action column; otherwise an .xlsx tab is skipped and a .csv is refused with `IMPORT_INVALID_FILE`. (W4.T1)
- Duplicates (same story and title, ignoring case, in the file or already saved) are flagged but can still be imported. (W4.T1)
- Story keys from tab names or the Story column are upper-cased. (W4.T1)
- NUL characters in imported cells are stripped silently. (W4 fix)

#### 3.6.9 Claude imports test cases from any file (with 3.6.8, 5.8, 5.9)

- `check_draft_cases` returns `case_count`, `creatable_count` and only the cases with an issue, so a clean file of 100 cases costs a few tokens. `create_draft_cases` returns only the new codes, in input order. (3.6.9 build)
- Both tools need `test_case.edit`, so both are refused on an archived project, the check included, like the web import preview. (3.6.9 build)
- A case needs a title, at least one step and a `source`; text lengths and step counts are not validated on input, so they come back as `text_too_long` or `too_many_steps` problems instead of failing the whole call. (3.6.9 build)
- AC codes go through the import's `AC2` / `AC-2` / `AC 2` reader; any other code is kept upper-cased and reported as unknown, never dropped silently. (3.6.9 build)
- The import plan and case creation are shared with the web import (`load_case_import_plan` takes a list of cases; `create_imported_case` in `utils/imported_case_creation.py`). (3.6.9 build)
- `extract_file.py` shows a line break inside a cell as `⏎` and a `|` as `\|`, repeats merged cells, marks hidden sheets and refuses files over 5 MB, 100 MB unpacked or 5000 rows. (3.6.9 build)
- The import skill runs the script as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/extract_file.py`, which Claude Code substitutes in plugin skills and pre-approves through `allowed-tools`. (3.6.9 build)

#### 3.7.3 AC pass / fail status

- Criterion impact ignores deprecated cases, and a run case without a result counts as run but not failed. (W5.T4)
- Story progress always includes stories missing from Jira, so it joins the story list. (W5.T4)

#### 3.7.4 "AC changed, review" flag

- *Mark reviewed* on an unflagged case changes nothing, and flagging skips deprecated cases. (W4.T1)
- A link to a removed AC still shows in the traceability data. (W5.T4)

#### 3.8.1 Gap list per story

- Gap targets match leniently (`ac2` matches AC2, case codes ignore case); a removed AC cannot be targeted, but older gaps still show its code. (W4.T2)

#### 3.8.2 Automatic routing by type

- When one member matches, the gap goes to that person; several matches give a role queue; reassigning to a user clears the role and the other way round. (W4.T2)
- Gaps of type *Other* go to Admin. (W7.T4)
- The raiser is not excluded from routing; if they are the only match they get the gap but no notification. (W4.T2)
- Viewers cannot be assignees, and a reassign names exactly one user or one role. (W4.T2, W5.T6)

#### 3.8.3 Answer and resolve a gap

- If answering or reassigning fails with `GAP_NOT_OPEN`, or reopening with `INVALID_STATUS_TRANSITION`, the dialog shows the message, closes and reloads the lists. (W5.T6)
- A Viewer has no `gap.raise`, so a Viewer is never a gap's raiser and cannot reopen one. (W7 fix)

#### 3.8.4 Run blocked while any gap is open

- The open-gap check takes no lock, so a gap raised during `start_run` can race (MVP). (W4.T2)

#### 3.8.5 Gap inbox per user

- Workspace admins who are not project members can raise, answer and reopen gaps but are never auto-assigned, and their inbox skips the Admin queues of those projects. (W4.T2)

#### 3.9.2 Create / edit environment

- An archived environment can still be renamed, and archiving clears the project default. (W2.T6)
- Environment names are unique per project ignoring case; an exact duplicate gives 409 (SEC-22). (W2.T6)

#### 3.9.3 Test data

- Rows of an archived environment can be updated or deleted, but not created or imported (422). (W2.T6)
- Update and delete check `test_data.edit` first, so a Viewer gets 403, not 404. (W2.T6)
- *Override* keeps the inherited item's kind, so a Dev cannot override a secret with a plain variable. (W3.T6)
- If the environments fail to load, only the All environments column shows. (W3 fix)

#### 3.9.4 Secret masking and role-based reveal

- A revealed secret is hidden again when its item is updated or deleted and when the Data tab unmounts. (W3.T6)
- Without `secret.edit` the Secret kind is disabled in the item form and left out of the import preview. (W3.T6)

#### 3.9.5 Import the existing shared data file

- The format is detected from the file name, ignoring case, so `.ENV.Production` is .env. (W2.T6)
- Empty values, YAML dates, nulls and lists are skipped as `unsupported_value`. (W2.T6)
- In .env files only whitespace or a `#` comment may follow a closing quote, an unterminated quote is `invalid_line`, and unknown escapes in double quotes are kept as they are. (W2.T6)
- The 1 MB limit is checked on the stored size and again on the bytes read. (W2.T6)
- If a commit sends the same key twice, the last kind wins. (W2.T6)
- .env and .yaml files upload as `text/plain` with the upload kind `import`. (W2.T6)
- NUL characters are stripped on decode. (W7.T1)
- Import files, for test data and test cases, can be previewed and committed only by the member who uploaded them (SEC-2). (W7.T1)

#### 3.10.1 Run list

- A 404 from the run list with a story filter shows "no runs match" with *Clear filters*. (W6 fix)

#### 3.10.2 Run detail

- A case that turns failed or blocked expands by itself. (W6.T1)
- The screenshot check accepts only .jpg, .jpeg, .webp or .png keys named after the step order; other uploads stay missing. (W5.T1a)
- A screenshot still pending after the run finished shows as missing. (W6 fix)

#### 3.10.3 Live progress of a Claude run

- Progress counts the cases with a result out of all cases, and the Report tab is disabled while the run is running. (W6.T1)

#### 3.10.4 Manual run

- A tester can record only a status; steps not reported are saved as skipped. (W5.T1b)
- A step with no status shows as *Not reported*, which also lets the tester un-mark a step. (W6.T2)
- Error text is saved only for failed or blocked steps. (W6.T2)
- Text fields take 4000 characters, a case takes 200 step results, and a duration is at most 24 hours. (W5.T1b)
- Evidence from an unknown file, another project, another kind or another uploader gives 422; a pending file gives `UPLOAD_NOT_COMPLETED` (409). (W5.T1b)
- Switching to another case cancels its running uploads, while text drafts stay. (W6.T2)
- Only the person who started the run can record it, and errors show inline. (W6.T2)

#### 3.10.5 Re-run failed only

- A re-run takes the parent's failed and blocked cases in run order. (W5.T1b)
- The environment defaults to the parent's while it is active, then the project default, then the only active environment. (W5.T1a, W5.T1b)
- `NO_FAILED_CASES_TO_RERUN` is decided before the story lock and the open-gap check (a tiny race, MVP). (W5.T1a)
- For a Claude run, *Re-run failed* shows the `/tessio:rerun-failed` command, and Admin and QC also get *Re-run manually instead*. (W7.T4)

#### 3.10.8 Aborted runs

- A stale abort keeps `last_activity_at` and sets the status aborted, the reason `inactive`, no summary and a partial report; a finish with zero results ends aborted with `no_results`. (W5.T1b, W5 PRE)
- The stale-abort loop stops on a short batch, or on a full batch that aborted nothing. (W5.T1b)

#### 3.11.1 Failure list

- *All statuses* is a broader view, not a filter; only a single status, an assignee or a story counts as a filter. (W6.T3)
- The assignee filter takes only a UUID from the URL and lists every member, invited and deactivated included. (W6.T3)

#### 3.11.2 Failure detail

- The screenshot polls every 5 s only while the failed step's screenshot is pending. (W6.T3)
- An *Unassigned* event keeps the previous assignee, and an event with no actor reads *Automatic*. (W5.T3, W6.T3)

#### 3.11.3 Fixed, Verified, Reopened

- A status change that lost a race shows "changed meanwhile" and reloads. (W6.T3)
- An automatic reopen sends no notification, because only `failure_assigned` exists. (W5.T3)

#### 3.11.5 Assign / reassign a failure

- Dev has `failure.assign` and `failure.mark_fixed`; QC has `failure.assign` and `failure.verify`. (W6.T3)
- If the current assignee is deactivated, the picker starts on *Unassigned* and saving unassigns the failure. (W6.T3)

#### 3.12.1 In-app notifications

- Notification text is trimmed and cut to 200 characters with an ellipsis. (W3.T2)
- The actor gets no `gap_assigned` for their own action, while `run_finished` also goes to the starter. (W4.T2, W5.T1a)
- A notification kind from a newer server falls back to the project link and name instead of crashing. (W4.T4)

#### 3.13.1 Project settings

- The default environment card shows `UNKNOWN_REFERENCE` on the field and reloads the options. (W3.T5)

#### 3.13.2 Jira connection

- The site URL must be a DNS host name; default ports are dropped and other ports kept. (W2.T3)
- The email is trimmed and lower-cased, and the URL and token are checked before Jira is called. (W2.T3)
- A stored token that cannot be decrypted gives `JIRA_NOT_CONFIGURED` (409, "Connect Jira first.") instead of 500. (W2.T3)
- The token is required on first setup or when the normalised site URL changes. (W3.T5)
- Two first-time saves at the same moment could race; this is accepted for a rare admin action. (W2.T3)

#### 3.13.4 Allowed file types per project

- The list keeps its order without duplicates, holds 1 to 50 types, and each type is at most 255 characters. (W1.T1)
- Content types are lower-cased with parameters stripped, on requests and on the project list. (W1.T3)

#### 3.14.1 API types generated from OpenAPI

- Fields with a server default, such as `defaultEnvironmentId`, are optional in the generated types. (W2 POST)

#### 3.14.2 Data-fetching layer

- A failed query toasts once per distinct error, and a refetch that fails again toasts again. (W1.T4)
- `useGetEnvironments` turns off the global error toast, because every caller shows an inline error. (W3 fix)

#### 3.14.3 Session handling

- `SessionGuard` shows its error state only when `/me` never loaded; a later failure keeps the cached user, and a 401 always redirects with `reason=expired`. (W2.T4)

#### 3.14.4 Live events client

- The client listens to every event type and reconnects on `online` only when no stream is open. (W2.T4)
- Signed download links (failure screenshots, run files) are not refreshed by live events, because they have their own lifetime. (W6 POST)

#### 3.14.6 File uploads through signed links

- The client posts the signed fields as they are, including the key and content type the server returns. (W1.T3, W1 POST)
- A cancel after completion still returns the stored file, and a second upload's cancel cannot overwrite the new one. (W2.T7)
- In production, bucket CORS goes through Caddy to RustFS, and Caddy is assumed to pass RustFS's CORS headers unchanged. (W2 POST)

#### 4.2 Authentication

- Rate limits are per client IP in fixed windows and fail open when Redis is down. (W7.T1)
- The per-email forgot-password counter counts every request, and the reply is still 204, so it never shows whether the address exists. (W7.T1)
- Behind Caddy the API runs uvicorn with `--proxy-headers --forwarded-allow-ips *` and `api` is not published, so the limits see the real client IP. (W7.T1)

#### 4.2b Authorization

- Workspace owners and admins signed in with a session act as project Admin in every project, even with a lower project membership; API tokens get only the real membership role. (W1.T1, W1 fix)
- A missing capability gives 403 before an archived project's 409 `PROJECT_ARCHIVED`. (W1.T1)
- Project capabilities are listed in a fixed order for the client. (W1.T1)
- Completing an upload checks any upload capability before the lookup, then the capability for the file's kind. (W7.T1)

#### 4.2c MCP API tokens

- Token names are trimmed to 1 to 100 characters, and the limit message reads "You already have 10 active tokens. Revoke one first." (W2.T1)
- Tokens can be created only from a signed-in session, not with another token. (W2.T1)
- The token list is newest first, and the status is computed when the response is built, with Revoked winning over Expired. (W2.T1)
- Recording a token's last use never overwrites a concurrent revoke. (W2.T1)

#### 4.4 Jira sync

- `Retry-After` takes whole or decimal seconds or an HTTP date; a past value means no wait, and an unreadable one falls back to 1, 2 and 4 s; credentials are never logged. (W2.T3)
- Paging stops on an empty page or `isLast`; a missing `isLast` ends project, board and sprint pages, and search continues while `nextPageToken` is present. (W2.T3)
- Jira calls time out after 5 s to connect and 20 s otherwise. (W2 POST)
- AC heading markers match ignoring case and accents form, with the typographic apostrophe read as a plain one, so "Critères d’acceptation" matches. (W3.T1)
- Among sprints of equal rank, the first one seen keeps the issue, and a closed sprint with no end date is never in scope. (W3.T1)
- Stored sprints that fell out of scope are refreshed but never inserted. (W3.T1)
- A failed sync keeps `started_at` and sets `finished_at`; a successful one also sets `last_succeeded_at`. (W3.T1)
- Sync runs only when someone starts it; there is no schedule. (W7.T4)

#### 4.5 Secret storage

- New ciphertexts always use the v1 format with a key id; old ciphertexts have no fallback, so dev 2FA secrets made before W1 need a redo. (W1.T3)
- A secret encrypted with a key that is no longer in the key ring gives 500 on reveal, preview, commit and read. (W2.T6)
- `resolve_data` writes its audit rows in the same transaction as the read. (W5.T2)

#### 4.6 File storage via S3 API

- Each signed upload is bound to one exact sanitised object key, so one pending row maps to one object. (W1 fix)
- Within the 15-minute policy the uploader can overwrite the same key after completion; the 20 MB cap and the type still apply, but the stored size can go stale. (W1 fix)
- Completion re-reads the object's content type and deletes the object on a mismatch with `FILE_TYPE_NOT_ALLOWED`. (W1.T3)
- Completion re-checks the upload capability, and screenshot and report files cannot be completed over REST. (W1.T3)
- The original file name is kept for display and download; the object key uses a sanitised name, with `file` as the fallback. (W1.T3)
- Only screenshots, test files, evidence and reports can be downloaded (SEC-1). (W7.T1)

#### 4.6b Email sending

- SMTP supports STARTTLS or TLS with a user name and password; Mailpit locally needs neither. (W1.T3)

#### 4.8 Real-time updates

- Each API process keeps one Redis subscription and listens again after a Redis error; events published while it is down are lost (best effort, no replay). (W1.T2)
- If Redis is down when a browser subscribes, that request fails and the browser retries. (W1.T2)
- `run.case_recorded` carries the story id, a re-run's `run.started` carries `parentRunId`, and `story.changed` is published on every run start. (W5.T1a, W5.T1b)

#### 4.9 Notification service

- Notifications are sent after the caller's transaction commits. (W3.T2)

#### 4.11 Background jobs

- The worker runs one BullMQ worker per queue: `email`, `jira` and `maintenance`. (W1.T2)
- `files.delete_orphans` runs daily at 03:00, `sessions.delete_expired` at 03:30 and `runs.abort_stale` every 15 minutes. (W1 POST, W2.T2, W5.T1b)

#### 4.12 Run and failure rules

- The environment is resolved before the cases, so an environment error comes before `OPEN_GAPS_BLOCK_RUN` or `RUN_ALREADY_RUNNING`. (W5.T1a)
- Environment names match ignoring case and surrounding spaces, and a named archived environment gives `UNKNOWN_REFERENCE`. (W5.T1a)
- Manual results may leave out the duration, and step results can carry an evidence file. (W5 PRE, W5.T1a)
- The `run_finished` notification uses the starter as its actor, so the starter receives it too. (W5.T1a)

#### 5.1 Tessio MCP server

- Tool errors read "Error executing tool <name>: <CODE>: <message>", and the skills branch on the code after that prefix. (W2.T1)
- `get_story_context` counts only draft and in-review cases in `other_case_count`; deprecated cases are left out. (W5.T2)
- Replies leave out null, empty and false fields, but keep integers such as 0. (W5.T2)
- `get_test_file` gives `NOT_FOUND` for no match, `INVALID_REQUEST` for several versions, and `NOT_FOUND` for a file not yet uploaded; the signed URL is made after the commit. (W5.T2)
- `resolve_data` trims and de-duplicates keys and allows only the data keys of the run's case versions; other keys come back as `unknown_keys`, so nothing shows whether they exist. (W5.T2, W5 fix)
- `get_test_file` records the file version per run, case and key in `run_files`. (W5 PRE)
- An empty or oversized `raise_gaps` list is refused by MCP argument validation. (W4.T2)

#### 5.2 Token auth for MCP

- `/mcp` and the screenshot upload route accept only `tsio_` API tokens, never a session token. (W2.T1)

#### 5.3 Migrate existing skills to Tessio MCP

- `run-story-tests` maps case codes to case ids from `get_story_context` before calling `start_run`. (W1.T7)
- The skills use snake_case tool arguments, and `raise_gaps` takes a `data_scope`. (W1.T7)

#### 5.5 Tessio Claude plugin

- The plugin reads `CLAUDE_PLUGIN_OPTION_TESSIO_URL` and `CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN`, with `TESSIO_*` variables as the fallback. (W1.T7)
- The marketplace sits at the repo root and points at `./claude`; the plugin has no licence, icon or privacy URL, and `plugin validate --strict` passes. (W1.T7)

#### 5.10 and 5.11 The API serves the plugin, one version for everyone

- Both plugin routes are public and left out of the OpenAPI document: the plugin holds no secrets, and the token is entered at install. (5.10 build)
- The zip is built in memory when the API starts, from `TESSIO_PLUGIN_DIR` (the repo's `claude/` by default, `/app/plugin` in the image). It leaves out `tests/`, `__pycache__`, `.pyc` and `.DS_Store`, uses fixed timestamps and keeps the executable bit, so its sha256 is the same on every start. A missing or invalid `plugin.json` stops the API at start-up. (5.10 build)
- The archive URL in `marketplace.json` is built from `CLIENT_URL`, the public address. The zip is cached for a year (its name holds the version); `marketplace.json` is `no-cache`. (5.10 build)
- The version check needs `MAJOR.MINOR.PATCH` and compares by number; a newer plugin than the server's is accepted, so the plugin can be released before the API. `PLUGIN_OUTDATED` maps to HTTP 426 for REST, though only MCP uses it. (5.11 build)
- The screenshot-upload REST route used by the hook does not check the plugin version: the hook ships inside the plugin, and refusing an upload would lose evidence. (5.11 build)

#### 5.15 AI Harness page

- The route is `GET /api/ai-harness` in a new top-layer module `ai_harness`, not under `/api/plugin`: the `plugin` module is in the lowest import layer and can't use the session check. (5.15 build)
- The token is now checked before the plugin version, so an outdated plugin's version can be saved and shown. An unknown token now gets `INVALID_API_TOKEN` instead of `PLUGIN_OUTDATED`. "Last used" is refreshed even when the call is then refused for an old plugin or a missing capability. (5.15 build)
- The server version is `TESSIO_SERVER_VERSION`, or else the `version` in `server/pyproject.toml`; `TESSIO_BUILD_COMMIT` is optional and no image sets it yet. (5.15 build)
- "AI Harness" is a product name and stays in English in French and Vietnamese. (5.15 build)

#### 5.6 Screenshot upload hook

- The hook reads the case result id from the first content block only. (W1.T7)
- The pending upload list lives under `~/.tessio`; invalid lines and steps without an integer order are skipped. (W1.T7)
- A 4xx on the signed-upload request is not retried; network errors, 5xx and replies without `url`, `keyPrefix` or `fields` stay in the retry list, with no cap. (W1.T7)
- On invalid input the hook prints one line and exits 0 without retrying; missing settings print a message naming both variable sets. (W1.T7)

#### 5.7 Measure tokens per test case

- `measure-tokens.sh` marks a row as an error when `claude` exits non-zero or its JSON cannot be parsed, and still saves the raw output with a UTC timestamp. (W1.T7)

#### 6.2 End-to-end tests of Tessio

- The e2e users sign in with addresses on the reserved `.test` domain, because the client email check needs an alphabetic top-level domain; the fake Jira account uses `example.com`, because the server's Jira email check rejects special-use domains. (W8.T1)
- The e2e seed refuses any database whose name does not end in `_e2e` and exits with code 2. (W8.T1)
- The two-factor code input submits itself on the sixth digit, so the tests never click Confirm as well, which would trip the code replay guard. (W8.T1)
- Where the screen text differs from the spec wording (blocked sign-off message, the gap block on New run, the manual re-run dialog), the tests assert what the screen shows. (W8.T1)
- The phone-layout check measures each screen once the network is idle and nothing is busy, and reports every screen that scrolls sideways in one run. (W8.T1)
- The focused-border check waits for transitions to end before it reads colours; the date input is not covered. (W8.T1)
- The suite runs one worker in file order and stops at the first failure; `E2E_REUSE_STATE=1` re-runs one spec on the data of an earlier run. (W8.T1)
- The table scroll wrapper is the containing block for visually hidden labels, so they no longer widen the page at 375 px (E2E-BUG-1). (W8 POST)
- The acceptance criterion code badge on the story detail keeps its width when the criterion text wraps (E2E-BUG-2). (W8 POST)

#### 6.3 Permission tests

- A route counts as a project write when a Viewer lacks its capability, so the member list, candidates and secret reveal are writes; token create is a session route and the boards list a workspace route. (W7.T1)
- The archived sweep leaves out reveal, archive and unarchive, each with its reason recorded. (W7.T1)

#### 6.4 Accessibility review

- Text and badges need 4.5:1 contrast, and input borders and focus outlines 3:1; a token-level unit test guards contrast, because jsdom axe cannot measure it. (W7.T2)
- Every password visibility toggle and every table wrapper is a Tab stop. (W7.T2)
- Menus focus their first item when they open. (W7.T2)
- Modals and drawers mounted already open return focus to their trigger on close. (W7.T2)
- The full-page not-found and error screens have an h1; the `/` redirect screen has none. (W7.T2)
- The reduced-motion reset uses `!important`, so it also wins over inline transitions. (W7.T2)
- Focused inputs use Mantine's focus border in the primary colour. (W7 fix)

#### 7.1 Git repository and branching strategy

- Branch names carry the WBS id (`feat/3.4.1-sprint-list`); a squash merge needs a review and every CI job green; rollback deploys an earlier SHA and never rolls back migrations. (W1.T6)

#### 7.1b Docker Compose for local services

- Images are pinned to exact tags as of 2026-11-01: postgres 17.11-alpine, redis 8.10.3-alpine, rustfs 1.0.4, aws-cli 2.39.3, caddy 2.11.7-alpine, node 24.22.2-alpine3.24, Mailpit v1.27.11 and bull-board 3.4.15. (W1.T6)

#### 7.2 CI pipeline

- The docker job pushes images only on a push to `main`, and deploy also needs a push event, so a manual run never deploys an unpushed SHA. (W1.T6)
- Pull request values and SSH secrets go through environment variables, and deploy has a non-cancelling concurrency group. (W1.T6)

#### 7.3 Hosting on a rented VPS

- Production storage uses `http://rustfs:9000` inside the network and a public storage domain behind Caddy for signed links, so nothing depends on hairpin DNS. (W1.T6)
- `.env` is optional for `docker compose config`, but missing values still stop the run, and `deploy.sh` exits when `.env` is absent. (W1.T6)
- A shared VPS cannot run a second Caddy, so staging domains would go into the production Caddyfile; a separate staging VPS is still open. (W1.T6)

#### 7.4 Monitoring, logging, error tracking

- JSON logs drop uvicorn's colour field, and setting up logging twice still leaves one handler. (W1.T6)
- Running Alembic in-process no longer silences app loggers (SEC-14). (W7.T1)

#### 8.1 User guide per role

- The guide is English only, PM and BA share one page, and screenshots are named placeholders. (W7.T4)
- The **Versions** button belongs to test files; case versions are compared on the History tab. (W7.T4)

#### 8.2 MCP / Claude setup guide

- The main install path is the one-step `claude plugin install tessio --marketplace <marketplace> --config ...`; the two-step `marketplace add` route is kept for older Claude Code versions. (W8.T2)
- The marketplace host is not decided, so the guide keeps a `<marketplace>` placeholder, as the Connect Claude page does. (W8.T2)
- Plugin options are stored once per plugin, so one install works on one project at a time, and switching project means configuring a new token. (W8.T2)
- Only macOS and Linux (including WSL) are supported, because the upload hook needs python3 plus sips or cwebp. (W8.T2)
- If Claude Code does not pass the token to hooks, the fix is the `TESSIO_URL`/`TESSIO_TOKEN` env block in `~/.claude/settings.json`. (W8.T2)
- The manual setup without the plugin has no skills, because the skills name the plugin's tool prefix. (W8.T2)
- The manual `claude mcp add` example uses user scope and warns against project scope. (W8.T2)
- Rotating a token means creating a new one for the same project, configuring it, then revoking the old one. (W8.T2)
- The guide is English only and screenshots are named placeholders. (W8.T2)

#### 8.3 Developer docs

- The server proposal's module table lists health under operations (7.4) and users under 3.2 and 3.3b, because the spec index names neither module. (W8.T4)
- The docs index links the release plan from the product/ row. (W8.T4)
- The MCP bearer value is described as a `tsio_` API token, which the plugin sends as a Bearer header. (W8.T4)
- The documented hook matcher is the plugin-prefixed name from `claude/hooks/hooks.json`. (W8.T4)
- The proxy-header item from W7 is closed by documentation: the server image already trusts forwarded headers, and the API is reachable only through Caddy. (W8.T4)
- The ADR template's superseded placeholder is plain text, so the docs link check passes. (W8.T4)

#### 9 Competitive features: wave W9 integration

- W9 has no runnable spike: S1 to S7 belong to W11, W12, W14 and W15, so none was run. (W9.PRE)
- No `GAP_NOT_ASSIGNABLE_HERE` error code: `ReassignGapUseCase` already refuses a non-member or Viewer with `ASSIGNEE_NOT_ACTIVE_MEMBER` and another project's gap with `NOT_FOUND`, and the MCP `reassign_gap` reuses it. (W9.PRE)
- `REVIEWER_IS_AUTHOR` is 403, like `RUN_NOT_OWNED`, because the refusal is about who the actor is; `REVIEW_COMMENTS_OPEN` is 409, like the other state conflicts. (W9.PRE)
- `labels` is its own import layer, directly below `test_cases` and above `stories`, so `test_cases`, `gaps`, `runs`, `failures`, `story_context` and `insights` may import it and it never imports them. Its router was registered in `main.py` by PRE. (W9.PRE)
- Live events `label.changed` and `review_comment.changed`; a case's labels, quarantine, the flaky recompute and the review rules reuse `test_case.changed`. (W9.PRE)
- Jobs `test_cases.recompute_flaky` (one case) and `test_cases.sweep_flaky` (the nightly sweep, because a `JobSchedule` carries no data) run on the existing `maintenance` queue. (W9.PRE)
- Translation namespaces `labels`, `flakyCases` and `caseReview`; the "via Claude" answer badge reuses the `gaps` namespace. Icons `label`, `flaky`, `quarantine`, `comment` and `compare` were added to `DS_ICONS`. W9 adds no sidebar entry. (W9.PRE)
- The test container records jobs in `RecordingJobQueue` (`server/tests/support/`), so no test reaches the dev Redis; worker job tests use the testcontainer Redis. (W9.PRE)
- The parallel tasks checked their migrations on their own throwaway databases (`tessio_migcheck_<task>` or a testcontainer Postgres) so they would not drop each other's `tessio_migcheck`; POST ran the official check on `tessio_migcheck`. The dev database `tessio` was never touched. (W9.T1, W9.T3, W9.T4, W9.T5)
- The plugin went from 0.3.0 to 0.4.0 (minor: a new skill and new MCP tools). The server takes its required version from `claude/.claude-plugin/plugin.json`, so MCP calls from a 0.3.x plugin get `PLUGIN_OUTDATED`. (W9 POST)
- The e2e spec `12-answer-gaps` creates a Dev API token through `POST /api/me/api-tokens` with the Dev's session, calls `get_my_gaps` and `answer_gap` on `/mcp` with the plugin version read from `plugin.json`, checks `isAnsweredViaClaude` over REST and the "via Claude" badge on the story's Gaps tab, then revokes the token. It uses SHOP-2, so the SHOP-1 flow of specs 05 to 09 is unchanged. (W9 POST)
- `GET_LABELS_KEY` stays on `label.changed` only: when someone else changes a case's labels (`test_case.changed`), the "Used by n cases" counts in the label manager refresh on the next fetch, not live. Adding the key to `test_case.changed` would refetch the labels list after every case change. (W9 POST, from W9.T3)

#### 9 Competitive features: wave W10 integration

- W10 has no runnable spike: S1 to S7 belong to W11, W12, W14 and W15, so none was run. (W10.PRE)
- No `GAPS_OPEN` error code: a suite run blocked by open gaps gets the existing `OPEN_GAPS_BLOCK_RUN` (409), which the skills and the client already handle; `when-gaps-block.md` now says so. (W10.PRE, W10.T4)
- Import layers: `plans` above `suites`, `suites` above `story_context | insights` (so above `runs`), and `shared_steps` beside `labels` directly below `test_cases`. `runs` reads suites only through its `SuiteRunScopeReader` port, implemented in `suites` and wired in `container.py`; run list, run detail and the insights read models get the suite name through their own SQL. (W10.PRE, W10.T1)
- Suite names are unique without case among a project's active suites (`SUITE_NAME_ALREADY_USED`), because `/tessio:run-suite <name>` finds a suite by name; plan names need not be unique. (W10.PRE)
- Error codes reserved and used: `SUITE_ALREADY_RUNNING`, `SUITE_EMPTY`, `SUITE_NAME_ALREADY_USED`, `SUITE_ARCHIVED`, `PLAN_FAILURES_ACTIVE`, `PLAN_NOT_OPEN` (409); `SHARED_STEP_KEY_ALREADY_USED` (409); `UNKNOWN_SHARED_STEP`, `INVALID_STEP_SHAPE`, `SECRET_IN_DATA_ROW`, `ITERATION_OUT_OF_RANGE` (422). Specific codes, not `INVALID_REQUEST`, so Claude and the client can explain the problem. The `SECRET_IN_DATA_ROW` message avoids a literal `{{data.key}}`, which i18next would interpolate away. (W10.PRE)
- Closing a plan needs `plan.edit`; `signed_off` and `closed` plans refuse edits with `PLAN_NOT_OPEN`. The plan's "`plan.signed_off` event" is a live event of that name (W11 webhooks subscribe to the Redis live events), published with `plan.changed`. (W10.PRE)
- Reads: Suites and Shared steps use `test_case.view`, Plans `report.view`, MCP `get_suite_context` `run.view`; every role holds them. The sidebar order is Test cases, Shared steps, Suites, Runs, Plans, Failures. (W10.PRE)
- Translation namespaces `suites` (including the suite strings on run screens and manual run creation), `plans`, `sharedSteps` and `dataRows`. (W10.PRE)
- T1 creates `docs/spec/suites-and-plans.md` and its index row; T3 adds the Plans part. (W10.PRE)
- The parallel tasks checked their migrations on their own throwaway databases (`tessio_migcheck_<task>`); POST ran the official check on `tessio_migcheck`. The dev database `tessio` was never touched. (W10.T1, W10.T3, W10.T5 and their reviews)
- Live refresh added by POST, as the T2 and T3 reviews asked: `test_case.changed` also refreshes the suites list, suite detail and plan detail, and `suite.changed` the plan detail. (W10 POST) W10.FIX added the plans list to `test_case.changed` and `suite.changed`, and the plans list and plan detail to `story.changed`, because the list's counts come from the plans' suites and stories. (W10.FIX)
- The plugin went from 0.4.0 to 0.5.0 (minor: a new skill, a new MCP tool, `start_run(suite=…)` and `record_case_result(iteration=…)`). The server reads its required version from `claude/.claude-plugin/plugin.json`, so a 0.4.x plugin gets `PLUGIN_OUTDATED`. (W10 POST)
- 9.1 and 9.2 are ✅ although `/tessio:run-suite` and the per-iteration recording were never tried in a real Claude Code session: no W10 "Done when" item asks for that run, and the run rules say a missing real-system run alone doesn't make a task 🚧. It is named as "Not verified" in the rows and in the M13 exit criterion. (W10 POST; W9 POST set 9.18 to 🚧 because its dry run was a Done-when item)
- The e2e spec `13-suite-run` labels TC-1 `regression` from the case page, creates the suite "Checkout regression" and fills it with Add by filter, raises a gap on SHOP-1 for the Dev, sees the manual suite start refused with the open-gaps message, lets the Dev answer on `/gaps`, opens the plan "Release 1.0" on the suite, runs the suite by hand (SHOP-1 stays *Passed*), and signs off the plan at 1 of 1 passed. It runs through the UI only, no MCP. (W10 POST)

#### 9.1 Labels (W9.T3)

- `PUT …/test-cases/{case_code}/labels` and `SetTestCaseLabelsUseCase` live in `test_cases`, which calls the `labels` repositories; `labels` never imports `test_cases`, and `test_case_labels.test_case_id` names its FK by table name. (W9.T3)
- That PUT returns the case's labels as `[{id, name, color}]`, sorted by name, not the whole case; the case detail and every case-list row carry `labels`. (W9.T3)
- Colours are a fixed palette of 8 names (`gray` by default, `red`, `orange`, `yellow`, `green`, `teal`, `blue`, `violet`), not hex values. `DSBadge` gained `orange`, `teal`, `blue` and `violet`, each with a `--color-<colour>-text` token; their AA contrast was not measured with a tool. (W9.T3)
- Names are trimmed, 1 to 40 characters and unique per project without regard to case, checked in the use case; a duplicate gets the existing `CONFLICT` (409). The database constraint `UNIQUE(project_id, name)` is case-sensitive, as for environments. (W9.T3)
- A label of another project or an unknown id in the PUT gets `INVALID_REQUEST` (422); on PATCH and DELETE it gets `NOT_FOUND`. At most 20 ids per request (repeats count), and the case-list `label` filter takes at most 20 names. (W9.T3)
- The `label` filter takes names, repeatable, AND, trimmed and matched without case; an unknown name matches nothing. (W9.T3)
- Labels are not versioned and can change in any status, Deprecated included. (W9.T3)
- The label manager card is in project settings, which only `project.edit` (Admin) sees. QC (`test_case.edit`) creates labels from the case's label picker, but renames, recolours and deletes only through the Admin's card. (W9.T3)
- No labels MCP tool in W9: labels show in `get_story_context`, and `list_cases(filter)` comes in W14. (W9.T3)
- Spec numbers: CASE-13 and SET-5. (W9.T3)
- The picker is a "Labels" box on the case page's Details tab, outside the versioned case form. The New case page has no picker. It saves on an explicit "Save labels" (one PUT, nothing when unchanged). "Create and add" creates the label in `gray`, or picks an existing label with that name in any case. (W9.T3)
- A label name in the URL that matches no label is kept and shown as its own filter option. The filter is hidden while the project has no labels and none is chosen. The UI says "Color", as in "Color theme". (W9.T3)

#### 9.1 Suites and suite runs (W10.T1, W10.T2, W10.T4)

- A label can be deleted while suites hold its cases: Add by filter is a one-shot fixed list and no filter is stored, so the plan's "refuse while a suite filter uses the label" doesn't apply; the suite keeps its cases (CASE-13 AC4, SUITE-3 AC5). (W10.T1)
- A suite run's run-finished notification is a new kind, `suite_run_finished` (`runId`, `testSuiteId`, `testSuiteName`, outcome, counts); `run_finished` keeps its shape. Migration 0024 widens the `notification_kind` check. The bell wording is in `notifications.json` (`kind.suiteRunFinished`). (W10.T1, W10.T2)
- Skip reasons: a case that isn't `ready` is `not_ready`, a Ready case flagged Needs review is `needs_review`. They are stored on the run (`runs.skipped_cases`, JSONB, in 0024), so the report keeps them after the suite changes. (W10.T1)
- Open gaps on any story with a case in the suite block it, skipped cases included. The message lists up to 20 gaps (story key, gap id, assignee name, role or "nobody", question cut to 120 characters). (W10.T1) When the message ends with "; and N more", `when-gaps-block.md` takes the candidate stories from the suite context (`stories[].key` and `skipped_cases[].story_key`) and calls `get_open_gaps` for each, and it always takes severity, target and a deactivated assignee from the `get_open_gaps` / `get_my_gaps` replies, never from the message (GAP-6 AC4; the exact message format is in SUITE-4 AC2). (W10.FIX)
- `start_run` takes `suite` as a name (without case) or an id; exactly one of `story_key` and `suite` is needed, so `story_key` is optional in the tool schema. A name used only by an archived suite gives `SUITE_ARCHIVED`, not `NOT_FOUND`. (W10.T1)
- `start_run(suite, case_ids=[…])` runs chosen cases of the suite in that order and lists nothing as skipped; `/tessio:run-suite` uses it for its 50-case batches. (W10.T1, W10.T4)
- A suite run and a story run don't block each other; each one-running-run rule applies to its own kind of run. (W10.T1)
- A suite run's AC impact lists only the active ACs a case of the run is linked to, grouped by story; a story's last run in story progress is the newest run that ran one of its cases. (W10.T1)
- The API's `RunExecutor` stays `claude` and `manual`; the database accepts `script` and `ci` since 0024 (one migration of `runs`), and W11 (`ci`) and W12 (`script`) add them to the API. (W10.T1)
- Limits: suite name 1 to 120 characters, description up to 2000, at most 1000 cases per suite, 20 labels per filter, MCP suite reference 1 to 200 characters (in `get_suite_context`, and since W10.FIX in `start_run.suite` too, `MAX_SUITE_REFERENCE_LENGTH` in the runs module). Filters: `labels` by name, all must match; `priorities` any; `storyKey` and `sprintId` narrow; they combine; deprecated cases never match; at least one filter. (W10.T1)
- `get_suite_context` needs `run.view` plus `story.view`, `test_case.view` and `test_data.view`, like `get_story_context`, and reuses `story_context`'s JSON builders, which T1 made public (renames only). (W10.T1)
- Archiving is one-way and idempotent; a suite run in progress keeps running. (W10.T1)
- New response fields (`testSuiteId`, `testSuiteName`, `skippedCases`, the report's `stories`, the case `story*` fields) have defaults, so the generated client types mark them optional. (W10.T1)
- Story sign-off's running-run check (`PostgresRunningRunChecker`) counts a story run of the story and a running suite run that holds a case of the story (a `run_cases` row whose case belongs to the story), so either blocks `Mark passed` with `STORY_SIGN_OFF_BLOCKED`; a running suite run without a case of the story doesn't (SUITE-7 AC7, STORY AC3). Raised by the T1 review; the T1 review's recommendation was taken, not decided by Peter. (W10.T1 review, W10.FIX)
- Drag to reorder is a new design-system component, `DSSortableList`, on native HTML5 drag and drop with no new dependency: drag by the handle, arrow keys on the handle, and *Move up/down/to the top/to the bottom* in the row menu. Each move saves at once with `PUT …/cases`; moves during a save are queued, and a refused save puts the server's order back. (W10.T2)
- A manual suite run with every runnable case checked sends `{suiteId, environmentId}` without `testCaseIds`, so the run keeps its skipped cases; with some left out it sends `testCaseIds` and lists nothing as skipped. The case labels show the story key, because `SuiteCaseResponse` has no step count. (W10.T2)
- The manual suite run page doesn't list the open gaps before the start (no "gaps of a suite" read exists); the refusal shows a translated message pointing at the stories and `/tessio:answer-gaps`. (W10.T2)
- On the run list, the Story and Suite filters exclude each other; the Suite filter lists archived suites as "(archived)" and is hidden while the project has no suite. (W10.T2)
- The copyable command quotes a name with a space (`/tessio:run-suite "Checkout regression"`) and uses the suite id when the name has a double quote. (W10.T2, W10.T4)
- T2 overwrote PRE's French `suites.json` page text without reading it first; the current French `page.title` and `page.description` are T2's translation of the English. (W10.T2, noted by its review)
- `/tessio:run-suite` arguments: a quoted name or an id, an unquoted first word is the suite, and after `NOT_FOUND` the whole argument text is tried once as the name; `TC-<n>` words are case codes, another word is the environment. The environment is the argument, else the context's `is_default` one, else the only one, else Claude asks, and the same one is used for every batch. (W10.T4)
- Batches of at most 50 follow the `get_suite_context` order (stories in order, then each story's cases). `case_ids` are passed only when more than one run is needed or the user gave case codes; follow-up runs start on their own, one after the other after each `finish_run`. When the skill stops early it prints the command for the rest. On `CASE_NOT_READY` or `UNKNOWN_REFERENCE` for a case it reloads the context and retries once. With more than three blocked stories it calls `get_my_gaps()` once. (W10.T4) On `UNKNOWN_REFERENCE` naming an environment (archived since the context was loaded) it reloads the context, lists its environments, asks which to use for this and every later batch, and retries; with no environment left it stops (SUITE-8 AC6). (W10.FIX)
- `rerun-failed` re-runs a suite run with `start_run(suite=…, parent_run_id=…)` as one linked child run when it has 50 failed or blocked cases or fewer. With more (a large manual suite run), it keeps only the failed cases still in the suite context's `stories[].cases`, reports the dropped codes, and, if more than 50 are left, runs them in batches of at most 50 with `start_run(suite=<id>, environment, case_ids=…)`, one after the other, without a parent link (`start_run` refuses `case_ids` with `parent_run_id`); each `finish_run` summary names the parent run (SUITE-8 AC8). A story run's re-run stays one run. (W10.T4, W10.FIX)
- Skills link bundled files with relative markdown links, as `run-story-tests`, `rerun-failed` and `draft-cases` already do; `${CLAUDE_PLUGIN_ROOT}` stays for script paths. (W10.T4 review)

#### 9.1 Test plans (W10.T3)

- States: `open -> signed_off -> closed` and `open -> closed`; closed is final, and a signed-off plan keeps its sign-off when closed. `PLAN_NOT_OPEN` covers PATCH, `PUT …/items` and sign-off on a signed-off or closed plan, and close on a closed plan. (W10.T3)
- "Since the plan opened" means since `test_plans.created_at`; a plan never reopens. A signed-off plan counts results up to `signed_off_at`, one closed without sign-off up to `closed_at`; failures and gaps always show today's state. (W10.T3)
- The plan's environment, when set, keeps only results of runs on it (an active environment of the project, else `UNKNOWN_REFERENCE`); `null` means any environment. (W10.T3)
- A case's latest result uses the traceability rule (the newest result from any run, `skipped` only when there is no other), with the worst iteration of a data-driven case, whatever order the iterations were recorded in (PLAN-3 AC4; a test since W10.FIX). (W10.T3, W10.T5, W10.FIX)
- The plan's cases: suite cases in suite order, then story cases by case number, following item order, each case once (first place wins); deprecated cases left out; Draft, In review and Needs-review cases kept. Blocker gaps are the open gaps of every story with a case in the plan, plus every story item. (W10.T3)
- Only active failures (`open`, `fixed`, `reopened`) on the plan's cases block sign-off; open gaps, cases not run, running runs and an empty plan don't. (W10.T3)
- An archived suite can be a plan item and stays, with its frozen cases. Extra columns: `test_plans.closed_by`, `closed_at`, `test_plan_items.position`; limits: name 1 to 120, description up to 2000, 100 items. (W10.T3)
- Progress is part of `GET …/plans/{plan_id}` (no separate route); the list carries `counts` and `itemCount`. Items take `{"suiteId"}` or `{"storyId"}` (story by id); both or neither is a 422 body validation error. Input validation runs before the permission check, as in suites. (W10.T3, W10.T3 review)
- `plan.signed_off` carries `ids.planId` only. No MCP tool and no audit event for plans. (W10.T3)
- The items dialog has two searchable multi-selects (active suites plus any archived suite already in the plan, and every story); saving sends suites first, then stories, in the order picked. The plans module reads suites with its own hook (`GET_PLAN_SUITES_KEY`). (W10.T3)
- *Sign off* stays visible with `plan.sign_off`; while failures are active its dialog says so and the confirm button is disabled. Edit and *Choose suites and stories* show for an open plan with `plan.edit`, *Close plan* for an open or signed-off plan with `plan.edit`; none in an archived project. (W10.T3)
- The progress bar is a new design-system component, `DSProgress` (a stacked Mantine `Progress`, one named `progressbar` per section). The plans list's status filter is component state, not in the URL. After a create, the new plan opens. (W10.T3)

#### 9.2 Shared steps and data-driven cases (W10.T5, W10.T6)

- A case version stores a shared step as `{order, shared_step_key}`, never a copy; the editor's step response shows `{order, action: null, expected: null, sharedStepKey}` and every plain step has `sharedStepKey: null`. Expanded snapshot steps keep `shared_step_key` and `shared_step_version_number`; run step responses don't carry `sharedStepKey`. (W10.T5)
- Keys: letters, digits and `_`, starting with a letter, at most 64, stored in lowercase, unique per project including archived steps, so a reference never changes meaning. A bad key gets `INVALID_REQUEST` (pydantic checks the pattern before trimming). (W10.T5)
- Only new steps add a shared step version; a title change, archive and restore don't. `PATCH` needs `baseVersionNumber` (`CONFLICT` when stale), as for test cases. (W10.T5)
- An archived shared step can't be added to a case; a case that already uses it keeps it, can be edited, and runs its last version. Archiving has no confirmation, because Restore undoes it. (W10.T5, W10.T6)
- "Used by N cases" counts the cases whose current version uses the step, Deprecated cases left out. (W10.T5)
- `parameters` is a list of names and `dataRows` a list of `{name: value}` objects with exactly those names; names `^[A-Za-z][A-Za-z0-9_]{0,49}$`, unique without case; values up to 1000 characters; rows without parameters refused; an unknown `{{param.x}}` is listed in `unknownReferences` and blocks Ready. (W10.T5) Since W10.FIX every save also refuses parameters without rows (`require_data_table`, `INVALID_STEP_SHAPE`, "Add at least one data row for the parameters, or remove the parameters."), so no saved version has them; the Ready guard in `utils/readiness.py` stays for versions saved before the rule. The case editor checks the same before the save (`validateDataTable` -> `parametersWithoutRows`) and sends nothing (CASE-16 AC8, AC10, AC16). (W10.FIX)
- A row value is refused (`SECRET_IN_DATA_ROW`) when it contains any secret value of the project, in any environment; checked only when the rows change. (W10.T5)
- A case version's data keys are its own, its rows' and its shared steps' as they were at save time. A `{{param.x}}` inside a shared step is not checked against each case's parameters; runs and the context tools always read the current shared steps. (W10.T5)
- Worst-iteration order: `failed`, `blocked`, `passed`, `skipped`, the lowest iteration on a tie. Only the first failing iteration in a run opens or updates the failure; the flaky score takes one decisive result per run. (W10.T5)
- Run detail: `RunCaseResponse` gains `parameters` and `iterations[]` (`iteration`, `values`, `result`, `steps`; empty without rows); `result` and `steps` show the worst iteration; `RunCaseResultResponse` gains `iteration`; the manual run reply gains `parameters` and `dataRows`; the manual record reply has `iteration`; missing screenshots name their `iteration` for a data-driven case (`null` otherwise in the REST report, left out of a plain case's `finish_run` reply). (W10.T5, W10.T6)
- `run.case_recorded` keeps its ids, with no iteration added; `shared_step.changed` carries `sharedStepKey` and `sharedStepId`. (W10.T5)
- The CSV and xlsx import and `create_draft_cases` accept plain steps only; shared steps, parameters and rows are added in the editor (plan item 6, confirmed). (W10.T5)
- The 0026 downgrade deletes results with `iteration > 0` (and their step results) before restoring the old unique key, and fails if a failure points at one of them, so nothing is lost silently. (W10.T5)
- Claude runs a data-driven case once per row in row order (iteration = row index from 0), each iteration from the preconditions, with `{{param.name}}` replaced in preconditions, actions and expected results; a failed or blocked iteration ends only itself. It records each iteration right after its last executed step, and resolves `{{data.key}}` row values with `resolve_data` just before the iteration, writing only the reference in chat and results. (W10.T6)
- The manual record body always carries `iteration` (`0` without data rows); five existing tests that compare the exact PUT body now expect `iteration: 0` (a request-shape change, no assertion removed). (W10.T6)
- The editor and read view find a referenced shared step through one `GET …/shared-steps?archived=true` per project; a key the list lacks shows "This shared step no longer exists in the project." Expanded, it shows the shared step's current version, read-only. Both the editor and the read view show `{{data.key}}` in the expanded step as value chips; the editor takes its references from the effective test data of the project's default environment (else the first one) and the case's files, with secrets masked and no Reveal (CASE-16 AC15). (W10.T6, W10.T6 review, W10.FIX)
- Run detail and recording replace `{{param.name}}` with the iteration's value and list the row values above the steps. Recording opens one iteration block at a time (the first without a result), moves on after each save, keeps a draft per iteration, and counts a case as recorded only when every iteration is. (W10.T6)
- The shared step page is its own route, `/projects/[projectKey]/shared-steps/[key]`; keys are lowercased, and one that can't match the pattern shows "not found" without a request. (W10.T6)
- Version history and Compare show a shared step as "Shared step: key". A version that changes the parameters or data rows shows a "Parameters and data rows" entry in History and a row in Compare (the parameter names, then "1. value | value" per row, with the word diff), so it never shows "identical"; Compare shows the row only when one of the versions has parameters (CASE-7 AC3, CASE-15 AC9). (W10.T6, W10.T6 review, W10.FIX)
- No `{{param.` autocomplete in the step editor (the design-system suggestions know only `data` and `file`); an unknown `{{param.x}}` is reported by the server on Ready. The usage list's `status` is a plain string in the API: a known value shows the badge, an unknown one raw text. (W10.T6)
- Design-system additions: `DSInput.isLabelHidden`, `DSStepEditor.renderSharedStep` and `footerActions`, `DSStepEditorStep.sharedStepKey`. Fixtures and three small spots in other modules (case-review compare, review comment step option, version history) were updated only for the regenerated API types. (W10.T6)

#### 9.1 and 9.2 fix-up of the W10 review items (W10.FIX)

What the code does now for the W10 review items that W10.FIX fixed, and the choices its fixers made. Checks after the fix-up: server `pytest` 2385, client Vitest 1422 in 244 files, plugin 62, e2e 37, all passing.

- Story sign-off: a running suite run that holds a case of the story blocks `Mark passed` (see 9.1 Suites above); a running suite run with no case of the story doesn't. (W10.FIX)
- The 0024 downgrade first deletes the suite runs and every row that depends on them (their `suite_run_finished` notifications, the failures a suite run opened with their events and `failure_assigned` notifications, step and case results, run cases, run files and run logs), clears `failure_events.case_result_id` and `parent_run_id` links that point at them, then makes `runs.story_id` NOT NULL again. A story-run failure whose latest result came from a suite run is kept and points back at its newest story-run result, or at its opening result if there is none. Audit events keep their `run_id`, which has no foreign key. `tests/migrations/test_suites_downgrade.py` runs the downgrade for real on its own database (`tessio_migration_downgrade` on the test container), never on `tessio` or `tessio_migcheck`. (W10.FIX)
- `PUT …/suites/{suite_id}/cases` with the same cases in the same order writes nothing and publishes no `suite.changed` (SUITE-1 AC5). Unknown or foreign case ids are still checked before the comparison, so a bad request fails as before. (W10.FIX)
- SUITE-4 AC2 now spells out the real `OPEN_GAPS_BLOCK_RUN` message: the lead sentence, gaps separated by "; ", `{key} gap {id} (assigned to {x}): {question}`, the assignee as a name, "the {Role} role" or "nobody", whitespace collapsed, the question cut to 120 characters ending in "…", and "; and {n} more". (W10.FIX)
- MCP `start_run.suite` takes 1 to 200 characters (`MAX_SUITE_REFERENCE_LENGTH`). An empty `suite` is now refused by MCP input validation; before, it counted as no suite and gave `INVALID_REQUEST` ("exactly one of story_key and suite"). (W10.FIX)
- Project isolation of the write routes is tested: a foreign suite gives 404 `NOT_FOUND` on PATCH, archive, `PUT …/cases`, by-filter and a manual run with its `suiteId`, and a foreign plan on PATCH, `PUT …/items`, sign-off and close, each leaving the foreign record unchanged. (W10.FIX)
- Shared step messages: a step with both an action and `sharedStepKey` gets "Step n: a shared step has no action or expected result of its own." (it said "shared step step"); CASE-16 AC6 quotes both step-shape messages. (W10.FIX)
- Expanded step limit: a case save whose steps, with shared steps expanded, go over 200 is refused (`INVALID_STEP_SHAPE`, `ExpandedCaseTooLongError`), and so is a shared step save that would push any case using it over 200 (no version is added). The check covers the current version of every non-Deprecated case that names the shared step, the same set as "Used by N cases"; an archived shared step a case still uses counts with its current steps. The limit is its own constant, `MAX_EXPANDED_CASE_STEPS = 200` in `shared_steps`, because `test_cases` can't import `runs`; a unit test keeps it equal to `MAX_STEPS_PER_CASE` and the manual route's `max_length`. A run start doesn't refuse an older case over 200 steps, but any save of that case reruns the check. (W10.FIX)
- A case saved before these rules (parameters without rows, or over 200 expanded steps) is refused on its next edit, even a title change, because `update_test_case` reruns `check_case_content`; the message says what to fix. Accepted by the G2 review. (W10.FIX)
- `PostgresStoryContextReader` gets the container's `case_step_expander` injected (`container.py`); a test swaps the container's expander for a recording one and checks the reader uses it. (W10.FIX)
- Two concurrent creates of the same shared step key: the repository maps the unique violation on `shared_steps_project_id_key_key` (the default name migration 0026 creates; 0026 not edited) to `SHARED_STEP_KEY_ALREADY_USED` (CASE-16 AC2). The race is tested with a repository whose key lookup misses; a real two-request HTTP race was not run. (W10.FIX)
- A failure's result history lists every iteration with its number: `iteration` on `CaseResultHistoryItem` and `FailureResultResponse` is the data row index (from 0) for a case version with data rows, `null` otherwise (the same rule as `missingScreenshots`, RUN-6 AC5), joined through `case_results.test_case_version_id`. The client shows an "Iteration" column after Result, numbered from 1 (`formatIterationNumber`), "—" for none, hidden when no result has one (FAIL-3 AC3b). (W10.FIX)
- French `suites.json` says "Étiquettes" / "étiquette" in the filter dialog and the empty suite text, like `labels.json`; a Vitest test checks the term in all three languages. (W10.FIX)
- A preselected suite in the manual-run select is named from the loaded suite (with "(archived)" when archived), never its id; the field stays empty until the suite loads. The run list's Suite filter follows the same rule. (W10.FIX)
- "{code} removed from the suite" shows only once the `PUT …/cases` succeeds: on each successful save, every removed case missing from that save's ids gets its toast; a failed save drops the pending toasts, because the order goes back. (W10.FIX)
- The plugin stays 0.5.0: the W10.FIX skill changes ship with the 0.5.0 that W10 POST set, so no version bump. (W10.FIX)
- `runs.md` RUN-9 AC1 points to the suite run page and the suite re-run (SUITE-5 AC6, SUITE-8 AC7 and AC8) and to RUN-8 AC1 for *A story* / *A suite*, which W10 POST had already updated; RUN-7 AC6b was added by W10 POST. RUN-9 AC2 also names the suite re-run call and the batches of at most 50 (SUITE-8 AC8). (W10.FIX)

#### 9.3 Version compare and review comments (W9.T5)

- Review comments live in the `test_cases` module (no new module), because the Ready rule is in `ChangeTestCaseStatusUseCase`. The resolve route is nested under the case: `PUT …/test-cases/{case_code}/review-comments/{comment_id}/resolve`. (W9.T5)
- "The author" for `requireSeparateReviewer` is whoever saved the current version (`currentVersion.createdBy`), not the case's creator; if a reviewer edits the case, the first author may then review it. Both review actions count: Mark ready and Mark reviewed. Submit for review, Back to draft, Back to review and Deprecate stay open to the author. (W9.T5)
- An open comment, on any version, blocks only the move to Ready. Adding a comment to a Ready case leaves it Ready, and editing a Ready case keeps it Ready, so with the setting on an author can still change a Ready case without a second review (open point for Peter). (W9.T5)
- Admin and QC (`test_case.edit`) comment and resolve, any comment including their own; everyone with `test_case.view` reads. Resolving twice changes nothing. Comments are never edited, reopened or deleted. (W9.T5)
- A comment takes an optional `versionNumber` (default: current) and `stepOrder` (must exist in that version, else `INVALID_REQUEST`); an unknown version gets `NOT_FOUND`. A deprecated case takes no new comments (`CONFLICT`), but its comments can still be resolved. (W9.T5)
- `REVIEW_COMMENTS_OPEN` puts the open count in the message only. The Ready checks run in this order: separate reviewer (403), open comments (409), then `CASE_NOT_READY` and `UNKNOWN_REFERENCE`. (W9.T5)
- The comment reply carries `authorName` and `resolvedByName`. `review_comment.changed` carries `testCaseId`, `code`, `storyId` and `commentId`, and is published only when something changed. (W9.T5)
- `ProjectResponse.requireSeparateReviewer` is always present; in `PATCH /api/projects/{project_key}` a missing field or null keeps the saved value (`project.edit`). (W9.T5)
- No MCP tool or plugin change: `get_story_context` serves only Ready cases, which by rule have no open comments. Spec numbers: CASE-15 and SET-4. (W9.T5)
- The compare view and the comments panel are two new case tabs, Review (with the open count) and Compare (`?tab=review`, `?tab=compare`). The History tab and its inline compare stay, because CASE-7 relies on them; History still lists AC links, data keys and files, which Compare leaves out. (W9.T5)
- Compare lines steps up by content (longest common subsequence on action plus expected result), not by position, and starts on the previous and the current version. (W9.T5)
- A new comment sends the current version's number explicitly. If the case was saved in between, the server still accepts that older number: the comment stays on the version the reviewer saw and shows "On version n". (W9.T5, wording corrected by the W9.T5 review)
- The client compares the signed-in user with `currentVersion.createdBy` to hide Mark ready and Mark reviewed from a blocked author, and disables Mark ready while a comment is open; the server rules stay the real check. Screens without a session hide nothing. (W9.T5)
- The Review settings card sits after the Labels card and is visible only with `project.edit`. The new required `requireSeparateReviewer` meant adding it to 10 project test fixtures. (W9.T5)

#### 9.13 Flaky cases and quarantine (W9.T4)

- Only `passed` and `failed` count as flips; `blocked` and `skipped` are skipped, then the last 10 decisive results are taken, across executors. (W9.T4)
- "The same case version" is the current version. Saving a new version (an edit or a file attach) resets the score, `flakySince` and the disagreement at once, in `add_version`. (W9.T4)
- `flakySince` is when the case first reached 3 flips, kept while it stays flaky, cleared below 3; `isFlaky` is `flakySince != null`. (W9.T4)
- Disagreement compares the latest manual with the latest automated decisive result on the current version (automated = any executor other than `manual`), at most 24 hours apart (exactly 24 h counts); `disagreedAt` is the later time, stored in `test_cases.disagreed_at`. An older differing pair (manual pass, then Claude fail, then Claude pass) does not count: Peter to confirm "latest against latest". (W9.T4)
- Auto-release counts the 10 most recent decisive results after `quarantinedAt`, on any version. (W9.T4)
- The quarantine audit trail is a new table `test_case_quarantine_events` in 0022 (`quarantined`, `released`, `auto_released`, actor null for the automatic release), read through `GET …/quarantine-events` (`test_case.view`), because `audit_events.actor_id` is NOT NULL and its action enum widens only in W15. Migration 0022 also adds `disagreed_at` and `quarantine_reason`. (W9.T4)
- An optional reason, up to 500 characters, is stored on the case and the event. A PUT on a quarantined case or a DELETE on one that isn't is a no-op that returns 200, keeps the first reason and time, and adds no event. Both work in any status. (W9.T4)
- Recompute jobs are not deduplicated (the recompute is idempotent and cheap). They are enqueued after the result's transaction commits; a Redis error is logged and swallowed, and the nightly sweep at 03:45 UTC catches up. The sweep recomputes every case, one transaction each. (W9.T4)
- Ports: runs owns `FlakyRecomputeRequester`; test_cases owns `CaseResultHistoryReader`, which runs implements, because test_cases sits below runs. (W9.T4)
- List filters `flaky`, `disagreeing` and `quarantined` take `true` or `false`; the screen has "only" checkboxes that send `true` or nothing. (W9.T4)
- Badges sit in the Status cell (Flaky yellow, Disagreeing red, Quarantined gray). Quarantine and Release are header buttons for `test_case.quarantine` on a project that is not archived; Release has no confirmation. The alert names the member who quarantined the case, or "a former member". The quarantine history is a timeline on the History tab. (W9.T4)
- The disagreement alert says "A person and Claude disagree", because `claude` is the only automated executor today; it needs new wording when `script` and `ci` arrive (W12, W13). (W9.T4)

#### 9.18 Answer gaps with Claude (W9.T1, W9.T2)

- The REST field is `isAnsweredViaClaude`, not the plan's `answeredViaClaude`, following the predicate rule and the sibling `isRaisedViaClaude`. It always describes the latest answer: a reopened gap keeps its old answer, and the next answer sets the flag again. (W9.T1)
- `get_my_gaps` needs `gap.answer` and is `is_write=True` in the MCP tool catalog, though the reservation said `false`: in `test_mcp_tool_access.py` the flag means "refused for Viewers and on archived projects", and the plan wants a Viewer 403. (W9.T1)
- `set_test_data` takes `kind` in `variable | endpoint | secret`; `endpoint` is stored as `variable` (merged by migration 0015), and `secret` is refused with `INVALID_REQUEST`. A key that is a secret in any scope is refused too. (W9.T1)
- `set_test_data` with no environment writes to All environments; with an environment name (trimmed, any case) it writes that environment's override and leaves the project value alone. An existing value is updated (same value: `unchanged`), the key's description is kept, an unknown environment gets `NOT_FOUND` and an archived one `INVALID_REQUEST`. A project write also returns `overridden_in`. (W9.T1)
- Similar answers use Postgres full-text search on `search_vector` (`'simple'` config): words of 3 or more letters, minus a short English stop-word list and repeats, at most 20, joined with OR. Only resolved gaps of the token's project match, same story first, then rank, then the latest answer, 3 at most. French and Vietnamese common words are not dropped. One query runs per listed gap (up to 50). (W9.T1)
- `get_my_gaps` replies `{gap_count, gaps[], stories[], assignees[]}`, at most 50 gaps, high severity first, then story key, then age; `assignees` lists the active non-Viewer members so the skill can reassign. `answer_gap` replies `{status, open_gap_count, is_ready}` and `reassign_gap` `{assignee_name}` or `{assignee_role}`. (W9.T1)
- `reassign_gap` takes exactly one of `assignee_user_id` and `assignee_role` (never `viewer`), with the REST validator's messages. (W9.T1)
- `api_tokens` moved to its own import layer below `jira | test_data`, so the `test_data` MCP tool can use token authentication. (W9.T1)
- The "via Claude" badge for an answer sits in the answer box beside "Answered by"; a gap raised and answered with Claude shows two badges. It reuses the `gaps.badge.viaClaude` text. (W9.T1)
- The blocked-run procedure handles `OPEN_GAPS_BLOCK_RUN` (story runs and re-runs today) and `GAPS_OPEN` (suite runs, W10); W10 must keep `GAPS_OPEN` or update the procedure. (W9.T2) W10 updated the procedure: suite runs get `OPEN_GAPS_BLOCK_RUN` too. (W10.T4)
- `get_open_gaps` gained `assignee_name` or `assignee_role` and `is_assignee_deactivated`, so the procedure can name who must answer; MCP only, no REST change. (W9.T2)
- `get_my_gaps` returns `test_data_url` (`CLIENT_URL` + `/projects/{key}/test-data`) when a listed gap is `missing_test_data`, so the skill can send secrets to the Test data page. (W9.T2)
- Claude Code's question prompt allows 2 to 4 options: "write my own" is the built-in free text, and with three suggestions "Not mine" and "Skip" merge into one option with a follow-up. Up to four gaps per prompt, then one batch summary with Save all, Change one or Cancel; picking alone saves nothing. (W9.T2)
- `set_test_data` runs before `answer_gap`. On `PERMISSION_DENIED` (PM, BA) the answer is still saved and Claude says a QC, Dev or Admin must add the value. (W9.T2)
- Only `/tessio:run-story-tests` is offered for a ready story; `/tessio:run-scripts` arrives in W12. (W9.T2)
- Claude cites product code only after a quick `Glob` finds source files in the working directory, and never edits. Secrets are passwords, tokens, API keys, private keys, card security codes and other credentials, or keys the context or `set_test_data` reports as secret. (W9.T2)
- The argument hint `[STORY-KEY | mine]` is quoted, and a plugin test refuses unquoted front matter values that start with a YAML indicator. (W9.T2)
- T2 changed server code the reservations did not list: additive MCP reply fields in the `gaps` module and one line in `container.py`; no migration, capability, error code, event or REST change. (W9.T2)

### Open issues (parked)

Each item was checked against the code on 2026-11-01 and is still true. The W10 review items that W10.FIX fixed were removed on 2026-11-02; what the code does now is under [Implementation assumptions](#91-and-92-fix-up-of-the-w10-review-items-w10fix).

- 3.3b.4: `/users/[userId]` lists real memberships only; a workspace admin's implicit Admin access to every project is not shown.
- 3.3.1: project create does not check the Jira project key or board against Jira; only the "already linked" check runs.
- 3.13.2: there is no Jira disconnect (`DELETE /api/workspace/jira`), and changing the connection publishes no audit or live event.
- 4.10: admin user actions (invite, deactivate, reactivate, reset 2FA, role change) write no audit events.
- 3.2.5: old avatar files are not deleted when a new avatar is saved or the photo is removed.
- 3.10.2: a screenshot uploaded after `finish_run` stays missing.
- 3.11.3: an automatic failure reopen sends no notification.
- 3.14.6: an upload cannot be aborted mid-request while it is being signed or completed; the cancel takes effect at the next step.
- 3.6.4b: `useDownloadFile` opens the new tab after the request returns, so a popup blocker may stop it.
- 3.13.4: pressing Enter in the "Other MIME type" input submits the form instead of adding the type; use the Add button.
- 3.6.1: the case list has no pagination, and test files cannot be deleted (upload a new version instead).
- 4.11: BullMQ de-duplication: a stale running sync that is still active in BullMQ leaves a new request queued until the next request.
- 4.4: Kanban boards have no sprints, so a sync on a Kanban board succeeds with no stories.
- 5.6: the hook retry list has no cap, so a screenshot whose upload keeps failing with 5xx stays pending for good.
- 3.2.6: the install command puts the token on the command line, so it can end up in shell history.
- 4.12: the finish side effects are repeated in `finish_run.py`, `finish_manual_run.py` and `abort_stale_runs.py`.
- 3.14.2: `RATE_LIMITED` shows the generic message without the `Retry-After` value.
- 2.5: the Mermaid diagrams have not been parsed by mermaid-cli (B-16).
- 7.1b: the local dev containers still run the old unpinned images (postgres:17-alpine, redis:8-alpine, rustfs latest, Mailpit v1.27) until the next `docker compose up -d`.
- 6.2: the e2e suite does not cover file uploads (so bucket CORS stays a manual check), a real Jira site, Claude runs over MCP or the date input focus border. Since W9, `12-answer-gaps` calls two MCP gap tools over `/mcp` with an API token, but no Claude session. Since W10, `13-suite-run` covers a manual suite run and a plan sign-off, but not shared steps, data-driven cases or a Claude suite run.
- 9.18: `/tessio:answer-gaps <STORY-KEY>` on a story blocked only by other people's gaps says "Nothing is waiting for you" and doesn't say the story is still blocked, because `get_my_gaps` returns `stories` only for the listed gaps (W9.T2 review). Fix: call `get_open_gaps` and follow the blocked-run procedure.
- 9.18: `get_my_gaps` runs one similar-answer query per listed gap (up to 50 in one transaction); batch it if the call gets slow (W9.T1 review).
- 9.1: label names are unique without regard to case only in the use case; the database constraint is case-sensitive, so two concurrent creates of "Smoke" and "smoke" can both succeed, and two identical concurrent names can end in an unmapped integrity error (W9.T3 review). Fix: a unique index on `(project_id, lower(name))` or map the error to `CONFLICT`.
- 9.1: QC can create labels from the case picker but has no screen to rename, recolour or delete them, because the label manager card is on the Admin-only settings page (W9.T3).
- 9.3: with "Reviewer must not be the author" on, an author can still edit a Ready case and it stays Ready, skipping a second review; Peter to decide whether an edit should send it back to In review (W9.T5 review).
- 9.3: the client modules `test-cases` and `case-review` import each other; move `TextDiff` and the version types to `shared/` later (W9.T5 review).
- 9.13: the nightly flaky sweep recomputes every case in every project, archived ones included; limit it to cases with a new result or a flag once projects grow (W9.T4 review).
- 9.1: the plans list runs 2N+3 queries for N plans (counts per plan); batch it when plan lists grow (W10.T3 review).
- 9.1: the `suite-detail.test.tsx` "moves a case to the bottom…" test failed once under full parallel load and passed on every re-run; watch it for flakiness (W10.T2, T3 and T6 reports).

---

## Screens needed for mockups (from section 3)

The checklist for design work packages 2.6 and 2.7.

**MVP**

- [ ] Sign in, accept invite (set password), two-factor setup and prompt, reset password
- [ ] Profile (password, 2FA, API tokens, theme)
- [ ] Project switcher, create project (link Jira project and board)
- [ ] Project members and roles
- [ ] Workspace user directory
- [ ] Workspace settings: Jira connection
- [ ] Dashboard (current sprint + "my work")
- [ ] Sprint list, sprint detail
- [ ] Story list (with Sync states: never synced, syncing, last sync), story detail (AC, test cases, traceability matrix, gaps, runs)
- [ ] Test case editor (steps, AC links, data references, test case files, review status)
- [ ] Google Sheets import
- [ ] Gap inbox and gap detail
- [ ] Environments and test data (with secret masking)
- [ ] Run list (including aborted runs), run detail with step screenshots (and the "screenshot missing" state), run report
- [ ] Manual run entry
- [ ] Failure list and failure detail (with the assign control)
- [ ] Project settings
- [ ] Empty, loading and error states for each of the above

**Later**

- [ ] Trend charts · Email/Slack notification settings · Report export · Claude-drafted test cases review

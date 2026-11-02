# Client ↔ API

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.14 · Story prefix API · Index: [README](README.md)

## Purpose

How the Next.js client talks to the FastAPI server: types generated from the server's OpenAPI spec, one typed fetch client, react-query hooks, a shared error shape, the session gate, the live event stream that refreshes data, and signed uploads and downloads that go straight to object storage. Server: [server/app/commands/export_openapi.py](../../server/app/commands/export_openapi.py), [server/app/api](../../server/app/api), [server/app/modules/live_events](../../server/app/modules/live_events), [server/app/modules/files](../../server/app/modules/files). Client: [client/src/lib/api](../../client/src/lib/api), [client/src/lib/react-query](../../client/src/lib/react-query), [client/src/shared/hooks](../../client/src/shared/hooks), [client/src/components/session-guard](../../client/src/components/session-guard), [client/src/lib/uploads](../../client/src/lib/uploads).

## Roles and capabilities

- The data layer adds no permission of its own. Each request is checked on the server by the capability its spec names.
- The event stream sends a user only the events of their own user id or of projects they can see.

## User stories

### API-1 Generated API types (WBS 3.14.1)

As a client developer, I want the API types generated from the server, so that a changed endpoint breaks the build instead of the user.

- AC1: `uv run python -m app.commands.export_openapi` writes [openapi.json](../../client/src/lib/api/openapi.json) with the `ErrorResponse` and `ErrorCode` schemas added.
- AC2: `npm run generate:api` runs `openapi-typescript` and writes `openapi.type.ts`. The client's error code type is the generated `ErrorCode` schema.
- AC3: CI fails when either file differs from what the commands produce (`git diff --exit-code`).

### API-2 Data-fetching layer (WBS 3.14.2)

As a client developer, I want one way to call the API, so that every screen handles loading and errors the same way.

- AC1: `apiClient` is an `openapi-fetch` client on the same origin, with `credentials: "same-origin"`, typed by `paths`.
- AC2: Each request has one hook in its module (`hooks/queries/use-get-…`, `hooks/mutations/use-post-…`), built on `useAppQuery` or `useAppMutation`, with an exported `<NAME>_KEY` constant used as the first part of the query key.
- AC3: A failed call becomes an `ApiError` with `status`, `code` (an `ErrorCode` or null), `message`, and `fieldErrors` when the server sent a 422 validation `detail`.
- AC4: Each hook maps the error codes it expects to translated messages (an `apiErrors` map); unknown codes fall back to `errors.api.<CODE>` or "Something went wrong. Try again in a moment."
- AC5: Query defaults: no automatic retry, no refetch on window focus, data fresh for 30 s.
- AC6: Every screen reads real data; the old mock data folder is gone.

### API-3 Session handling (WBS 3.14.3)

As a user, I want to be sent to sign-in, the two-factor step or setup when needed, so that I never see a broken page.

- AC1: `proxy.ts` (the Next.js request proxy) redirects any non-public page to `/sign-in?next=<path>` when the `tessio_session` cookie is missing.
- AC2: Inside `(app)`, the session guard loads `GET /api/auth/me`. `nextStep` `two_factor_required` goes to `/two-factor`, `two_factor_setup_required` goes to `/two-factor/setup`, both keeping `next`. Only `signed_in` renders the page.
- AC3: A 401 from `/api/auth/me` (or any call that makes it refetch) goes to `/sign-in` with the "Your session has expired" message and the current path as `next`.
- AC4: If `/api/auth/me` fails for another reason, the guard shows "We could not load your session." with Try again.

### API-4 Live events (WBS 3.14.4)

As a user, I want screens to update when someone else changes data, so that I don't have to reload.

- AC1: When signed in, the client opens one `EventSource` on `/api/events`. The server sends `ready`, then one frame per event, and a keep-alive ping every 15 s. The stream sends `Cache-Control: no-transform` so proxies do not hold it back.
- AC2: The server fans out from Redis pub/sub (channel `tessio:events`): an event with a user id goes to that user; a project event goes to users who can see the project. Visibility is refreshed every 60 s, and at once on `project.members_changed`.
- AC3: Each event type invalidates the query keys listed in [live-event-query-keys.constant.ts](../../client/src/shared/typing/constants/live-event-query-keys.constant.ts); the screens refetch.
- AC4: On a dropped stream the client reconnects after 1 s, doubling to at most 30 s, with up to 20 % jitter, and also when the browser comes back online. After a reconnect it invalidates every query, since events may have been missed.
- AC5: When the stream closes because the session ended, the guard re-checks the session.

### API-5 Local forwarding (WBS 3.14.5)

As a developer, I want `/api` and `/mcp` to reach the server through the Next.js dev server, so that cookies and SSE work on one origin.

- AC1: `next.config.ts` rewrites `/api/:path*` and `/mcp` to `TESSIO_SERVER_URL` (default `http://localhost:3202`).
- AC2: In production, Caddy sends `/api/*` and `/mcp*` to the API with response buffering off, and everything else to the client.

### API-6 Signed uploads and downloads (WBS 3.14.6)

As a user, I want files to go straight to storage, so that large files never pass through the API server.

- AC1: `useSignedUpload` checks size (20 MB, or 2 MB for avatars) and type on the client first.
- AC2: It asks `POST /api/projects/{project_key}/uploads` with kind (`test_file`, `evidence`, `import`), file name, content type and size, and gets a signed POST (URL and fields) valid for 15 minutes. The storage server enforces the size range and the exact content type.
- AC3: It posts the file to that URL as a form, with progress, then calls `POST …/uploads/{file_id}/complete`. The server reads the stored object: a missing object gives `UPLOAD_NOT_COMPLETED`; a bigger size or another type deletes it and gives `FILE_TOO_LARGE` or `FILE_TYPE_NOT_ALLOWED`.
- AC4: Only the uploader can complete their file. A cancel stops at the next step.
- AC5: Downloads call `GET /api/projects/{project_key}/files/{file_id}` (`file.download`) and open the returned link, valid for 5 minutes. Only uploaded screenshots, test files, evidence and reports can be downloaded; other files give `NOT_FOUND`.
- AC6: Avatars use `POST /api/me/avatar-upload` and its complete call, with no project.
- AC7: Files left `pending` for over a day are deleted by the daily `files.delete_orphans` job (03:00); pending screenshots are marked missing instead.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Error body | `{"code": "<ErrorCode>", "message": "<text>"}` | [error_response.py](../../server/app/api/error_response.py) |
| Query stale time | 30 s | `QUERY_STALE_TIME_IN_MILLISECONDS` |
| SSE reconnect | 1 s to 30 s, 20 % jitter | `LIVE_EVENTS_*` constants |
| SSE keep-alive | 15 s | FastAPI default |
| Visibility refresh on the server | 60 s | `PROJECT_ACCESS_REFRESH_INTERVAL` |
| Upload link | 15 minutes | `UPLOAD_LIFETIME` |
| Download link | 5 minutes | `DOWNLOAD_LINK_LIFETIME` |
| Orphan uploads | deleted after 1 day, daily at 03:00 | `ORPHAN_AGE` |

HTTP status per code (from `STATUS_BY_ERROR_CODE`):

| Status | Codes |
| --- | --- |
| 400 | `INVALID_ONE_TIME_LINK`, `INVALID_TWO_FACTOR_CODE`, `INVALID_CURRENT_PASSWORD` |
| 401 | `INVALID_CREDENTIALS`, `NOT_SIGNED_IN`, `INVALID_API_TOKEN` |
| 403 | `ORIGIN_NOT_ALLOWED`, `PERMISSION_DENIED`, `OWNER_ONLY`, `RUN_NOT_OWNED`, `REVIEWER_IS_AUTHOR`, `TOKEN_SCOPE_NOT_ALLOWED` |
| 404 | `NOT_FOUND` |
| 413 | `FILE_TOO_LARGE` |
| 422 | `WEAK_PASSWORD`, `PASSWORD_BREACHED`, `INVALID_REQUEST`, `JIRA_INVALID_CREDENTIALS`, `FILE_TYPE_NOT_ALLOWED`, `IMPORT_INVALID_FILE`, `UNKNOWN_REFERENCE`, `UNKNOWN_SHARED_STEP`, `INVALID_STEP_SHAPE`, `SECRET_IN_DATA_ROW`, `ITERATION_OUT_OF_RANGE`, `WEBHOOK_URL_INVALID`, `JUNIT_INVALID`, `JUNIT_NO_MAPPED_TESTS` |
| 429 | `SIGN_IN_LOCKED`, `RATE_LIMITED` (with `Retry-After`) |
| 502 | `JIRA_UNREACHABLE`, `CHAT_DELIVERY_FAILED` |
| 409 | every other code |

Event types and what they refresh:

| Event | Sent when | Refreshes |
| --- | --- | --- |
| `run.started` | a run starts | runs, run detail, story progress, recent runs, Insights trends |
| `run.case_recorded` | a case result is saved | runs, run detail, failures, traceability, story progress, latest results, recent runs, manual run, Insights trends, top failing, flaky, coverage by label, sprint coverage |
| `run.finished` | a run finishes or is aborted | the same, plus dashboard, my work and Insights tokens |
| `jira.sync_started` | a sync is queued | sync status |
| `jira.sync_finished` | a sync succeeded | sync status, sprints, stories, traceability, story progress, dashboard, my work, manual-run story picker, Insights sprint coverage |
| `jira.sync_failed` | a sync failed | sync status |
| `notification.created` | a notification is created (to its user) | notification list and unread count |
| `project.members_changed` | a member is added, changed or removed | members, project, projects, member candidates |
| `gap.changed` | a gap is raised, answered, reopened or reassigned | story gaps, gap inbox, story progress, dashboard, my work, Insights trends |
| `failure.changed` | a failure status, assignee or cause changes, or its Jira bug is requested, created, refused or refreshed by a sync | failures, failure detail, story progress, dashboard, my work, Insights trends |
| `test_case.changed` | a case is created, saved, reviewed, attached, changes status or gets new labels | test cases, case detail, versions, file versions, traceability, story progress, latest results, dashboard, my work, Ready cases for manual runs, shared steps, suites, suite detail, plans, plan detail, Insights top failing, flaky, coverage by label, sprint coverage |
| `story.changed` | a story's test status changes (by hand or by a run) | stories, story, traceability, story progress, dashboard, manual-run story picker, plans, plan detail, Insights sprint coverage |
| `review_comment.changed` | a review comment is added to a case or resolved | test cases, case detail, review comments |
| `label.changed` | a label is created, renamed, recoloured or deleted (`ids.labelId`) | test cases, case detail, labels, Insights coverage by label |
| `suite.changed` | a suite is created, renamed, has its description changed, is archived, or its cases change (`ids.suiteId`) | suites, suite detail, plans, plan detail |
| `shared_step.changed` | a shared step is created, saved with new steps (a new version), renamed, archived or restored (`ids.sharedStepKey`, `ids.sharedStepId`) | shared steps library, shared step detail and usage (keys added by W10.T6) |
| `plan.changed` | a test plan is created, edited, has its items changed, is signed off or is closed (`ids.planId`) | plans, plan detail |
| `plan.signed_off` | a test plan is signed off (`ids.planId`), sent right after its `plan.changed` | nothing on screen (the `plan.changed` sent with it refreshes); for webhooks (W11) |
| `failure.opened` | a case result opens a new failure (`ids.failureId`, `ids.runId`, `ids.storyId`, `ids.testCaseId`), sent right after its `run.case_recorded` (MCP, manual and JUnit import results) | nothing on screen (the `run.case_recorded` sent with it refreshes); for webhooks and chat ([integrations.md](integrations.md)) |
| `failure.status_changed` | a failure moves to another status, by hand (sent after its `failure.changed`) or reopened by a new failed result (`ids.failureId`, `ids.status`, `ids.storyId`, `ids.testCaseId`) | nothing on screen; for webhooks and chat |
| `gap.raised` | a gap is raised, by REST or MCP (`ids.gapId`, `ids.storyId`), sent after its `gap.changed` | nothing on screen; for webhooks and chat |
| `story.signed_off` | a story's test status becomes `passed` (`ids.storyId`, `ids.jiraKey`), sent after its `story.changed` | nothing on screen; for webhooks and chat |
| `webhook.changed` | a webhook is added, edited or removed, or one of its deliveries is queued, tried or redelivered (`ids.webhookId`) | the webhooks card and its delivery log in project settings ([integrations.md](integrations.md)) |
| `chat_channel.changed` | a Slack or Teams channel is added, edited or removed, or a message to it (test or event) was delivered or failed (`ids.chatChannelId`) | chat channels card in project settings ([NOTIF-8](notifications.md#notif-8-slack-and-teams-channels-wbs-96)) |
| `insights.changed` | the nightly `insights.daily_snapshot` job wrote a project's daily stats (`project_id`, no ids) | the Insights page queries ([insights.md](insights.md)) |
| `report.ready` | a report export finished (to the requester: `user_id`, `ids.fileId`, `ids.format`), sent with its `report_ready` notification | the export buttons' pending state ([INS-7](insights.md#ins-7-export-a-run-plan-or-story-report-wbs-95-3107)) |

## Screens and states

The data layer has no screen of its own. Every spec's "Screens and states" table lists the loading, error and live states it produces.

## API

| Method and path | Who |
| --- | --- |
| `GET /api/auth/me` | any session |
| `GET /api/events` | signed in (full session) |
| `POST /api/projects/{project_key}/uploads` | the kind's capability: `test_case.edit`, `run.record_manual` or `test_data.edit` |
| `POST /api/projects/{project_key}/uploads/{file_id}/complete` | the uploader, with the kind's capability |
| `GET /api/projects/{project_key}/files/{file_id}` | `file.download` |
| `POST /api/me/avatar-upload`, `POST /api/me/avatar-upload/{file_id}/complete` | signed in |
| `GET /api/health`, `GET /api/health/ready` | public |
| `/mcp` | API token ([runs.md](runs.md)) |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_SIGNED_IN` | No session, an expired session, or a half session on a full-session route |
| `ORIGIN_NOT_ALLOWED` | A `POST`, `PUT`, `PATCH` or `DELETE` under `/api/` whose `Origin` is not allowed, or with `Sec-Fetch-Site` from another site |
| `FILE_TOO_LARGE`, `FILE_TYPE_NOT_ALLOWED` | Upload outside the limits, at signing or at completion |
| `UPLOAD_NOT_COMPLETED` | Completion before the object exists |
| `INVALID_REQUEST` | Body or query validation failed (422 with `detail`), or an upload kind not allowed here |
| `NOT_FOUND` | Completing or downloading a file that is not the caller's or not in the project |

## Later

- Nothing in WBS 3.14 is Later.

## Differences from the proposals

- The [server proposal §7](../discussions/server-proposal.md#7-rest-api) published the OpenAPI spec from the running server. The code exports it to a file in the repo, and CI checks it.
- A Next.js `proxy.ts` (the request proxy of this Next.js version) gates pages on the cookie; the server is still the only judge of the session.

## Open points

- The SSE path through the production Caddy proxy has been set up (`flush_interval -1`) but not tried on a server (blocker for WBS 7.3).
- Real browser uploads need the bucket CORS rule; it is set by the `rustfs-bucket` service but no end-to-end browser upload has run yet.
- `useDownloadFile` opens the link after an `await`; some popup blockers may stop it (W5 carry-over).
- Cancelling during signing or completing waits for that request to end (W2 carry-over).

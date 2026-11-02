# Integrations: webhooks, API scope and CI import

**Status:** Draft · **Updated:** 2026-11-02

WBS 9.6 · Story prefix INT · Index: [README](README.md)

## Purpose

Tessio tells other systems what happens in a project and lets CI talk to it without a person signed in. Three parts, from [competitive features proposal F6](../discussions/competitive-features-proposal.md#f6-notifications-webhooks-public-api-and-ci-result-import-m-wbs-96):

- **Outbound webhooks:** a project Admin registers HTTPS URLs that get a signed JSON `POST` for chosen events.
- **API token scope:** a personal token is either for Claude Code (`mcp`, as before) or for the public REST routes (`api`), so a CI job can import results and read runs, failures and cases with the same role checks as its owner.
- **JUnit import:** CI uploads a JUnit XML report and gets a finished `ci` run ([runs.md, RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)).

Slack and Teams channels are in [notifications.md, NOTIF-8](notifications.md#notif-8-slack-and-teams-channels-wbs-96). Server: [server/app/modules/integrations](../../server/app/modules/integrations) (`webhook*` files), [server/app/modules/api_tokens](../../server/app/modules/api_tokens) (scope) and [server/app/modules/runs](../../server/app/modules/runs) (import). The api and the worker never call Claude and never run a browser.

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List, add, edit and remove webhooks; see the delivery log; redeliver | `integration.manage` | Admin |
| Create a token of either scope | `api_token.create` + project member ([AUTH-10](authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326)) | all members |
| Import JUnit results | `run.start` | Admin, QC, Dev |
| Read runs, failures and cases with an `api` token | `run.view`, `failure.view`, `test_case.view` | all |

An `api` token carries its user's project role, so every route still checks the same capability as for a signed-in user.

## User stories

### INT-1 Manage webhooks (WBS 9.6)

As a project Admin, I want to send Tessio events to our own systems, so that CI dashboards and bots react to runs and failures.

- AC1: `POST /api/projects/{project_key}/webhooks` with `url`, `events` (1 to 7 of the events in INT-3), optional `description` (1 to 200 characters) and `isActive` (true by default) answers 201 with `{webhook, secret}`. `events` is stored once each, in the fixed order of INT-3.
- AC2: The URL must be `https`, 2048 characters at most, with a host that has a dot, no user name or password, no whitespace and not port 0. `localhost`, names ending in `.localhost`, `.local`, `.internal`, `.lan` or `.home.arpa`, and IP addresses that are not global (private, loopback, link-local such as `169.254.169.254`, reserved, documentation, multicast, including IPv4-mapped IPv6) are refused with `WEBHOOK_URL_INVALID` (422).
- AC3: The server makes the signing secret: `whsec_` and 32 random bytes in URL-safe base64. It is shown once, in the create answer (and when rotated, AC5), and stored encrypted with the secrets key (`webhooks.secret_encrypted`). Every other answer has only `secretHint` (`whsec_…` and its last 4 characters).
- AC4: `GET /api/projects/{project_key}/webhooks` lists the project's webhooks, oldest first: `id`, `url`, `description`, `events`, `isActive`, `secretHint`, `createdAt` and `lastDelivery` (the newest delivery, or null).
- AC5: `PATCH /api/projects/{project_key}/webhooks/{webhook_id}` changes any of `url`, `description` (null clears it), `events` and `isActive`, and with `rotateSecret: true` makes a new secret. It answers `{webhook, secret}` with `secret` null unless it was rotated.
- AC6: `DELETE /api/projects/{project_key}/webhooks/{webhook_id}` removes the webhook and its deliveries (204).
- AC7: A project has at most 20 webhooks (`CONFLICT`). Another project's webhook gives `NOT_FOUND`. Every change publishes `webhook.changed` (`ids.webhookId`).

### INT-2 Deliveries, retries and the delivery log (WBS 9.6)

As a project Admin, I want to see what was sent and whether it arrived, so that I can fix a broken receiver and resend.

- AC1: For each event (INT-3), every active webhook of the event's project that chose it gets a delivery row (`pending`, 0 attempts) with the payload (INT-4), and a `webhook.deliver` job on the `integrations` queue (job id `webhook-delivery-<delivery id>`). Inactive webhooks and webhooks that didn't choose the event get nothing.
- AC2: The job sends `POST <url>` with the JSON body and the headers `Content-Type: application/json`, `User-Agent: Tessio-Webhooks/1`, `X-Tessio-Event`, `X-Tessio-Delivery` (the delivery id), `X-Tessio-Timestamp` (Unix seconds) and `X-Tessio-Signature` (INT-5). It waits 10 seconds at most and never follows a redirect.
- AC3: Before sending, the worker resolves the host. When any address is not global, nothing is sent and the try fails with "The webhook host resolves to a private, loopback or link-local address." (this also stops a public name that points at a private address). The HTTP client then resolves the host again to connect, so a host whose DNS answer changes between the two lookups (DNS rebinding) can still reach a private address; the sent address is not pinned to the checked one today.
- AC4: A 2xx answer makes the delivery `succeeded` with `responseStatus` and `deliveredAt`. Anything else (another status, a timeout, an unreachable host) is a failed try: `attempts`, `responseStatus` (when there was one), `error` (for example "The receiver answered HTTP 500." with the first characters of the answer, 500 at most) and `lastAttemptAt` are saved and the job fails, so BullMQ tries again.
- AC5: Five tries in all, with exponential backoff from 30 seconds (30 s, 1 min, 2 min, 4 min between them; `JOB_ATTEMPTS`, `JOB_BACKOFF_DELAY`). After the fifth failed try the delivery is `failed` and is not tried again. A delivery whose webhook was turned off fails at its next try with "The webhook is turned off." without sending.
- AC6: Every try publishes `webhook.changed`.
- AC7: `GET /api/projects/{project_key}/webhooks/{webhook_id}/deliveries?limit=` lists the webhook's deliveries, newest first (50 by default, 200 at most): `id`, `webhookId`, `event`, `status` (`pending`, `succeeded`, `failed`), `attempts`, `responseStatus`, `error`, `redeliveryOfId`, `lastAttemptAt`, `deliveredAt`, `createdAt` and `payload`.
- AC8: `POST /api/projects/{project_key}/webhooks/{webhook_id}/redeliver/{delivery_id}` copies the delivery's payload into a new `pending` delivery (`redeliveryOfId` = the original), queues it and answers 202 with it. The payload keeps its `id`, so a receiver can tell it is the same event. A delivery of another webhook gives `NOT_FOUND`.
- AC9: Deliveries are kept 30 days: the nightly `webhook.delete_old_deliveries` job (maintenance queue, `15 4 * * *`) deletes older ones.

### INT-3 Events (WBS 9.6)

As an integrator, I want a small, stable set of events, so that I don't have to follow every internal change.

- AC1: The events are `run.started`, `run.finished`, `failure.opened`, `failure.status_changed`, `gap.raised`, `story.signed_off` and `plan.signed_off` (`IntegrationEvent`, shared with the Slack and Teams channels).
- AC2: Webhooks listen to the existing Redis live events ([client-api.md](client-api.md)); no module calls webhooks directly. The worker's live event listener hands each event to the webhook handler (`RequestWebhookDeliveriesUseCase`), which maps it with `INTEGRATION_EVENT_BY_LIVE_EVENT` and queues the deliveries. The HTTP call happens only in the job. Every worker process runs this listener, so Tessio runs one worker (`compose.prod.yml`): a second worker replica would queue every delivery twice.
- AC3: When each is sent:

| Event | Sent when | `data` |
| --- | --- | --- |
| `run.started` | a Claude, manual or suite run starts, or a JUnit import is saved | `runId`, `storyId` or `suiteId` (none for an import without a suite) |
| `run.finished` | a run finishes, is aborted, or a JUnit import is saved | `runId`, `storyId` or `suiteId`, `status` |
| `failure.opened` | a failed result opens a new failure (MCP, manual or import) | `failureId`, `runId`, `storyId`, `testCaseId` |
| `failure.status_changed` | someone changes a failure's status, or a failed result reopens a fixed failure | `failureId`, `status`, `storyId`, `testCaseId` |
| `gap.raised` | a gap is raised (REST or MCP) | `gapId`, `storyId` |
| `story.signed_off` | a story's test status becomes `passed` | `storyId`, `jiraKey` |
| `plan.signed_off` | a test plan is signed off | `planId` |

- AC4: Live events are fire and forget: an event sent while the worker is down is not delivered, and is not in the delivery log.

### INT-4 Payload (WBS 9.6)

- AC1: The body is compact JSON (UTF-8):

```json
{
  "id": "0193…",
  "event": "run.finished",
  "occurredAt": "2026-11-02T10:15:00.123456+00:00",
  "project": {"id": "0192…", "key": "SHOP", "name": "Shop"},
  "data": {"runId": "0193…", "suiteId": "0192…", "status": "failed"}
}
```

- AC2: `id` is the event's id: the same for every webhook that gets this event and for its redeliveries. `X-Tessio-Delivery` is the delivery's own id.
- AC3: `data` holds only ids and short values (INT-3 AC3). A receiver that needs more reads it from the REST API with an `api` token (INT-6). No secret value is ever in a payload.

### INT-5 Signature (WBS 9.6)

As an integrator, I want to check that a call comes from our Tessio, so that nobody else can trigger my CI.

- AC1: `X-Tessio-Signature` is `sha256=` and the hex HMAC-SHA256 of `<X-Tessio-Timestamp>.<raw body>` with the webhook's secret as the key.
- AC2: To verify: read the raw body and the timestamp header, compute the same HMAC, compare in constant time, and refuse timestamps older than a few minutes to stop replays. In Python:

```python
expected = "sha256=" + hmac.new(secret.encode(), f"{timestamp}.".encode() + body, hashlib.sha256).hexdigest()
ok = hmac.compare_digest(expected, request.headers["X-Tessio-Signature"])
```

- AC3: Rotating the secret (INT-1 AC5) signs every later try, including retries of older deliveries, with the new secret.

### INT-6 `api`-scope tokens for the public REST API (WBS 9.6)

As a CI maintainer, I want a token that can import results and read runs, so that my pipeline needs no browser session.

- AC1: `POST /api/me/api-tokens` takes `scope`: `mcp` (default) or `api`; any other value is a 422 validation error. The token list and the create answer return `scope`. Existing tokens are `mcp` (migration 0029 column `api_tokens.scope`).
- AC2: An `api` token is sent as `Authorization: Bearer tsio_…` without a session cookie, and is accepted only on these routes (the route catalog marks them `token_allowed`):
  - `POST /api/projects/{project_key}/runs/import`
  - `GET /api/projects/{project_key}/runs`, `GET …/runs/{run_id}`, `GET …/runs/{run_id}/log`
  - `GET /api/projects/{project_key}/failures`, `GET …/failures/{failure_id}`
  - `GET /api/projects/{project_key}/test-cases`, `GET …/test-cases/{case_code}`, `GET …/test-cases/{case_code}/versions`
- AC3: On those routes the token must be active (`INVALID_API_TOKEN` otherwise) and be for the project in the path (another project gives `NOT_FOUND`, even when its user is a member there). The route's own capability check then uses the user's role.
- AC4: An active `api` token on any other route (every session route, the plugin hook routes `…/screenshot-upload` and `…/log` upload) and on `/mcp` tool calls gets `TOKEN_SCOPE_NOT_ALLOWED` (403).
- AC5: An `mcp` token keeps today's behaviour: it works on `/mcp` and the hook routes, and REST routes that need a session answer `NOT_SIGNED_IN` (401), the token-allowed ones included. A revoked or expired token on a session route also answers `NOT_SIGNED_IN`.
- AC6: When a request has both a session cookie and a token, the session is used.
- AC7: The REST docs come from the OpenAPI spec the server publishes; the request and answer shapes are the same for a token and a session.
- Tests: `test_token_scope.py` in [tests/api/security](../../server/tests/api/security) sends an `api` token and an `mcp` token to every catalogued route.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Webhooks per project | 20 | `MAX_WEBHOOKS_PER_PROJECT` |
| URL | `https`, 2048 characters, public host | `is_allowed_webhook_url`, `MAX_WEBHOOK_URL_LENGTH` |
| Description | 1 to 200 characters | `MAX_WEBHOOK_DESCRIPTION_LENGTH` |
| Secret | `whsec_` + 32 random bytes, encrypted at rest | `generate_webhook_secret`, `webhooks.secret_encrypted` |
| Request timeout | 10 seconds, no redirects | `WEBHOOK_REQUEST_TIMEOUT_SECONDS` |
| Tries | 5, exponential backoff from 30 s | `JOB_ATTEMPTS`, `JOB_BACKOFF_DELAY` |
| Error kept per try | 500 characters | `MAX_WEBHOOK_ERROR_LENGTH` |
| Delivery log | 50 by default, 200 at most | `DEFAULT_WEBHOOK_DELIVERY_LIST_LIMIT`, `MAX_WEBHOOK_DELIVERY_LIST_LIMIT` |
| Deliveries kept | 30 days, cleaned nightly at 04:15 | `WEBHOOK_DELIVERY_RETENTION`, `webhook.delete_old_deliveries` |
| Delivery statuses | `pending`, `succeeded`, `failed` | `WebhookDeliveryStatus`, check `webhook_delivery_status` |
| Token scopes | `mcp` (default), `api` | `ApiTokenScope`, check `api_token_scope` |
| Tables | `webhooks`, `webhook_deliveries` (cascade on webhook delete) | migration 0029 |

## Screens and states

Client: [client/src/modules/webhooks](../../client/src/modules/webhooks) (strings in the `integrations` namespace), the token form in [client/src/modules/connect-claude](../../client/src/modules/connect-claude) and the import dialog in [client/src/modules/junit-import](../../client/src/modules/junit-import) (namespace `junitImport`, [runs.md, RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)).

| Screen | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| Webhooks card in `/projects/[projectKey]/settings` | "No webhooks yet." | skeleton ("Loading webhooks") | "Webhooks could not be loaded" + Try again | card hidden | card hidden without `integration.manage` | `webhook.changed` |
| Delivery log drawer (from the webhook's menu) | "No deliveries yet" | skeleton ("Loading deliveries") | "Deliveries could not be loaded" + Try again | – | – | `webhook.changed` |
| Scope choice on `/connect-claude` | – | – | errors as in AUTH-10 | – | – | – |

**Webhooks card** (after the review settings and the Slack and Teams card, before the archive card):
- A table with one row per webhook: the URL, its description and `Secret whsec_…a1b2`; the chosen events ("All events" when all 7 are chosen); Active or Off; the last delivery's status badge (Pending, Delivered, Failed) and time, or "None yet".
- *Add webhook* opens a form: Payload URL (required), Description (optional, 200 characters), the 7 events as checkboxes (all checked for a new webhook, shown with their wire names) and an Active switch. The client checks what it can before sending: empty URL, more than 2048 characters, not `https://`, no dot in the host, user info ("Use an https:// address.", "Enter a valid public https URL."), more than 200 characters, no event ("Choose at least one event."). `WEBHOOK_URL_INVALID` from the server shows on the URL field; `CONFLICT` shows "A project can have 20 webhooks. Remove one to add another." in the form.
- After *Add webhook* the signing secret is shown once in a dialog with a copy button, "Copy it now. You will not see this secret again." and how the signature is built. Done forgets it; it is never kept in the query cache.
- Each row's menu: *Delivery log*, *Edit* (sends only the changed fields), *Rotate secret* (asks first, then shows the new secret once, like a new webhook) and *Remove* (asks first).
- At 20 webhooks, *Add webhook* is disabled and the limit text is shown.

**Delivery log** (a drawer): the webhook's URL and "Deliveries of the last 30 days, newest first.", then up to 50 deliveries: the event (and "Redelivery" for a copy), the status badge, the number of tries, the receiver's HTTP status and the error text, and the time of the last try. Each row can show its JSON payload (with a copy button) and *Redeliver* it (`POST …/redeliver/{delivery_id}`, toast "Delivery queued again"); the new delivery appears at the top.

**Scope choice** (AUTH-10 AC8): the token form has a fourth field, "Used for": "Claude Code (MCP)" (the default) or "CI and scripts (REST API)", with a one-line description of each. For an `api` token the created dialog shows a `curl` call that imports `results.xml` into the `Staging` environment with the token in `Authorization: Bearer`, and "Store the token as a CI secret…", instead of the plugin install command. A Viewer choosing `api` is told the token "can read runs, failures and test cases but not import results". The token table has a "Used for" column (Claude Code, REST API).

## API

| Method and path | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/webhooks` | `integration.manage` |
| `POST /api/projects/{project_key}/webhooks` | `integration.manage` |
| `PATCH /api/projects/{project_key}/webhooks/{webhook_id}` | `integration.manage` |
| `DELETE /api/projects/{project_key}/webhooks/{webhook_id}` | `integration.manage` |
| `GET /api/projects/{project_key}/webhooks/{webhook_id}/deliveries?limit=` | `integration.manage` |
| `POST /api/projects/{project_key}/webhooks/{webhook_id}/redeliver/{delivery_id}` | `integration.manage` |
| `POST /api/me/api-tokens` (`scope`) | `api_token.create` |
| `POST /api/projects/{project_key}/runs/import` | `run.start` (session or `api` token) |

Jobs: `webhook.deliver` (queue `integrations`), `webhook.delete_old_deliveries` (queue `maintenance`, nightly).

## Errors

| ErrorCode | When |
| --- | --- |
| `WEBHOOK_URL_INVALID` (422) | Not `https`, no host, user info, or a private, loopback or link-local host |
| `CONFLICT` (409) | A 21st webhook in a project |
| `NOT_FOUND` | Another project's webhook or delivery; a token used on another project's route |
| `TOKEN_SCOPE_NOT_ALLOWED` (403) | An `api` token on a route that isn't token-allowed, on a hook route or on `/mcp` |
| `INVALID_API_TOKEN` (401) | A bad, expired or revoked token on a token-allowed route |
| `NOT_SIGNED_IN` (401) | An `mcp` token on a REST route that needs a session |
| `JUNIT_INVALID`, `JUNIT_NO_MAPPED_TESTS`, `FILE_TOO_LARGE`, `UNKNOWN_REFERENCE` | JUnit import ([RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)) |
| `PERMISSION_DENIED`, `PROJECT_ARCHIVED` | Missing capability, or any webhook route on an archived project |

## Later

- A "send test event" button for webhooks (Slack and Teams channels have one).
- Richer payloads (names, counts and links) if receivers ask for them; today they read details from the REST API.

## Differences from the proposals

- The proposal has `webhooks (project_id, url, secret_encrypted, events, active)`. The code adds `description`, `created_by` and `created_at`, and names the flag `is_active`.
- The secret is made by the server (shown once, rotatable), not typed in by the Admin.
- The signature covers the timestamp too (`<timestamp>.<body>`), against replays.
- An `api` token is limited to the import and the run, failure and case reads in this wave; more routes can be marked `token_allowed` later.

## Open points

- The webhook URL check (`utils/webhook_url.py`) and the chat channel URL check (`utils/chat_channel_url.py`) apply the same rules in two files; they can be merged into one.

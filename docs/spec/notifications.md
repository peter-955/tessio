# Notifications

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.12 · Story prefix NOTIF · Index: [README](README.md)

## Purpose

Tell a person, inside Tessio, when work lands on them: a gap assigned to them or their role, a failure assigned to them, or a run they started or follow finished. Notifications arrive live over the event stream and, if the person wants, by email. A project can also post its events to Slack or Teams channels. Server: [server/app/modules/notifications](../../server/app/modules/notifications) (notifications, email, settings) and the chat channel files of [server/app/modules/integrations](../../server/app/modules/integrations). Client: [client/src/modules/notifications](../../client/src/modules/notifications), [client/src/modules/notification-preferences](../../client/src/modules/notification-preferences) (profile card) and [client/src/modules/chat-channels](../../client/src/modules/chat-channels) (project settings card).

## Roles and capabilities

- Every signed-in user reads and marks only their own notifications. No project capability is needed.
- Notifications go only to active members of the project.
- Every signed-in user reads and changes only their own notification settings.
- Chat channels need `integration.manage` (project Admin; a workspace admin acts as Admin).

## User stories

### NOTIF-1 Bell and panel (WBS 3.12.1)

As a team member, I want a bell with my unread count, so that I notice new work.

- AC1: The top bar bell shows the unread count from `GET /api/notifications/unread-count` (its label reads "Notifications, {count} unread").
- AC2: Opening the panel lists notifications from `GET /api/notifications`, newest first, 20 per page by default (up to 100), with "Load more" (cursor paging).
- AC3: The filter switches between All and Unread (`unreadOnly=true`).
- AC4: Each item links to its target: the story's Gaps tab (`?tab=gaps`), the failure, or the run.
- AC5: "Mark as read" calls `PUT /api/notifications/{notification_id}/read`; "Mark all as read" calls `PUT /api/notifications/read-all`.
- AC6: Empty states: "No notifications yet" and "You're all caught up".

### NOTIF-2 Gap assigned (WBS 3.12.1)

As a BA, I want to know when a gap is routed to me or my role, so that I answer it before the run.

- AC1: Raising, reopening or reassigning a gap sends `gap_assigned` to the assignee, or to every active member of the role queue when no one is assigned.
- AC2: The person who caused it is not notified.
- AC3: The item reads "Gap assigned to you on {storyKey}" with the question (cut at 200 characters).

### NOTIF-3 Failure assigned (WBS 3.12.1)

As a Dev, I want to know when a failure is assigned to me, so that I start the fix.

- AC1: Assigning a failure sends `failure_assigned` to the new assignee, unless they assigned it to themselves.
- AC2: The item reads "Failure assigned to you on {storyKey}" with "{testCaseCode} · {testCaseTitle}".

### NOTIF-4 Run finished (WBS 3.12.1)

As a QC, I want to know when a run finishes, so that I review the results.

- AC1: Finishing a run (Claude, manual, or the stale-run abort) sends `run_finished` to the person who started it and to every active QC member of the project.
- AC2: The item reads "Run passed on {storyKey}", "Run failed on {storyKey}" or "Run aborted on {storyKey}", with "{passed} passed · {failed} failed · {blocked} blocked".
- AC3: A suite run ([suites-and-plans.md](suites-and-plans.md#suite-5-finish-a-suite-run-and-its-report-wbs-91)) sends `suite_run_finished` instead, to the same people. Its payload is `runId`, `testSuiteId`, `testSuiteName` (cut to 200 characters), `outcome`, `passedCount`, `failedCount` and `blockedCount`; it has no story. The bell shows it as "Suite run passed: {name}" (or failed, aborted) with the counts and the suites icon, and links to the run.

### NOTIF-5 Live delivery (WBS 3.12.1)

As a user, I want new notifications to appear without reloading, so that the count is always right.

- AC1: Each new notification publishes `notification.created` to its recipient only.
- AC2: The client refreshes the list and the unread count when it arrives.

### NOTIF-6 Email notifications (WBS 3.12.2)

As a team member, I want an email when work lands on me, so that I see it even when Tessio is closed.

- AC1: Every notification kind can also go out by email. When a notification is sent, the server checks each recipient's email setting for that kind ([NOTIF-7](#notif-7-notification-settings-wbs-3133)) and queues one `notification.email` job per recipient who wants it, on the `email` queue (ADR 0006). The API never talks to the mail server.
- AC2: The worker reads the recipient again when it runs the job: a user who is no longer active, or who turned email off for that kind since, gets nothing. It then sends the mail through SMTP (the `SMTP_*` settings). If SMTP fails, the job fails and BullMQ tries again (5 tries, 30 s exponential backoff, like every job).
- AC3: The email is plain text in the recipient's language (`users.language`: English, French or Vietnamese). Subject: `[{projectKey}] {title}`, where the title is the bell text of [NOTIF-2](#notif-2-gap-assigned-wbs-3121) to [NOTIF-4](#notif-4-run-finished-wbs-3121) ("Gap assigned to you on SHOP-12", "Écart qui vous est attribué sur SHOP-12", "Khoảng trống được giao cho bạn ở SHOP-12"). Line breaks in a name never reach the subject.
- AC4: The body has a greeting with the recipient's name, the title, the detail (the gap question, "{testCaseCode} · {testCaseTitle}", or the counts "{passed} passed · {failed} failed · {blocked} blocked"), the project ("Project: {name} ({key})"), a link to the target (the same targets as the bell: the story's Gaps tab, the failure, the run; for `report_ready`, the run, plan or story the report is about) and a footer that says why the mail came, with a link to `/profile` to change it.
- AC5: The texts live in the server (`NOTIFICATION_EMAIL_TEXTS`), one set per language, so the worker needs no client code.

### NOTIF-7 Notification settings (WBS 3.13.3)

As a team member, I want to choose, for each kind of notification, whether I get it in Tessio and by email, so that I'm told only about what matters to me.

- AC1: `GET /api/me/notification-preferences` returns one row per kind, in `NotificationKind` order: `{ kind, inApp, email }`. Only the signed-in user's own settings; no project capability.
- AC2: Defaults (nothing saved yet): in-app on for every kind; email on for `gap_assigned` and `failure_assigned`, off for the others (`EMAIL_ON_BY_DEFAULT_KINDS`). A kind added later starts in-app on and email off.
- AC3: `PATCH /api/me/notification-preferences` takes `{ preferences: [{ kind, inApp?, email? }] }`. A left-out field or kind keeps its setting; a kind listed twice gives `INVALID_REQUEST`. The reply is the full list, as in AC1.
- AC4: With in-app off for a kind, no notification row is stored and no `notification.created` is sent for it to that user (the bell stays quiet); email still follows its own setting.
- AC5: Settings are per user and apply to every project. They are stored in `notification_preferences` (user, kind, channel `in_app` or `email`, on or off; migration 0028); only changed values are stored.
- AC6: A "Notifications" card on `/profile`, after "Preferences" ([notification-preferences-card.tsx](../../client/src/modules/notification-preferences/components/notification-preferences-card/notification-preferences-card.tsx)), says "Choose what reaches you in Tessio and by email. Emails go to {email}. These settings apply to every project." It shows a table with one row per kind from AC1 (in the server's order): the kind's name and a one-line description ("Gap assigned to me", "Failure assigned to me", "Run finished", "Suite run finished", "Report ready"), and an "In Tessio" and an "Email" checkbox (named "In Tessio: {kind}" and "Email: {kind}" for screen readers). A note under the table says that with In Tessio off the bell stays quiet for that kind and email follows its own setting.
- AC7: "Save notification settings" is enabled only when a checkbox differs from the saved value. It sends `PATCH /api/me/notification-preferences` with only the changed kinds and only their changed fields (for example `{ preferences: [{ kind: "run_finished", email: true }] }`); undoing a change disables Save again. The reply replaces the cached list, and the card shows "Notification settings saved.". The checkboxes follow a newer saved list from the server.
- AC8: While loading, the card shows a skeleton ("Loading notification settings"); on an error, "Notification settings could not be loaded" + Try again.

### NOTIF-8 Slack and Teams channels (WBS 9.6)

As a project Admin, I want the project's events posted to a Slack or Teams channel, so that the team sees results where it already talks.

- AC1: A chat channel belongs to one project: kind `slack` or `teams`, a name (1 to 80 characters, unique in the project in any case), the incoming webhook URL that Slack or Teams gives, the events it gets, and on or off. At most 20 per project. No Slack app and no Teams bot: only incoming webhook URLs.
- AC2: Events are the seven public events of `IntegrationEvent`: `run.started`, `run.finished`, `failure.opened`, `failure.status_changed`, `gap.raised`, `story.signed_off`, `plan.signed_off`. A channel needs at least one; they are stored in that order, without repeats.
- AC3: The webhook URL must be `https`, with a host, without a user name or password, and not `localhost`, a `.local`, `.localhost`, `.internal`, `.lan` or `.home.arpa` name, a one-word host, or a private, loopback, link-local, reserved or multicast IP address; otherwise `WEBHOOK_URL_INVALID` (422). The host is checked after IDNA conversion (so `127。0。0.1` counts as `127.0.0.1`). A host whose last label is a number (decimal or `0x` hex) is treated as an IP address: it must be a plain dotted IPv4 address, so short, hex, octal or single-number forms (`127.1`, `0x7f.0.0.1`, `2130706433`, `0177.0.0.1`) are refused. An IPv4-mapped IPv6 address (`[::ffff:10.0.0.8]`) is checked as its IPv4 address. The check runs on create and on a new URL.
- AC4: The URL is a secret. It is stored encrypted with the secrets key (AES-256-GCM, like test-data secrets) and never returned: replies carry `webhookUrlMasked`, the host plus the last 4 characters ("https://hooks.slack.com/…9876"; no characters when the path is shorter than 12). A new URL replaces the old one and clears the last delivery status. Logs never hold the URL: `configure_logging` sets the `httpx` and `httpcore` loggers to `WARNING`, so the HTTP client's per-request INFO line (which holds the full URL) is never written, and Sentry runs without its httpx integration, so no breadcrumb holds the URL either. Delivery errors keep only a fixed reason and the HTTP status.
- AC5: Routes (all `integration.manage`, so project Admins; refused on an archived project with `PROJECT_ARCHIVED`): `GET …/chat-channels`, `POST …/chat-channels` (201), `PATCH …/chat-channels/{chat_channel_id}` (only the sent fields change; the kind cannot change), `DELETE …/chat-channels/{chat_channel_id}` (204). Each change publishes `chat_channel.changed`.
- AC6: `POST …/chat-channels/{chat_channel_id}/test` posts "Tessio test message" ("This channel is connected to the Tessio project {name} ({key}).", the chosen events, a link to project settings) right away, from the API. On success it returns the channel with `lastDeliveryStatus: "delivered"`; when Slack or Teams refuses it or cannot be reached it records `failed` with the reason and gives `CHAT_DELIVERY_FAILED` (502) with that reason.
- AC7: Delivery of events: the worker listens to the live events on Redis (the shared `LiveEventListener`). For an event that maps to an `IntegrationEvent`, it queues one `chat.deliver` job (queue `integrations`) per active channel of that project that has the event. The job reads the channel again (removed, turned off or no longer subscribed: nothing is sent), reads the target (run, failure, gap, story or plan; gone: nothing is sent), builds the message and posts it.
- AC8: Messages are in English (a channel is shared, so there is no user language). Title, an optional text and facts:
  - `run.started`: "Suite run started: {suiteName}", "Run started on {storyKey}" (story title), or for a run with neither a suite nor a story (a JUnit import without a suite, [RUN-17](runs.md#run-17-import-junit-results-from-ci-wbs-96)) "{executor} run started · {environmentName}" ("CI run started · Staging"); Executor, Environment, Started by.
  - `run.finished`: "Suite run passed/failed/aborted: {suiteName}", "Run passed/failed/aborted on {storyKey}", or "{executor} run passed/failed/aborted · {environmentName}" for a run with neither; Passed, Failed, Blocked, Skipped (from the run report), Executor, Environment.
  - `failure.opened`: "Failure opened on {storyKey}", "{testCaseCode} · {testCaseTitle}"; Status, Assignee.
  - `failure.status_changed`: "Failure {testCaseCode} is now {status}", the case title; Story, Assignee.
  - `gap.raised`: "Gap raised on {storyKey}", the question; Severity, Assigned to (person, or the role), Raised by.
  - `story.signed_off`: "Story signed off: {storyKey}", the story title; Signed off by.
  - `plan.signed_off`: "Plan signed off: {name}"; Signed off by, Target date.
  Each has an "Open in Tessio" link to the run, failure, story Gaps tab, story or plan, and the footer "Tessio · {projectName}". Text is cut at 500 characters, titles at 150.
- AC9: Slack gets Block Kit: `text` (the title, for the notification, with `&`, `<` and `>` escaped), then blocks `header` (plain text, 150 characters at most), `section` with the text (mrkdwn, `&`, `<` and `>` escaped, then cut to 3000 characters without splitting an escaped character), `section` with up to 10 `fields` ("*Label*\nvalue", escaped and cut the same way at 2000), `actions` with a button to the link, and a `context` with the footer.
- AC10: Teams gets the Workflows webhook format ("Post to a channel when a webhook request is received"): `{"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "contentUrl": null, "content": <Adaptive Card 1.4>}]}`, the card holding a bold title `TextBlock`, the text, a `FactSet` and the footer, with an `Action.OpenUrl` "Open in Tessio". **Not verified:** spike S7 was not run against a real Teams Workflows webhook, so this payload has only been checked against Microsoft's documented format, not by a real channel.
- AC11: Retries: a timeout, a network error, HTTP 429 or a 5xx makes the job fail, so BullMQ tries it again (5 tries, 30 s exponential backoff); any other answer that is not 2xx (for example 404 or 410 for a removed webhook) is final. Redirects are not followed. Each try records `lastDeliveryStatus` (`delivered` or `failed`), `lastDeliveryAt` and `lastDeliveryError` on the channel and publishes `chat_channel.changed`.
- AC12: Live events are fire and forget: an event sent while the worker is down is not posted.
- AC13: The chat channels card in project settings is the client part ([SET-7](settings.md#set-7-chat-channels-wbs-96)): list, add, edit, turn off or on, test message and delete.

### NOTIF-9 Report ready (WBS 9.5)

As a team member who asked for a report export, I want to be told when the file is ready, so that I can download it.

- AC1: When a `report.export` job has stored the file ([INS-7](insights.md#ins-7-export-a-run-plan-or-story-report-wbs-95-3107)), the requester (only them) gets `report_ready`. There is no actor.
- AC2: The payload is `fileId`, `fileName`, `format` (`md` or `pdf`), `source` (`run`, `plan` or `story`), `sourceId` (the run id, the plan id or the story's Jira key) and `sourceLabel` (the story key and title, the suite name or the plan name, masked against the project's secrets). `fileName` and `sourceLabel` are cut to 200 characters.
- AC3: The download link comes from `GET /api/projects/{project_key}/files/{fileId}` (`file.download`, 5 minutes), as for other stored files.
- AC4: Email for `report_ready` is off by default; a user can turn it on in the notification settings (NOTIF-7).
- AC5: `report.ready` is published with it (`user_id` = the requester, `ids.fileId`, `ids.format`), next to the `notification.created` of AC1.
- AC6: In the bell, the item reads "Report ready: {sourceLabel}" with the file name, links to the run's report tab, the plan or the story, and has *Download the report*, which fetches the link, opens it in a new tab and marks the item read ([insights.md, Export button](insights.md#export-button-run-plan-story)).

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Kinds | `gap_assigned`, `failure_assigned`, `run_finished`, `suite_run_finished`, `report_ready` | `NotificationKind` |
| Run outcomes in the payload | `passed`, `failed`, `aborted` | `RunOutcome` |
| Page size | 20 by default, 100 at most | `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` |
| Text cut in the payload | 200 characters, ending with `…` | `MAX_PAYLOAD_TEXT_LENGTH` |
| Kinds that skip the actor | `gap_assigned`, `failure_assigned` | `ACTOR_EXCLUDED_KINDS` |
| Channels | `in_app`, `email` | `NotificationChannel` |
| Email on by default | `gap_assigned`, `failure_assigned` (in-app is on by default for every kind) | `EMAIL_ON_BY_DEFAULT_KINDS` |
| Email languages | `en`, `fr`, `vi` (the user's language) | `NOTIFICATION_EMAIL_TEXTS` |
| Chat channel kinds | `slack`, `teams` | `ChatChannelKind` |
| Chat channel name | 1 to 80 characters, unique in the project (any case) | `MAX_CHAT_CHANNEL_NAME_LENGTH` |
| Chat channels per project | 20 | `MAX_CHAT_CHANNELS_PER_PROJECT` |
| Chat webhook URL | `https`, public host, 2048 characters at most | `is_allowed_chat_webhook_url`, `MAX_CHAT_WEBHOOK_URL_LENGTH` |
| Chat delivery error kept | 300 characters | `MAX_CHAT_DELIVERY_ERROR_LENGTH` |
| Chat jobs | `notification.email` on queue `email`; `chat.deliver` on queue `integrations` | `JobName`, `QueueName` |

- The payload keeps the target ids and the texts shown, so an item still reads correctly after the target changes.

## Screens and states

| Where | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| Bell and panel (top bar, every page) | "No notifications yet"; Unread: "You're all caught up" | "Loading notifications" | "Notifications could not be loaded" + Try again | items still listed | – | `notification.created` |
| Notifications card (`/profile`) | – (always one row per kind) | skeleton, "Loading notification settings" | "Notification settings could not be loaded" + Try again | – (per user, not per project) | – (own settings) | – (only this user changes them) |
| Chat channels card (project settings) | "No chat channels yet." | skeleton, "Loading chat channels" | "Chat channels could not be loaded" + Try again | card hidden | card hidden without `integration.manage` | `chat_channel.changed` |

## API

| Method and path | Who |
| --- | --- |
| `GET /api/notifications?unreadOnly=&cursor=&limit=` | signed in, own |
| `GET /api/notifications/unread-count` | signed in, own |
| `PUT /api/notifications/read-all` | signed in, own |
| `PUT /api/notifications/{notification_id}/read` | signed in, own |
| `GET /api/me/notification-preferences` | signed in, own |
| `PATCH /api/me/notification-preferences` | signed in, own |
| `GET /api/projects/{project_key}/chat-channels` | `integration.manage` |
| `POST /api/projects/{project_key}/chat-channels` | `integration.manage` |
| `PATCH /api/projects/{project_key}/chat-channels/{chat_channel_id}` | `integration.manage` |
| `DELETE /api/projects/{project_key}/chat-channels/{chat_channel_id}` | `integration.manage` |
| `POST /api/projects/{project_key}/chat-channels/{chat_channel_id}/test` | `integration.manage` |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Marking a notification that is not the caller's |
| `NOT_SIGNED_IN` | No session |
| `INVALID_REQUEST` | A notification kind listed twice, an unknown kind or event, no events, a name out of range |
| `NOT_FOUND` | A chat channel that is not in the project |
| `CONFLICT` | A chat channel name already used in the project, or a 21st channel |
| `WEBHOOK_URL_INVALID` | A chat webhook URL that is not `https`, has no host, or points to a private, loopback, link-local, reserved or multicast IP address (in any written form of the address) |
| `CHAT_DELIVERY_FAILED` | The test message was refused by Slack or Teams, or they could not be reached (502) |
| `PERMISSION_DENIED` | Chat channels without `integration.manage` |
| `PROJECT_ARCHIVED` | Chat channels of an archived project |

## Later

- HTML email (the email is plain text today).
- Chat messages in the project's language.

## Differences from the proposals

- `run_finished` goes to the starter plus the project's QC members (assumption 3.12.1); the proposals did not name the recipients.
- The settings also let a user turn the in-app notification off per kind (the plan named the channels `in_app` and `email`); the proposal only asked for email settings.
- The chat channel webhook URL check runs when the URL is saved, on the URL's host (after IDNA conversion, and with every written form of an IP address). It does not resolve the host name, so a public name that resolves to a private address is not caught (see Open points).

## Open points

- An automatic failure reopen sends nothing (see [failures.md](failures.md#open-points)).
- Not checked by hand: a `notification.created` frame updating the badge in a signed-in browser (W4 carry-over).
- Not verified against a real system: an email through a real SMTP server, a Slack incoming webhook, and the Teams Workflows payload (spike S7 not run).
- Not checked by hand in a browser: the profile Notifications card and the project Chat channels card (covered by Vitest with a mocked API only).
- The chat URL check does not resolve DNS, so a public host name pointing to a private address would be posted to (DNS rebinding). Slack and Teams URLs are public; resolving at send time is a follow-up.

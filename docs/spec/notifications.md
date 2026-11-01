# Notifications

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.12 · Story prefix NOTIF · Index: [README](README.md)

## Purpose

Tell a person, inside Tessio, when work lands on them: a gap assigned to them or their role, a failure assigned to them, or a run they started or follow finished. Notifications arrive live over the event stream. Server: [server/app/modules/notifications](../../server/app/modules/notifications). Client: [client/src/modules/notifications](../../client/src/modules/notifications).

## Roles and capabilities

- Every signed-in user reads and marks only their own notifications. No project capability is needed.
- Notifications go only to active members of the project.

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

### NOTIF-5 Live delivery (WBS 3.12.1)

As a user, I want new notifications to appear without reloading, so that the count is always right.

- AC1: Each new notification publishes `notification.created` to its recipient only.
- AC2: The client refreshes the list and the unread count when it arrives.

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Kinds | `gap_assigned`, `failure_assigned`, `run_finished` | `NotificationKind` |
| Run outcomes in the payload | `passed`, `failed`, `aborted` | `RunOutcome` |
| Page size | 20 by default, 100 at most | `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` |
| Text cut in the payload | 200 characters, ending with `…` | `MAX_PAYLOAD_TEXT_LENGTH` |
| Kinds that skip the actor | `gap_assigned`, `failure_assigned` | `ACTOR_EXCLUDED_KINDS` |

- The payload keeps the target ids and the texts shown, so an item still reads correctly after the target changes.

## Screens and states

| Where | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| Bell and panel (top bar, every page) | "No notifications yet"; Unread: "You're all caught up" | "Loading notifications" | "Notifications could not be loaded" + Try again | items still listed | – | `notification.created` |

## API

| Method and path | Who |
| --- | --- |
| `GET /api/notifications?unreadOnly=&cursor=&limit=` | signed in, own |
| `GET /api/notifications/unread-count` | signed in, own |
| `PUT /api/notifications/read-all` | signed in, own |
| `PUT /api/notifications/{notification_id}/read` | signed in, own |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Marking a notification that is not the caller's |
| `NOT_SIGNED_IN` | No session |

## Later

- 3.12.2 Email and Slack notifications.
- 3.13.3 Notification settings.

## Differences from the proposals

- `run_finished` goes to the starter plus the project's QC members (assumption 3.12.1); the proposals did not name the recipients.

## Open points

- An automatic failure reopen sends nothing (see [failures.md](failures.md#open-points)).
- Not checked by hand: a `notification.created` frame updating the badge in a signed-in browser (W4 carry-over).

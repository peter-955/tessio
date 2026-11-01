# Readiness review (gap questions)

**Status:** Draft · **Updated:** 2026-11-01

WBS 3.8 · Story prefix GAP · Index: [README](README.md)

## Purpose

Before a run, Claude (or a person) reviews a story, its AC and its test cases, and files **gaps**: questions about a missing AC, an unclear goal, a missing step, missing test data, or anything else. Each gap is routed to the role that can answer it. Every open gap blocks runs on that story. Answers stay in Tessio, so the same question does not come back. Server: [server/app/modules/gaps](../../server/app/modules/gaps) (REST and the MCP tools `raise_gaps` and `get_open_gaps`). Client: [client/src/modules/gaps](../../client/src/modules/gaps). The Claude skill is [claude/skills/review-readiness](../../claude/skills/review-readiness/SKILL.md).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open gaps, MCP `get_open_gaps` | `gap.view` | all |
| Raise gaps (REST or MCP `raise_gaps`) | `gap.raise` | Admin, PM, BA, QC, Dev |
| Answer a gap | `gap.answer` | Admin, PM, BA, QC, Dev |
| Reassign a gap | `gap.reassign` | Admin, PM, BA, QC, Dev |
| Reopen a gap | `gap.raise`, and the caller raised it or is QC or Admin | |
| My gaps inbox | signed in | |

Viewers cannot raise, answer, reassign or be assigned gaps.

## User stories

### GAP-1 Gap list per story (WBS 3.8.1)

As a team member, I want the story's gaps with their type, target, severity and assignee, so that I see what blocks testing.

- AC1: The story's Gaps tab lists gaps from `GET /api/projects/{project_key}/gaps?storyKey=` with a filter Open / Answered / All, with counts.
- AC2: Each card shows the type (Missing AC, Unclear goal, Missing step, Missing test data, Other), severity (High, Medium, Low), target (Story, an AC code, or a case code), data scope for data gaps, the question, who raised it ("via Claude" when raised with an API token), the assignee ("Assigned to {name}", "Assigned to any {role}" or "Unassigned"), and the answer.
- AC3: An assignee who is deactivated shows a Deactivated badge and "Reassign this gap: its assignee is deactivated."
- AC4: The project list also accepts `status` and `mine=true`.

### GAP-2 Raise gaps (WBS 3.8.1, 3.8.2)

As Claude or a team member, I want to file gap questions on a story, AC or case, so that the owners answer them before the run.

- AC1: In the UI, "Raise gap" posts one gap to `POST /api/projects/{project_key}/stories/{jira_key}/gaps` with type, severity (`medium` by default), target type (`story` by default, or `criterion`, `test_case`), target ref (`AC2`, `TC-12`), question (1 to 2000 characters), optional data scope and optional assignee.
- AC2: Through MCP, `raise_gaps(story_key, gaps[])` files 1 to 50 gaps in one call in the token's project. MCP gaps are always routed automatically.
- AC3: A target ref that is not on the story gets `UNKNOWN_REFERENCE` ("{ref} is not on this story."). Case codes are matched without case.
- AC4: The data scope is kept only on `missing_test_data` gaps.
- AC5: The reply lists the new gaps and the story's open gap count. Each new gap sends `gap_assigned` to its assignee or role queue (not to the raiser) and publishes `gap.changed`.

### GAP-3 Automatic routing (WBS 3.8.2)

As a BA, QC or Dev, I want gaps routed to my role by type, so that the right person answers.

- AC1: Routing by type: `missing_ac` and `unclear_goal` → BA; `missing_step` → QC; `missing_test_data` → QC, or Dev when the data scope is `environment`; `other` → Admin.
- AC2: When the routed role has exactly one active member, that person is the assignee.
- AC3: When it has several, the gap goes to the role queue (`assignee_role`) and anyone in that role sees it.
- AC4: When it has none, the same rule is applied to the Admin role. With no active Admin either, the gap goes to the Admin queue.
- AC5: Deactivated users are never chosen.
- AC6: A raiser in the UI may pick an assignee instead ("Automatic (routed by type)" is the default). The assignee must be an active member who is not a Viewer (`ASSIGNEE_NOT_ACTIVE_MEMBER`).

### GAP-4 Answer and resolve (WBS 3.8.3)

As the gap's owner, I want to answer the question, so that the story can be tested.

- AC1: "Answer" asks for the answer (1 to 4000 characters) and calls `PUT /api/projects/{project_key}/gaps/{gap_id}/answer` ("Answer and resolve").
- AC2: Answering resolves the gap (`open` → `resolved`) and records who answered and when. The UI calls resolved gaps "Answered".
- AC3: Any member with `gap.answer` may answer, not only the assignee.
- AC4: Answering a resolved gap gets `GAP_NOT_OPEN`.

### GAP-5 Reopen and reassign (WBS 3.8.3)

As a QC or the person who raised a gap, I want to reopen an answer that does not help, so that the question goes back.

- AC1: "Reopen" (`POST …/gaps/{gap_id}/reopen`) moves `resolved` → `open`, for the raiser, a QC or an Admin. Others get `PERMISSION_DENIED`; an open gap gets `INVALID_STATUS_TRANSITION`.
- AC2: Reopening keeps the assignee when it is still active, otherwise it routes again. It sends `gap_assigned` again and blocks runs again.
- AC3: "Reassign" (`PUT …/gaps/{gap_id}/assignee`) sets an active, non-Viewer member or a role queue ("Any {role}") on an open gap and sends `gap_assigned`. A resolved gap gets `GAP_NOT_OPEN`.

### GAP-6 Open gaps block runs (WBS 3.8.4)

As a QC, I want no run to start while a gap is open, so that we never test on unclear requirements.

- AC1: Starting a Claude run, a manual run or a re-run on a story with any open gap is refused with `OPEN_GAPS_BLOCK_RUN` ("{count} open gaps block runs on this story."). There is no override.
- AC2: The Gaps tab shows "{count} open gaps block runs" while any gap is open.
- AC3: `get_open_gaps(story_key)` returns the open gaps and the open gap count, so Claude can tell whether the story is ready.

### GAP-7 Gap inbox (WBS 3.8.5)

As a BA, I want one list of the gaps waiting for me across my projects, so that I don't have to visit every story.

- AC1: "My gaps" (`/gaps`) lists `GET /api/gaps/inbox`: gaps assigned to me, or to my role queue with no one assigned, in every project I can see that is not archived.
- AC2: The filter is Open (default) or All (`includeResolved=true`). At most 200 gaps are returned ("Showing the {count} most recent gaps.").
- AC3: Each card links to the story's Gaps tab. With nothing waiting: "Nothing waiting for you".

## Rules

| Rule | Value | Code |
| --- | --- | --- |
| Gap types | `missing_ac`, `unclear_goal`, `missing_step`, `missing_test_data`, `other` | `GapType` |
| Severities | `high`, `medium`, `low` | `GapSeverity` |
| Statuses | `open`, `resolved` | `GapStatus` |
| Targets | `story`, `criterion`, `test_case` | `GapTargetType` |
| Data scopes | `project`, `environment` | `GapDataScope` |
| Question length | 2000 characters | `MAX_QUESTION_LENGTH` |
| Answer length | 4000 characters | `MAX_ANSWER_LENGTH` |
| Target ref length | 40 characters | `MAX_TARGET_REF_LENGTH` |
| Gaps per `raise_gaps` call | 50 | `MAX_GAPS_PER_CALL` |
| Inbox size | 200 | `MAX_INBOX_SIZE` |
| Reopening roles | raiser, `qc`, `admin` | `REOPENING_ROLES` |

The gap status diagram is in [user-flows.md](../design/user-flows.md#gap-status).

## Screens and states

| Route | Empty | Loading | Error | Archived | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- | --- |
| Gaps tab of `/projects/[projectKey]/stories/[jiraKey]` | "No open gaps. Runs are not blocked by gaps on this story." / "No answered gaps yet" / "No gaps on this story" | "Loading gaps" | "Gaps could not be loaded" + Try again | actions hidden | Viewer: no actions | `gap.changed` |
| `/gaps` | "Nothing waiting for you" | "Loading gaps" | "Gaps could not be loaded" | archived projects left out | – | `gap.changed` |

## API

| Method and path or MCP tool | Capability |
| --- | --- |
| `GET /api/projects/{project_key}/gaps?storyKey=&status=&mine=` | `gap.view` |
| `GET /api/projects/{project_key}/gaps/{gap_id}` | `gap.view` |
| `POST /api/projects/{project_key}/stories/{jira_key}/gaps` | `gap.raise` |
| `PUT /api/projects/{project_key}/gaps/{gap_id}/answer` | `gap.answer` |
| `POST /api/projects/{project_key}/gaps/{gap_id}/reopen` | `gap.raise` + raiser, QC or Admin |
| `PUT /api/projects/{project_key}/gaps/{gap_id}/assignee` | `gap.reassign` |
| `GET /api/gaps/inbox?includeResolved=` | signed in |
| MCP `raise_gaps(story_key, gaps[])` | `gap.raise` |
| MCP `get_open_gaps(story_key)` | `gap.view` |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_FOUND` | Unknown story or gap |
| `UNKNOWN_REFERENCE` | Target ref not on the story, or a `criterion` or `test_case` target with no ref |
| `ASSIGNEE_NOT_ACTIVE_MEMBER` | Assignee not an active member, or a Viewer |
| `GAP_NOT_OPEN` | Answer or reassign a resolved gap |
| `INVALID_STATUS_TRANSITION` | Reopen an open gap |
| `OPEN_GAPS_BLOCK_RUN` | Start a run while gaps are open |
| `PERMISSION_DENIED` | Missing capability, or reopening someone else's gap without QC or Admin |
| `PROJECT_ARCHIVED` | Any write on an archived project |
| `INVALID_API_TOKEN` | MCP call with a bad, expired or revoked token |

## Later

- Nothing in WBS 3.8 is Later.

## Differences from the proposals

- Answering resolves the gap in one step; there is no separate "resolve" (assumption 3.8.3).
- Gaps can be reopened and reassigned, and raised from the UI; the proposals had only raise and answer.
- Routing with several or no role members (role queue, Admin fallback) was not in the proposals (assumption 3.8.2).
- PM can raise, answer and reassign gaps, as can every non-Viewer role.

## Open points

- The open-gap check takes no lock, so a gap raised while a run starts can slip through (accepted MVP race).
- Not checked in a browser: live `gap.changed` updates and the raise → banner → answer flow (W5 carry-over).

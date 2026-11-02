# Readiness review (gap questions)

**Status:** Draft · **Updated:** 2026-11-02

WBS 3.8 · Story prefix GAP · Index: [README](README.md)

## Purpose

Before a run, Claude (or a person) reviews a story, its AC and its test cases, and files **gaps**: questions about a missing AC, an unclear goal, a missing step, missing test data, or anything else. Each gap is routed to the role that can answer it. Every open gap blocks runs on that story. Answers stay in Tessio, so the same question does not come back. Server: [server/app/modules/gaps](../../server/app/modules/gaps) (REST and the MCP tools `raise_gaps`, `get_open_gaps`, `get_my_gaps`, `answer_gap` and `reassign_gap`). Client: [client/src/modules/gaps](../../client/src/modules/gaps). The Claude skills are [claude/skills/review-readiness](../../claude/skills/review-readiness/SKILL.md) and [claude/skills/answer-gaps](../../claude/skills/answer-gaps/SKILL.md).

## Roles and capabilities

| Action | Capability | Roles |
| --- | --- | --- |
| List and open gaps, MCP `get_open_gaps` | `gap.view` | all |
| Raise gaps (REST or MCP `raise_gaps`) | `gap.raise` | Admin, PM, BA, QC, Dev |
| Answer a gap (REST or MCP `answer_gap`), MCP `get_my_gaps` | `gap.answer` | Admin, PM, BA, QC, Dev |
| Reassign a gap (REST or MCP `reassign_gap`) | `gap.reassign` | Admin, PM, BA, QC, Dev |
| Reopen a gap | `gap.raise`, and the caller raised it or is QC or Admin | |
| My gaps inbox | signed in | |

Viewers cannot raise, answer, reassign or be assigned gaps.

## User stories

### GAP-1 Gap list per story (WBS 3.8.1)

As a team member, I want the story's gaps with their type, target, severity and assignee, so that I see what blocks testing.

- AC1: The story's Gaps tab lists gaps from `GET /api/projects/{project_key}/gaps?storyKey=` with a filter Open / Answered / All, with counts.
- AC2: Each card shows the type (Missing AC, Unclear goal, Missing step, Missing test data, Other), severity (High, Medium, Low), target (Story, an AC code, or a case code), data scope for data gaps, the question, who raised it ("via Claude" when raised with an API token), the assignee ("Assigned to {name}", "Assigned to any {role}" or "Unassigned"), and the answer with who answered it ("via Claude" badge next to "Answered by {name}" when answered with an API token).
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
- AC3: `get_open_gaps(story_key)` returns the open gaps and the open gap count, so Claude can tell whether the story is ready. Each gap names who must answer it: `assignee_name` for one person, or `assignee_role` for a role queue, and `is_assignee_deactivated: true` when that person was deactivated.
- AC4: When gaps block a start, `/tessio:run-story-tests`, `/tessio:run-suite` and `/tessio:rerun-failed` follow the shared procedure [when-gaps-block.md](../../claude/skills/answer-gaps/references/when-gaps-block.md). They don't start the run. They list the open gaps grouped by assignee (the caller's own gaps first, found with `get_my_gaps`, then each person, each role queue, and the gaps that need reassigning), offer `/tessio:answer-gaps <STORY-KEY>` for the caller's gaps, and name who must answer the rest. A suite run is refused with the same `OPEN_GAPS_BLOCK_RUN` while any story with a case in the suite has an open gap ([SUITE-4 AC2](suites-and-plans.md#suite-4-start-a-suite-run-wbs-91)); the procedure takes the blocked stories from the refusal message and, with more than three of them, calls `get_my_gaps()` once without a story key. The message lists at most 20 gaps; when it ends with "; and N more", the procedure takes the candidate stories from the suite context (`stories[].key` and `skipped_cases[].story_key`) and calls `get_open_gaps` for each, because the rest are not named. The message gives no severity, target or deactivated assignee, so those come from the `get_open_gaps` and `get_my_gaps` replies.

### GAP-7 Gap inbox (WBS 3.8.5)

As a BA, I want one list of the gaps waiting for me across my projects, so that I don't have to visit every story.

- AC1: "My gaps" (`/gaps`) lists `GET /api/gaps/inbox`: gaps assigned to me, or to my role queue with no one assigned, in every project I can see that is not archived.
- AC2: The filter is Open (default) or All (`includeResolved=true`). At most 200 gaps are returned ("Showing the {count} most recent gaps.").
- AC3: Each card links to the story's Gaps tab. With nothing waiting: "Nothing waiting for you".

### GAP-8 Answer gaps with Claude (WBS 9.18)

As a BA, PM, QC, Dev or Admin, I want to answer the gaps waiting for me from my own terminal, so that blocked stories can be tested again in minutes.

- AC1: The `/tessio:answer-gaps` skill uses the three gap MCP tools `get_my_gaps`, `answer_gap` and `reassign_gap` (plus `set_test_data` and `get_story_context`, see AC9). The gap tools call the same use cases as the REST routes, so the rules, errors, `gap_assigned` and `gap.changed` are the same as in GAP-4 and GAP-5. Each works in the token's project only; a gap of another project gets `NOT_FOUND`.
- AC2: `get_my_gaps(story_key?)` (`gap.answer`) lists the open gaps assigned to the caller, or to the role queue of the caller's role with no one assigned, optionally for one story (`NOT_FOUND` for an unknown story). At most 50 gaps come back, high severity first, then by story key and age; `gap_count` is the full count. Each gap has its story key, type, severity, data scope, question, `is_assigned_to_me` (false for a role-queue gap), who raised it and its target:
  - a criterion target has the AC text;
  - a case target has the case title, version, preconditions and steps of its current version;
  - up to three `similar_answers` (question, answer, story key) from resolved gaps of the project whose question or answer matches the question, from the same story first, then the best matches of the project.
- AC3: The `get_my_gaps` reply also lists each story of those gaps with its open gap count (everyone's, not only the caller's) and `is_ready`, and the `assignees` a gap can be reassigned to (active members who are not Viewers, with name and role). When a listed gap is of type `missing_test_data`, it also has `test_data_url`, the project's Test data page (`CLIENT_URL` + `/projects/{project_key}/test-data`), so Claude can send the person there for a secret.
- AC4: `answer_gap(gap_id, answer)` (`gap.answer`) answers and resolves an open gap as `PUT …/gaps/{gap_id}/answer` does (answer 1 to 4000 characters, trimmed), records who answered and the API token used, and replies with the status and the story's open gap count and `is_ready`.
- AC5: `reassign_gap(gap_id, assignee_user_id? | assignee_role?)` (`gap.reassign`) works as `PUT …/gaps/{gap_id}/assignee`. Exactly one of the two is given, and the role is never `viewer` (`INVALID_REQUEST`). The reply names the new assignee or role queue.
- AC6: Viewers get `PERMISSION_DENIED` from all three tools, and an archived project gets `PROJECT_ARCHIVED` (nothing can be answered there).
- AC7: A gap answered with an API token shows "via Claude" next to the answer, as a raised gap does (REST field `isAnsweredViaClaude`). An answer typed in the app is not "via Claude"; a later answer after a reopen replaces the flag.
  - On the gap card (story Gaps tab and `/gaps`), the badge sits in the answer box, beside "Answered by {name} · {date}". The "via Claude" badge in the card's top row stays about who raised the gap, so a gap raised and answered with Claude shows both.
  - The badge text is the `gaps` namespace key `badge.viaClaude` in EN ("via Claude"), FR ("via Claude") and VI ("qua Claude").
- AC8: Similar-answer search uses Postgres full-text search: a generated column `gaps.search_vector` (`to_tsvector('simple', question || ' ' || coalesce(answer, ''))`, GIN index). The search terms are the question's words of 3 or more letters, without common English question words (`SEARCH_STOP_WORDS`) and repeats, at most 20, matched with OR and ranked with `ts_rank`. A question of only common words gets no suggestions.
- AC9: The skill [`/tessio:answer-gaps [STORY-KEY | mine]`](../../claude/skills/answer-gaps/SKILL.md) (Admin, PM, BA, QC, Dev) works through the caller's gaps from `get_my_gaps`, with `get_story_context` for each story:
  - It keeps the high-severity-first order and puts related gaps (same target, same data key, same question) next to each other.
  - For each gap it says the question in plain words and what it blocks (the AC or case, and every run on the story), and offers up to three suggested answers, each with one source: the story or an AC, an earlier answer from `similar_answers`, existing test data (never a secret's value), or product code (`path:line`) when Claude Code runs in a folder that holds the product's source code. A suggestion without a source is not offered; with none, Claude says "I found no source for this" and asks openly.
  - It asks with Claude Code's question prompt (`AskUserQuestion`), up to four gaps per prompt, so one key press picks a suggestion, **Not mine (reassign)** or **Skip**; the free-text choice is "write my own". Reassigning offers the role queue that fits the gap type and its members from `assignees`.
  - Before saving, it shows the whole batch (answers, test data with scope, reassignments, skips) and saves only after **Save all**. Then it calls `set_test_data` for missing plain data (before the answer), `answer_gap` and `reassign_gap`. A PM or BA gets `PERMISSION_DENIED` from `set_test_data`: the answer is still saved, and Claude says a QC, Dev or Admin must add the value.
  - It never asks for a secret value: for a secret it gives `test_data_url`. It never edits cases, Jira, files or code.
  - At the end it shows per story the open gaps left and whether runs are unblocked, offers `/tessio:run-story-tests <STORY-KEY>` for a ready story, follows the blocked-run procedure (GAP-6 AC4) for gaps of other people, and lists the cases the answers suggest updating, for QC.

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
| Gaps per `get_my_gaps` reply | 50 | `MAX_MY_GAPS` |
| Similar answers per gap | 3 | `MAX_SIMILAR_ANSWERS` |
| Search terms per question | 20, each at least 3 letters | `MAX_SEARCH_TERMS`, `MIN_SEARCH_TERM_LENGTH` |
| Search configuration | `simple` (no language stemming) | `SEARCH_CONFIGURATION` |
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
| MCP `get_my_gaps(story_key?)` | `gap.answer` |
| MCP `answer_gap(gap_id, answer)` | `gap.answer` |
| MCP `reassign_gap(gap_id, assignee_user_id?, assignee_role?)` | `gap.reassign` |

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
| `INVALID_REQUEST` | `reassign_gap` without exactly one of `assignee_user_id` and `assignee_role`, or with the role `viewer` |

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
- GAP-8: the stop-word list is English only; French and Vietnamese questions still match, but their common words are not left out.
- GAP-8: the `/tessio:answer-gaps` skill and the blocked-run procedure are checked only by the plugin file tests and `claude plugin validate`; the dry run in a real Claude Code session against a local server (answer two gaps, reassign one, skip one) is not done yet.
- GAP-8: the skill offers `/tessio:run-story-tests` for a ready story; `/tessio:run-scripts` is offered once script runs exist (W12).

# Execution log: what Claude did during a run

**Status:** Accepted
**Date:** 2026-11-01
**WBS:** [3.10.10](../wbs/wbs.md#310-runs) (log on the run page), [4.13](../wbs/wbs.md#4-server-python--fastapi-adr-0004-details-in-the-server-proposal) (log storage), [5.13](../wbs/wbs.md#5-claude-integration) (log upload hook)
**Related:** [runs spec](../spec/runs.md), [Tessio plugin](../../claude/README.md), [ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)

## Decisions at a glance

| Area | Decision (Peter, 2026-11-01) |
| --- | --- |
| What is captured | Claude's **notes and actions**: its visible text between actions, every tool call with its input and output, the time each took, and the run's token usage. |
| How | When `finish_run` returns, a plugin hook reads Claude Code's session log, keeps the part of this run, cleans it and uploads it once. No extra Claude tokens. |
| Live or after | After the run. Live progress per case stays as it is today. |
| Secrets | Masked twice: by the hook, with the values `resolve_data` returned, and by the server, with the environment's secret values, as reports are today. |
| Screenshots | Taken out of the log. Each step already has its own screenshot. |
| Who can read it | Everyone with `run.view` on the project, like the run itself. |
| Which sessions | Test runs only (`run-story-tests`, `rerun-failed`). |
| Kept for | As long as the run, like screenshots. |

## 1. Why

Today a run keeps, for each step, the status, actual result, error and screenshot, plus Claude's summary and the report. When a case fails, or passes unexpectedly, the tester can't see **how** Claude got there: which page it opened, what it clicked and typed, what it read on the page, or why it decided the step failed.

## 2. What Claude Code's session log holds

Checked on 2026-11-01 against a real session log (`transcript_path`, one JSON object per line):

| Entry | Holds |
| --- | --- |
| `type: assistant` | `message.content` blocks: `text` (Claude's visible notes), `tool_use` (`id`, `name`, `input`) and `thinking`. The thinking text is stored empty, so the log shows Claude's visible notes, never its hidden reasoning. `message.usage` holds the tokens of that request. |
| `type: user` | `tool_result` blocks: `tool_use_id`, `content` (text or images) and `is_error` |
| Every entry | `timestamp`, `uuid`, `sessionId` |
| Other types | Settings, snapshots, request metadata: ignored |

The format is Claude Code's own, not a published contract. So the hook reads only the fields above, skips anything it doesn't know, and turns the result into **Tessio's own log format** (§3). The server and the client never read Claude Code's format.

## 3. The hook (WBS 5.13)

`claude/hooks/upload_run_log.py`: a `PostToolUse` hook on `mcp__plugin_tessio_tessio__finish_run`, using only the standard library like the screenshot hook.

1. Read `transcript_path` and `tool_input.run_id` from the hook input.
2. Find this run's slice of the log: from the `start_run` result that holds the `run_id`, to the `finish_run` call.
3. Build the entries, in order:

   | Entry kind | From | Fields |
   | --- | --- | --- |
   | `note` | an assistant `text` block | `at`, `text` |
   | `action` | a `tool_use` plus its `tool_result` | `at`, `tool`, `input` (JSON), `output` (text), `is_error`, `duration_ms` (result time minus call time) |

4. Clean the entries:
   - replace every value `resolve_data` returned in this slice with `••••`, everywhere;
   - replace image blocks with `[screenshot]`;
   - cut each `output` and each `text` to 4000 characters, and each `input` to 4000 characters of JSON.
5. Add up `usage` once per API request (several log lines share one request id): input, cache creation, cache read and output tokens.
6. Send it all once: `POST /api/runs/{run_id}/log` with the plugin's token. If the network fails or the server answers 5xx, keep it in `~/.tessio/pending-run-logs/<run_id>.json` and retry on the next hook run. (As built: a folder of its own, because the screenshot hook rewrites `pending-uploads.jsonl` with only its own lines.)
7. Always exit 0. A missing log never breaks the run.

Limits: 3000 entries per run (the first 3000 are kept and the log is marked cut) and 10 MB per request.

## 4. Server (WBS 4.13)

- `POST /api/runs/{run_id}/log`, API token, `run.start`, from the run's starter only, after the run has finished, at most 24 hours after it. Sending it again replaces the earlier log.
- The server masks every text again with the environment's secret values (`SecretMasker`). Then it **assigns each entry to a case**: entries up to a `record_case_result` call belong to that call's `case_id`. Entries before the first case are `setup` (such as the health check); entries after the last case are `wrap_up`.
- Table `run_log_entries`: `run_id`, `position`, `test_case_id` (null for setup and wrap-up), `phase` (`setup`, `case`, `wrap_up`), `kind`, `at`, `tool`, `input` (JSONB), `output`, `is_error`, `duration_ms`. As built, the received time, the cut flag and the four token counts live in a table `run_logs` of a separate module `run_logs`, so the `runs` table and code stay untouched.
- `GET /api/projects/{project_key}/runs/{run_id}/log?caseId=` (`run.view`) returns the entries, for one case or for the whole run.
- Live event `run.log_received`, so an open run page shows the log when it arrives.

## 5. On the run page (WBS 3.10.10)

- As built, the timeline is a **Log** tab grouped into Setup, one section per case and Wrap-up, rather than a section under each case's steps, with the time from the first entry and the duration.
- Actions get a plain label, and open to show their input and output:

  | Tool | Label |
  | --- | --- |
  | Claude in Chrome `navigate` | Opened `<url>` |
  | `computer` click, type, key, scroll | Clicked, Typed `<text>`, Pressed `<key>`, Scrolled |
  | `form_input` | Filled a field with `<value>` |
  | `find`, `read_page`, `get_page_text` | Looked for `<query>`, Read the page |
  | `computer` screenshot | Took a screenshot |
  | `file_upload` | Attached a file |
  | `Bash` | Ran `<command>` |
  | A Tessio tool | Tessio: `<tool>` |
  | Anything else | `<tool name>` |

- A new **Log** tab on the run shows the whole timeline, with setup and wrap-up, plus the token counts and tokens per case.
- Until the log arrives: "Claude's log arrives when the run finishes." After 24 hours without one: "No log was received for this run."
- Manual runs have no log.

## 6. Not in this proposal

- Live streaming of each action while the run is going.
- Logs of subagents that Claude starts during a run. Their entries live in separate files.
- Searching across logs.

## 7. Open points

- The hook depends on Claude Code's session log format. The parser has fixture tests built from a real log, and a run whose log can't be read simply has no log.
- Not tried on a real run with Claude in Chrome yet. Labels for any Chrome tool missing from §5 fall back to the tool name.

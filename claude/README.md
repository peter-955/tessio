# Tessio for Claude Code

The Tessio Claude Code plugin (WBS 5.5). One install gives Claude the Tessio MCP server under the name `plugin:tessio:tessio`, the screenshot upload hook that runs after every `record_case_result` call, and seven skills: `/tessio:run-story-tests`, `/tessio:run-suite`, `/tessio:rerun-failed`, `/tessio:review-readiness`, `/tessio:answer-gaps`, `/tessio:import-cases` and `/tessio:draft-cases`. The developer only enters the Tessio URL and their token. This README is for the people who maintain the plugin.

Setup for developers: [Claude setup](../docs/guides/claude-setup.md).

Quick install, with the command the Connect Claude page shows:

```bash
claude plugin install tessio --marketplace https://tessio.example.com/api/plugin/marketplace.json --config tessio_url=https://tessio.example.com --config tessio_token=tsio_...
```

The Tessio API serves this marketplace and the plugin zip itself, built from this folder ([ADR 0010](../docs/decisions/0010-tessio-serves-its-claude-plugin.md)). Claude Code installs it only from an HTTPS address, so on a local checkout use `claude --plugin-dir claude`.

How to check the install: [Check that it works](../docs/guides/claude-setup.md#3-check-that-it-works). Without the plugin: [Manual setup without the plugin](../docs/guides/claude-setup.md#manual-setup-without-the-plugin).

## Contents

| Path | Role |
| --- | --- |
| [.claude-plugin/plugin.json](.claude-plugin/plugin.json) | The plugin manifest: name `tessio`, version and the two options. |
| [.mcp.json](.mcp.json) | The `tessio` http MCP server at `${user_config.tessio_url}/mcp`, with `Authorization: Bearer ${user_config.tessio_token}` and `X-Tessio-Plugin-Version`, which must equal the `version` in `plugin.json`. |
| [hooks/hooks.json](hooks/hooks.json) | The `PostToolUse` hook on `mcp__plugin_tessio_tessio__record_case_result`, timeout 120 seconds. |
| [hooks/upload_screenshots.py](hooks/upload_screenshots.py) | The screenshot upload hook. |
| [hooks/upload_run_log.py](hooks/upload_run_log.py) | The execution log hook, after `finish_run`. |
| [hooks/tests/](hooks/tests/) | Tests for the hook, the manifests and skills, and the measurement script. |
| [skills/run-story-tests/](skills/run-story-tests/) | The `/tessio:run-story-tests` skill, with the shared run procedure in [references/execute-cases.md](skills/run-story-tests/references/execute-cases.md). |
| [skills/run-suite/](skills/run-suite/) | The `/tessio:run-suite` skill: a regression suite in runs of at most 50 cases, with the shared run procedure. |
| [skills/rerun-failed/](skills/rerun-failed/) | The `/tessio:rerun-failed` skill. |
| [skills/review-readiness/](skills/review-readiness/) | The `/tessio:review-readiness` skill. |
| [skills/answer-gaps/](skills/answer-gaps/) | The `/tessio:answer-gaps` skill, with the procedure for a run blocked by open gaps in [references/when-gaps-block.md](skills/answer-gaps/references/when-gaps-block.md). |
| [skills/import-cases/](skills/import-cases/) | The `/tessio:import-cases` skill, with the shared check, confirm and create procedure in [references/create-cases.md](skills/import-cases/references/create-cases.md). |
| [skills/draft-cases/](skills/draft-cases/) | The `/tessio:draft-cases` skill. |
| [scripts/extract_file.py](scripts/extract_file.py) | Prints the text of an `.xlsx` or `.docx` file for `/tessio:import-cases`. Standard library only. |
| [scripts/measure-tokens.sh](scripts/measure-tokens.sh) | The token measurement script for WBS 5.7. |
| [../.claude-plugin/marketplace.json](../.claude-plugin/marketplace.json) | A marketplace `tessio` at the repository root, for a local checkout (`claude plugin marketplace add <repo>`). Users install from the marketplace the API serves, which has the same name, so the installed id is `tessio@tessio` either way. |

## Options

| Option | What to enter |
| --- | --- |
| `tessio_url` | The base URL of your Tessio server, without `/mcp`. Default `http://localhost:3202`. |
| `tessio_token` | Your personal API token (`tsio_...`). It is marked sensitive, so Claude Code keeps it in its secure credential storage and not in `settings.json`. |

Both options are required.

## MCP tools used by the skills

In Claude Code the tools are named `mcp__plugin_tessio_tessio__<tool>`. Each call checks the token's project role for this capability.

| Tool | Capability |
| --- | --- |
| `get_story_context` | `story.view` |
| `get_suite_context` | `run.view` |
| `get_open_gaps` | `gap.view` |
| `raise_gaps` | `gap.raise` |
| `get_my_gaps` | `gap.answer` |
| `answer_gap` | `gap.answer` |
| `reassign_gap` | `gap.reassign` |
| `set_test_data` | `test_data.edit` |
| `start_run` | `run.start` |
| `record_case_result` | `run.start` |
| `finish_run` | `run.start` |
| `get_test_file` | `run.start` |
| `resolve_data` | `secret.use_in_run` |
| `get_failed_cases` | `run.view` |
| `check_draft_cases` | `test_case.edit` |
| `create_draft_cases` | `test_case.edit` |

## Skills

| Skill | Arguments | What it does |
| --- | --- | --- |
| `/tessio:run-story-tests` | `<STORY-KEY> [environment] [case codes]` | Checks for open gaps, starts a run, checks the environment's health, runs each Ready case in Claude in Chrome and records one result per case. |
| `/tessio:run-suite` | `<suite> [environment] [case codes]` | Loads the suite with `get_suite_context` (its Ready cases grouped by story, and the skipped cases that are not Ready or flagged Needs review), then runs the cases in runs of at most 50 cases, one after the other: `start_run(suite=…, case_ids=…)`, then the shared run procedure. A suite name with spaces is quoted. If it stops early, it gives the command that runs the rest. Admin, QC and Dev. |
| `/tessio:rerun-failed` | `<run-id>` | Starts a child run of the failed and blocked cases of a story run or a suite run and executes it the same way. A suite run with more than 50 such cases (a large manual run) is re-run as several runs of at most 50 with `case_ids`, one after the other, without a parent link. |
| `/tessio:review-readiness` | `<STORY-KEY>` | Reviews the story, its acceptance criteria and its cases, and files the new gaps with `raise_gaps`. It never edits Jira or the cases. |
| `/tessio:answer-gaps` | `[STORY-KEY \| mine]` | Loads the gaps waiting for you with `get_my_gaps`, suggests two or three answers per gap with their sources (story, AC, earlier answers, test data, or the product's code when Claude runs in its repository), and asks you to pick one, write your own, reassign or skip. After you confirm, it saves with `answer_gap`, `reassign_gap` and, for missing plain data, `set_test_data`. It never asks for a secret (it gives the Test data link instead) and never edits cases or Jira. Admin, PM, BA, QC and Dev. |
| `/tessio:import-cases` | `<file> [STORY-KEY]` | Reads a test plan (xlsx, csv, docx, pdf, text or an image), turns it into cases, checks them with `check_draft_cases`, shows a summary and, after a yes, creates them as Draft with `create_draft_cases`. Admin and QC only. |
| `/tessio:draft-cases` | `<STORY-KEY>` | Writes cases from the story's acceptance criteria, then checks, confirms and creates them as Draft the same way. Admin and QC only. |

When open gaps block a start (`OPEN_GAPS_BLOCK_RUN`, also for a suite run, where any open gap on a story with a case in the suite blocks it), `/tessio:run-story-tests`, `/tessio:run-suite` and `/tessio:rerun-failed` follow [skills/answer-gaps/references/when-gaps-block.md](skills/answer-gaps/references/when-gaps-block.md): they list the open gaps by assignee (`get_open_gaps` names each gap's assignee or role queue), offer `/tessio:answer-gaps` for the caller's own gaps (`get_my_gaps`), and name who must answer the rest.

The run procedure shared by `/tessio:run-story-tests`, `/tessio:run-suite` and `/tessio:rerun-failed` is in [skills/run-story-tests/references/execute-cases.md](skills/run-story-tests/references/execute-cases.md):

- a `curl` health check before the first case, and `finish_run` with the reason when the environment is down;
- `scale: 0.5` for screenshots taken only to navigate;
- one full-size evidence screenshot per step, saved to disk;
- secrets resolved with `resolve_data` just before use and never written back.
- shared steps arrive already expanded; a data-driven case (`parameters` and `data_rows`) runs once per data row, with `{{param.<name>}}` replaced by the row's value, and each row is recorded as its own iteration: one `record_case_result` per row with `iteration` (0 for the first row).

## Screenshot upload hook

[hooks/upload_screenshots.py](hooks/upload_screenshots.py) runs after every `record_case_result` call. Claude passes only each step's local screenshot path. The hook then:

1. reads the `case_result_id` from the tool result;
2. asks Tessio for one signed upload per case (`POST /api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload`);
3. uploads each screenshot straight to storage. JPEGs from Claude in Chrome go as they are. Other formats are compressed first: JPEG with `sips` on macOS, WebP with `cwebp` elsewhere.

The image never goes through the model, and the tool result stays at about 30 tokens.

- It reads the URL and token from `CLAUDE_PLUGIN_OPTION_TESSIO_URL` and `CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN` (the plugin options), and falls back to `TESSIO_URL` and `TESSIO_TOKEN` (the manual setup).
- It always exits 0. Missing settings, input that is not JSON, an error result or a missing `run_id` mean nothing is uploaded, with no traceback.
- Uploads that fail with a network error or a 5xx response go to `~/.tessio/pending-uploads.jsonl`. They are retried the next time the hook runs. The plugin and the manual setup share this file.

## Execution log hook

[hooks/upload_run_log.py](hooks/upload_run_log.py) runs after every `finish_run` call. It reads the run's part of Claude Code's session log (`transcript_path` in the hook input), from the `start_run` result that holds the run id to the `finish_run` call, and sends one log to `POST /api/runs/{run_id}/log`:

- Claude's visible notes, and every tool call with its input, output, error flag and duration. Subagent lines and Claude's hidden thinking are left out.
- The values `resolve_data` returned are replaced with `••••`, images with `[screenshot]`, and each text and input is cut to 4000 characters. The server masks again.
- The token usage, summed once per API request, so the run page shows tokens per case.
- At most 3000 entries; the log is marked cut beyond that.

It reads only the session log fields it needs and skips anything else, because the format belongs to Claude Code. It always exits 0. A failed upload (network error or 5xx) waits in `~/.tessio/pending-run-logs/<run_id>.json` and is retried on the next run; a refused one (4xx) is reported on stderr and dropped.

## Local development

Load the plugin from a checkout, without installing it:

```bash
claude --plugin-dir <path to the Tessio repo>/claude
```

Set `CLAUDE_PLUGIN_OPTION_TESSIO_URL` and `CLAUDE_PLUGIN_OPTION_TESSIO_TOKEN`, or `TESSIO_URL` and `TESSIO_TOKEN`, if Claude Code does not prompt for the options.

Check the manifests:

```bash
claude plugin validate claude --strict
claude plugin validate .
```

## Releasing a new version

1. Bump `version` in [.claude-plugin/plugin.json](.claude-plugin/plugin.json) **and** `X-Tessio-Plugin-Version` in [.mcp.json](.mcp.json) to the same `MAJOR.MINOR.PATCH`. `test_plugin_files.py` fails if they differ.
2. Run the [tests](#tests) and the manifest checks above, then merge.
3. Deploy the API. It serves the new zip at once, and from then on it refuses MCP calls from older plugins with `PLUGIN_OUTDATED` and the update command.
4. Users get the new version with the commands below, or automatically if they turned on auto-update for the `tessio` marketplace under `/plugin` → **Marketplaces**:

```bash
claude plugin marketplace update tessio
claude plugin update tessio@tessio
```

## Measuring tokens (WBS 5.7)

[scripts/measure-tokens.sh](scripts/measure-tokens.sh) runs `/tessio:run-story-tests` headless with this plugin and Claude in Chrome, and records the token usage.

```bash
claude/scripts/measure-tokens.sh <STORY-KEY> <baseline|scaled> [environment]
```

- `scaled` runs the skill as written: navigation screenshots at `scale: 0.5`.
- `baseline` tells Claude to take every screenshot at full size.
- The raw JSON result goes to `${TESSIO_MEASUREMENTS_DIR:-~/.tessio/measurements}/<UTC timestamp>-<STORY-KEY>-<mode>.json`.
- A row is appended to `measurements.csv` in the same folder, and printed: `timestamp, story, mode, num_turns, input_tokens, cache_creation_input_tokens, cache_read_input_tokens, output_tokens, total_cost_usd, duration_ms, is_error`.

Procedure:

1. Pick a pilot story with Ready cases, an environment that is reachable from your machine, and fixed test data. Use the same story, environment and data for every run.
2. Run each mode 3 times, each in a fresh session (the script starts a new `claude -p` each time).
3. For each run, tokens per case = (`input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens` + `output_tokens`) / the number of cases in the `finish_run` report.
4. Compare the median tokens per case of `baseline` and `scaled`.
5. Record the results in WBS 5.7. It stays open until a pilot story has been measured.

## Tests

```bash
python3 -m unittest discover -s claude/hooks/tests -v
```

The tests use only the standard library. They cover the hook (with a local HTTP server standing in for Tessio and storage), the plugin manifests and skills, the measurement script (with a fake `claude`) `extract_file.py` (with small xlsx and docx files built in the test) and the log hook (with a synthetic session log and a local HTTP server).

# Claude setup

**Status:** Draft, written 2026-11-01 for the build after W7. WBS 8.2.

This page is for Dev and QC, and for Admins, PMs and BAs who want Claude to review a story's readiness or answer the gaps waiting for them. QC and Admins can also have Claude import or draft test cases. One plugin install gives Claude Code the Tessio MCP server `plugin:tessio:tessio`, the screenshot upload hook and seven skills, and the only inputs are your Tessio URL and a token.

## What Claude can do for your role

| Project role | `/tessio:review-readiness` | `/tessio:answer-gaps` | `/tessio:run-story-tests`, `/tessio:run-suite` | `/tessio:rerun-failed` | `/tessio:import-cases`, `/tessio:draft-cases` |
| --- | --- | --- | --- | --- | --- |
| Admin | Yes | Yes | Yes | Yes | Yes |
| QC | Yes | Yes | Yes | Yes | Yes |
| Dev | Yes | Yes | Yes | Yes | No |
| PM | Yes | Yes, without saving test data | No | No | No |
| BA | Yes | Yes, without saving test data | No | No | No |
| Viewer | Read only | No | No | No | No |

A Viewer's token can read the story, its gaps and its runs. Filing or answering gaps and starting runs are refused with `PERMISSION_DENIED`.

`/tessio:answer-gaps [STORY-KEY | mine]` works through the open gaps assigned to you or to your role queue, high severity first. For each gap it says what the question means and what it blocks, and offers two or three answers, each with its source: the story, an AC, an earlier answer to a similar question, existing test data, or the product's code (file and line) when you run Claude Code in the product's repository. You pick one with a key press, write your own, reassign the gap or skip it. Nothing is saved until you confirm the batch. For missing plain test data, Admin, QC and Dev also have the value saved to **Test data**; PM and BA answer only, and a QC or Dev adds the value. Claude never asks for a secret: it gives you the link to the project's **Test data** page instead. It never edits cases or Jira; at the end it lists the cases the answers suggest updating, for QC.

`/tessio:run-suite <suite> [environment] [case codes]` runs a regression suite: the Ready cases of many stories, picked on the suite page in Tessio. Quote a name with spaces (`/tessio:run-suite "Checkout regression" staging`). Claude first lists the cases the suite skips (not Ready, or flagged *Needs review*), then runs the rest in runs of at most 50 cases, one after the other, and reports the results per story. A suite run never changes a story's test status; its failures open on each case's story. If Claude stops before the end, it gives you the command that runs the cases that are left.

When a run is blocked by open gaps, `/tessio:run-story-tests`, `/tessio:run-suite` and `/tessio:rerun-failed` list the gaps by who must answer them, offer `/tessio:answer-gaps` for yours, and name the people or role queues for the rest.

`/tessio:import-cases <file> [STORY-KEY]` turns a test plan file (xlsx, csv, docx, pdf, text or an image) into test cases. `/tessio:draft-cases <STORY-KEY>` writes cases from the story's acceptance criteria. Both show you a summary and ask before creating anything, and every case they create is a Draft that QC reviews before it can run.

The token always acts with your current role in that one project. If your role changes, the next call uses the new role.

## Requirements

- Claude Code recent enough that `claude plugin install --help` lists `--config`. Older versions: see [Older Claude Code versions](#older-claude-code-versions).
- `python3` 3.9 or later. The upload hook uses only the standard library.
- `curl`.
- The Claude in Chrome extension, connected to Claude Code (run `/chrome` in a session). The skills drive the app under test through it.
- Membership in the project. Workspace admins need a project membership too, because a token only gets your real project role.
- Optionally `cwebp`. See [Screenshot compression](#screenshot-compression).
- macOS or Linux. On Windows, use WSL.

## 1. Create a token

1. In Tessio, open the user menu and select **Connect Claude** (`/connect-claude`).
2. Enter a **Name** of at most 100 characters, for example "My laptop".
3. Pick the **Project**. You can only pick a project you are a member of.
4. Pick **Expires after**: 7, 30, 60 or 90 days. The default is 30 days, and 90 is the maximum.
5. Select **Create token**.
6. The dialog says "Copy it now. You will not see this token again." Copy the command it shows. The **Token only** box holds just the `tsio_...` value.

Rules:

| Rule | Detail |
| --- | --- |
| One project | A token works for the one project you picked, and for no other. |
| Shown once | The token is shown only in this dialog. Tessio cannot show it again. |
| 10 active tokens | At most 10 active tokens per person. The page then says "You have 10 active tokens. Revoke one to create another." |
| Browser only | Tokens are created on this page while you are signed in. Claude cannot create them. |
| Viewer | The form says "You are a Viewer in this project, so Claude can read but not record results." |

Each project needs its own token.

> Screenshot to add: connect-claude-token.png: the created-token dialog with the install command.

## 2. Install the plugin

Run the command from the dialog in your terminal. It has this shape:

```bash
claude plugin install tessio --marketplace https://tessio.example.com/api/plugin/marketplace.json --config tessio_url=https://tessio.example.com --config tessio_token=tsio_...
```

| Argument | What it is |
| --- | --- |
| `tessio` | The plugin. Once installed, its id is `tessio@tessio`. |
| `--marketplace …/api/plugin/marketplace.json` | Where the plugin lives: your Tessio server serves it ([ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md)). Claude Code adds the marketplace first if it does not know it yet. |
| `--config tessio_url=...` | The address you use for Tessio in the browser, without `/mcp`. The page fills it in for you. |
| `--config tessio_token=...` | Your `tsio_...` token. It is marked sensitive, so Claude Code keeps it in its secure credential storage and not in `settings.json`. |

The plugin is installed for your user by default (`-s user`). Then restart Claude Code, or run `/reload-plugins` in a running session.

Claude Code installs the plugin only from an HTTPS address, so the command works against the deployed Tessio and not against `localhost`. In local development, load the plugin from the repository with `claude --plugin-dir <path to the repo>/claude`; the web app on `http://localhost:3201` forwards `/api` and `/mcp` to the server, so both `http://localhost:3201` and `http://localhost:3202` work as `tessio_url`.

### Keep the token out of your shell history

The command on the page puts the token on the command line. To avoid that, use one of these routes.

Leave out the token option, and Claude Code asks for it:

```bash
claude plugin install tessio --marketplace https://tessio.example.com/api/plugin/marketplace.json --config tessio_url=https://tessio.example.com
```

Or write the values in a file with an editor, and pipe the file in:

```json
{"tessio_url": "https://tessio.example.com", "tessio_token": "tsio_..."}
```

```bash
claude plugin configure tessio@tessio --values-stdin < values.json
rm values.json
```

### Older Claude Code versions

If `claude plugin install --help` does not list `--config`, add the marketplace first, then install. The install asks for both options.

```bash
claude plugin marketplace add https://tessio.example.com/api/plugin/marketplace.json
claude plugin install tessio@tessio
```

## 3. Check that it works

Check that the server answers:

```bash
curl -fsS https://tessio.example.com/api/health
```

Check that the plugin is installed and enabled:

```bash
claude plugin list
```

It lists `tessio@tessio` as enabled. Then, in a Claude Code session:

| Check | Expected |
| --- | --- |
| `/mcp` | `plugin:tessio:tessio` is connected. |
| `/hooks` | A `PostToolUse` hook with the matcher `mcp__plugin_tessio_tessio__record_case_result`. |
| Type `/tessio:` | `/tessio:run-story-tests`, `/tessio:run-suite`, `/tessio:rerun-failed`, `/tessio:review-readiness`, `/tessio:answer-gaps`, `/tessio:import-cases` and `/tessio:draft-cases` are listed. |

Make a first real call with your own story key:

```text
/tessio:review-readiness SHOP-12
```

The full run flow is in the [Dev guide](user/dev.md#run-the-tests).

## Execution log

After `finish_run`, the plugin also uploads Claude's notes and actions of the run, with secrets masked. Testers read them on the run's **Log** tab. A log that could not be sent waits in `~/.tessio/pending-run-logs/` and is sent with the next run.

## Screenshot compression

After each `record_case_result` call, the hook uploads the step screenshots straight to storage.

| Screenshot | What the hook does |
| --- | --- |
| `.jpg` or `.jpeg` | Uploaded as it is. Claude in Chrome already saves JPEG, about 46 KB at 1400 × 845. |
| Other format, on macOS | Converted to JPEG at quality 70 with the built-in `sips`. Nothing to install. |
| Other format, elsewhere | Converted to WebP at quality 70 with `cwebp`, if it is installed. |
| No tool available | The original file is uploaded. |

To install `cwebp`:

| System | Command |
| --- | --- |
| macOS (optional) | `brew install webp` |
| Debian or Ubuntu | `sudo apt-get install webp` |
| Fedora | `sudo dnf install libwebp-tools` |

Images never pass through the model. An upload that fails with a network error or a 5xx response waits in `~/.tessio/pending-uploads.jsonl` and is retried the next time the hook runs.

## Switch project, rotate or revoke a token

One install holds one token, so it works on one project at a time. To switch to another project:

1. Create a token for the other project on the Connect Claude page.
2. Write only the new token in a file, for example `{"tessio_token": "tsio_..."}`. Options you leave out keep their values.
3. Run the configure command, then `/reload-plugins` in your session.

```bash
claude plugin configure tessio@tessio --values-stdin < values.json
rm values.json
```

Rotate a token the same way: create a new one for the same project, configure it, then revoke the old one.

Your tokens are listed under **Your tokens** on the Connect Claude page. Select **Revoke** on a token you no longer use. Claude stops working with it at once.

A token stops working when it expires. Create a new one before then and configure it. If you lose a laptop, revoke its tokens at once from another device.

## Update or remove the plugin

Everyone must run the plugin version the server serves. When Tessio is updated, Claude's Tessio tools answer `PLUGIN_OUTDATED` with the command to run. Get the latest version, then restart Claude Code:

```bash
claude plugin marketplace update tessio
claude plugin update tessio@tessio
```

To get new versions without being asked, open `/plugin` in a session, go to **Marketplaces**, select `tessio` and turn on **Enable auto-update**. Claude Code then updates the plugin in the background and tells you to run `/reload-plugins`.

Remove the plugin:

```bash
claude plugin uninstall tessio@tessio
```

## Manual setup without the plugin

Use this only if the marketplace is not reachable from your machine, or if plugins are blocked by policy. The server refuses MCP calls without the plugin version, so this setup sends it by hand and must be updated with each release.

1. Connect the MCP server at local or user scope:

   ```bash
   claude mcp add --transport http tessio https://tessio.example.com/mcp --header "Authorization: Bearer tsio_..." --header "X-Tessio-Plugin-Version: 0.2.0" -s user
   ```

   Never use `-s project`. It writes the token to the project's shared `.mcp.json`. Use the version in `claude/.claude-plugin/plugin.json` of the release your Tessio runs.

2. Add the hook and the settings to `~/.claude/settings.json` or to the project's `.claude/settings.local.json`. Never put them in a committed `.claude/settings.json`. These files hold the token in plain text.

   ```json
   {
     "env": {
       "TESSIO_URL": "https://tessio.example.com",
       "TESSIO_TOKEN": "tsio_..."
     },
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "mcp__tessio__record_case_result",
           "hooks": [
             {
               "type": "command",
               "command": "python3 /absolute/path/to/tessio/claude/hooks/upload_screenshots.py",
               "timeout": 120
             }
           ]
         }
       ]
     }
   }
   ```

Limits of this setup:

- The skills are not available, because they only allow the plugin's tools.
- The server is named `tessio` here, so its tools are `mcp__tessio__<tool>`. The plugin's matcher does not fire for this server, and this matcher does not fire for the plugin's server.
- The plugin and the manual setup share `~/.tessio/pending-uploads.jsonl`.

## For workspace admins: the plugin source

Nothing to set up. The API serves the plugin from the `claude/` folder it was built with, at `https://<your Tessio>/api/plugin/marketplace.json`, and the Connect Claude page builds the install command from the page's own address. `CLIENT_URL` must be the public HTTPS address, because the marketplace file points at the zip under it. See [ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md).

## Troubleshooting

An MCP tool error reads `Error executing tool <tool>: <CODE>: <message>`. Look up the code below.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `/mcp` shows `plugin:tessio:tessio` as failed | The URL is wrong, `/mcp` was added to `tessio_url`, or the server is down. | Run the `curl` health check. Set `tessio_url` to the browser address without `/mcp`, then `/reload-plugins`. |
| `INVALID_API_TOKEN` | The token expired or was revoked, your user was deactivated, you were removed from the project, or the value is not a `tsio_` token. | Create a new token and configure it. |
| `PLUGIN_OUTDATED` | Your plugin is older than the one this Tessio serves. | Run `claude plugin marketplace update tessio && claude plugin update tessio@tessio`, then restart Claude Code. |
| `PERMISSION_DENIED` | Your role in the project cannot do this. | See [What Claude can do for your role](#what-claude-can-do-for-your-role). Ask a project admin for another role. |
| `NOT_FOUND` on a story | The story belongs to another project than the token's. | Switch to a token for that project. |
| `NOT_FOUND` on a suite | No suite of the token's project has that name or id. | Copy the command from the suite page in Tessio, or quote a name with spaces. |
| `PROJECT_ARCHIVED` | The project is archived. | Ask a project admin. |
| `OPEN_GAPS_BLOCK_RUN` | The story has open gaps. For a suite run: a story with a case in the suite has open gaps. | Answer yours with `/tessio:answer-gaps <STORY-KEY>` (or `/tessio:answer-gaps` for several stories); Claude names who must answer the rest. Then start again. |
| `NO_READY_CASES` | The story has no *Ready* test cases. | Ask QC to move the cases to *Ready*. |
| `RUN_ALREADY_RUNNING` | A run is already in progress for this story. | Wait for it to finish, or ask the person who started it. |
| `SUITE_ALREADY_RUNNING` | A run of this suite is already in progress. | Wait for it to finish, or ask the person who started it. A run with no activity for 4 hours is aborted on its own. |
| `SUITE_EMPTY` | The suite has no *Ready* case that isn't flagged *Needs review*. | Ask QC to move the cases to *Ready* or clear the flag. |
| `SUITE_ARCHIVED` | The suite is archived. | Run another suite, or ask QC. |
| `RUN_NOT_OWNED` | Only the person who started the run can record results or finish it. | Use your own run. |
| Hook stderr says "Tessio hook: set the plugin options tessio_url and tessio_token (...), or TESSIO_URL and TESSIO_TOKEN, to upload screenshots." | Claude Code did not pass the sensitive option to the hook. | Add `TESSIO_URL` and `TESSIO_TOKEN` under `env` in `~/.claude/settings.json`, as in the manual setup. |
| `finish_run` lists missing screenshots | The uploads did not reach storage. | Check `~/.tessio/pending-uploads.jsonl` and your network. Pending uploads are retried on the next hook run. |
| The run ends early with a reason | The environment was down at the health check. | Fix the environment, then run the skill again. |
| `TOKEN_LIMIT_REACHED` on the Connect Claude page | You already have 10 active tokens. | Revoke one under **Your tokens**. |

## Security

- A token acts as you, with your current role, in one project.
- Never commit a token or paste it into a chat.
- The plugin keeps the token in Claude Code's credential storage. The manual setup keeps it in plain text in a settings file.
- Secrets reach Claude only through `resolve_data`, during a running run that you started. Every call is audited.
- If a laptop is lost, revoke its tokens at once.

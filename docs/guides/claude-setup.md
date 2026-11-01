# Claude setup

**Status:** Draft, written 2026-11-01 for the build after W7. WBS 8.2.

This page is for Dev and QC, and for Admins, PMs and BAs who want Claude to review a story's readiness. One plugin install gives Claude Code the Tessio MCP server `plugin:tessio:tessio`, the screenshot upload hook and three skills, and the only inputs are your Tessio URL and a token.

## What Claude can do for your role

| Project role | `/tessio:review-readiness` | `/tessio:run-story-tests` | `/tessio:rerun-failed` |
| --- | --- | --- | --- |
| Admin | Yes | Yes | Yes |
| QC | Yes | Yes | Yes |
| Dev | Yes | Yes | Yes |
| PM | Yes | No | No |
| BA | Yes | No | No |
| Viewer | Read only | No | No |

A Viewer's token can read the story, its gaps and its runs. Filing gaps and starting runs are refused with `PERMISSION_DENIED`.

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
claude plugin install tessio --marketplace <marketplace> --config tessio_url=https://tessio.example.com --config tessio_token=tsio_...
```

| Argument | What it is |
| --- | --- |
| `tessio` | The plugin. Once installed, its id is `tessio@tessio`. |
| `--marketplace <marketplace>` | Where the plugin lives. Your workspace admin sets it. Claude Code adds the marketplace first if it does not know it yet. |
| `--config tessio_url=...` | The address you use for Tessio in the browser, without `/mcp`. The page fills it in for you. |
| `--config tessio_token=...` | Your `tsio_...` token. It is marked sensitive, so Claude Code keeps it in its secure credential storage and not in `settings.json`. |

The plugin is installed for your user by default (`-s user`). Then restart Claude Code, or run `/reload-plugins` in a running session.

In local development, the web app on `http://localhost:3201` forwards `/api` and `/mcp` to the server, so both `http://localhost:3201` and `http://localhost:3202` work as `tessio_url`.

### Keep the token out of your shell history

The command on the page puts the token on the command line. To avoid that, use one of these routes.

Leave out the token option, and Claude Code asks for it:

```bash
claude plugin install tessio --marketplace <marketplace> --config tessio_url=https://tessio.example.com
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
claude plugin marketplace add <marketplace>
claude plugin install tessio@tessio
```

### If the command shows `<marketplace>`

The plugin source is not set yet, and the dialog says "The plugin source is not configured. Replace <marketplace> with the value your admin gives you." Ask your workspace admin for the value. Admins: see [For workspace admins: the plugin source](#for-workspace-admins-the-plugin-source).

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
| Type `/tessio:` | `/tessio:run-story-tests`, `/tessio:rerun-failed` and `/tessio:review-readiness` are listed. |

Make a first real call with your own story key:

```text
/tessio:review-readiness SHOP-12
```

The full run flow is in the [Dev guide](user/dev.md#run-the-tests).

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

Get the latest plugin version, then restart Claude Code:

```bash
claude plugin marketplace update tessio
claude plugin update tessio@tessio
```

Remove the plugin:

```bash
claude plugin uninstall tessio@tessio
```

## Manual setup without the plugin

Use this only if the marketplace is not reachable from your machine, or if plugins are blocked by policy.

1. Connect the MCP server at local or user scope:

   ```bash
   claude mcp add --transport http tessio https://tessio.example.com/mcp --header "Authorization: Bearer tsio_..." -s user
   ```

   Never use `-s project`. It writes the token to the project's shared `.mcp.json`.

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

The Connect Claude page builds the install command with the plugin source that was set when the client image was built.

1. Set the GitHub repository variable `TESSIO_PLUGIN_MARKETPLACE` to the repository that holds `.claude-plugin/marketplace.json`. The CI workflow passes it to the build argument `NEXT_PUBLIC_TESSIO_PLUGIN_MARKETPLACE`.
2. Rebuild and deploy the client image.

| Form | Example |
| --- | --- |
| `owner/repo` | `acme/tessio` |
| A git or https URL | `https://git.example.com/acme/tessio.git` |
| A path | `/opt/tessio` |

For a private repository, each developer needs git read access with their usual credentials. Until the variable is set, the page shows `<marketplace>`.

## Troubleshooting

An MCP tool error reads `Error executing tool <tool>: <CODE>: <message>`. Look up the code below.

| Symptom | Cause | Fix |
| --- | --- | --- |
| `/mcp` shows `plugin:tessio:tessio` as failed | The URL is wrong, `/mcp` was added to `tessio_url`, or the server is down. | Run the `curl` health check. Set `tessio_url` to the browser address without `/mcp`, then `/reload-plugins`. |
| `INVALID_API_TOKEN` | The token expired or was revoked, your user was deactivated, you were removed from the project, or the value is not a `tsio_` token. | Create a new token and configure it. |
| `PERMISSION_DENIED` | Your role in the project cannot do this. | See [What Claude can do for your role](#what-claude-can-do-for-your-role). Ask a project admin for another role. |
| `NOT_FOUND` on a story | The story belongs to another project than the token's. | Switch to a token for that project. |
| `PROJECT_ARCHIVED` | The project is archived. | Ask a project admin. |
| `OPEN_GAPS_BLOCK_RUN` | The story has open gaps. | Get the gaps answered, then start again. |
| `NO_READY_CASES` | The story has no *Ready* test cases. | Ask QC to move the cases to *Ready*. |
| `RUN_ALREADY_RUNNING` | A run is already in progress for this story. | Wait for it to finish, or ask the person who started it. |
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

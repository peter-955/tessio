# AI Harness page: what Claude gets from Tessio

**Status:** Accepted, built 2026-11-02 ([spec](../spec/ai-harness.md))
**Date:** 2026-11-02
**WBS:** [5.15](../wbs/wbs.md#5-claude-integration)
**Related:** [ADR 0010](../decisions/0010-tessio-serves-its-claude-plugin.md), [AUTH-10 and AUTH-11](../spec/authentication-and-account.md#auth-10-create-an-api-token-for-claude-wbs-326), [app shell spec](../spec/app-shell.md)

## Decisions at a glance

| Area | Decision (Peter, 2026-11-02) |
| --- | --- |
| Place | A new **AI Harness** page at `/ai-harness`, in the sidebar's workspace section. |
| Who | **Every signed-in user**, whatever their role. |
| Content | The Tessio plugin's skills, commands, hooks and MCP server with its tools, plus the versions. |
| Your version | Each user sees the plugin version **they actually run**, per token. The server saves the version that the plugin sends. |
| Server version | The page shows the Tessio server version too. |
| Tool permissions | Each MCP tool shows the capability it needs and the roles that hold it (Peter, 2026-11-02). |

## 1. Why

Today the plugin's contents are visible only in the files under `claude/` and in the server code. A QC or a PM can't see which skills exist, what the hooks do, which MCP tools Claude may call, or whether their own plugin is out of date. They find out only when an MCP call fails with `PLUGIN_OUTDATED`.

## 2. What the page shows

One page with five cards, all read-only.

1. **Versions**
   - Tessio server version.
   - Plugin version that this Tessio serves and requires (`plugin.json`).
   - **Your plugins:** one row per active token. Each row has the token name, the project, the plugin version last seen and when. A badge says *Current*, *Out of date* (with `claude plugin update tessio` to copy) or *Not used yet*.
2. **Skills:** name, slash command (`/tessio:<name>` and its `argument-hint`), and description from each `SKILL.md` frontmatter. A Copy button copies the command.
3. **Commands:** the files in `claude/commands/`. The plugin has none today, so the card says "The plugin has no separate commands. Run a skill with its slash command above."
4. **Hooks:** from `hooks/hooks.json`, show the event (`PostToolUse`), the tool it follows (`record_case_result`, shown without the `mcp__plugin_tessio_tessio__` prefix), the script (`hooks/upload_screenshots.py`) and the timeout.
5. **MCP server:** the name `tessio`, the URL `<origin>/mcp`, the transport `http` and the headers it needs (`Authorization`, `X-Tessio-Plugin-Version`). Then one row per registered tool, with its name and description from the live MCP server, the capability it checks and the roles that hold it, so the list can't drift from the code.

The page links to Connect Claude for people who have no token yet.

## 3. Changes

**Server**
- At start-up, the plugin bundle loader also reads the skills' frontmatter, `hooks/hooks.json` and the `commands/` folder. A bad skill frontmatter stops the API, the same as a bad `plugin.json` does today.
- New signed-in route `GET /api/ai-harness` in a new module `ai_harness`, included in the OpenAPI document (the marketplace routes stay out of it). It is not under `/api/plugin`, because the `plugin` module sits in the lowest import layer and can't use the session check. It returns `server` (version, build commit), `plugin` (name, version, description, update command), `skills`, `commands`, `hooks`, `mcpServers` and `mcpTools`.
- The tools come from the MCP server's own tool list. Each tool declares its capability once, in its module's `tool_capability.py`, and passes it both to its `_meta` (`tessio/capability`) and to the token check.
- The server version comes from the installed package (`tessio-server` in `pyproject.toml`). An optional `TESSIO_BUILD_COMMIT` adds the git commit when the image is built with it.

**Data**
- A new nullable column `api_tokens.plugin_version` (up to 32 characters), with a migration.
- On every MCP call, the server saves the version that the plugin sends when it differs from the stored one. Otherwise it saves only on the 60-second "last used" refresh (AUTH-11 AC3, "Last used" is refreshed at most once every 60 seconds).
- `GET /api/me/api-tokens` returns `pluginVersion`. The Connect Claude token table gets a Plugin column.

**Version check order**
- Today `PLUGIN_OUTDATED` is raised before the token is read, so an old version is never seen. The new order: authenticate the token, save the sent version, then refuse with `PLUGIN_OUTDATED`. The answer is the same, and the page can show *Out of date*.
- An invalid token still gets the token error, and the version check runs only after it. Nothing new is revealed to a caller without a valid token.

**Client**
- A new module `modules/ai-harness` and route `/ai-harness`.
- The sidebar's workspace section gets AI Harness after Projects, for every user (it updates the app shell's SHELL-1 AC4 rule: the workspace section always lists Projects).
- en, fr and vi strings.
- `export_openapi` and `npm run generate:api` after the API change.

**Plugin**
- No change and no version bump. The plugin already sends `X-Tessio-Plugin-Version`.

## 4. Open points

- **Server version source:** the image doesn't set a version today. Built: `pyproject.toml` version (or `TESSIO_SERVER_VERSION`), plus the optional `TESSIO_BUILD_COMMIT`, until releases are tagged.

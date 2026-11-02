# AI Harness

**Status:** Draft · **Updated:** 2026-11-02

WBS 5.15 · Story prefix HARN · Index: [README](README.md) · Proposal: [ai-harness-proposal.md](../discussions/ai-harness-proposal.md)

## Purpose

One page that shows what Claude Code gets from Tessio: the server version, the plugin version that Tessio serves, the plugin version on each of the user's tokens, and the plugin's skills, commands, hooks, MCP server and MCP tools. The user can see at a glance which slash commands exist, which tools Claude may call for which role, and whether their own plugin is out of date.

## Roles and capabilities

- Every signed-in user can open the page, whatever their workspace or project role. It needs no capability.
- The page reads only. It never changes the plugin or the tokens.
- "Your plugins" shows only the caller's own active tokens.

## User stories

### HARN-1 Open the AI Harness (WBS 5.15)

As a signed-in user, I want an AI Harness page, so that I can see what the Tessio plugin gives Claude Code.

- AC1: The sidebar's workspace section lists AI Harness (`/ai-harness`) after Projects, for every user.
- AC2: The page loads `GET /api/ai-harness` and shows five cards in this order: Versions, Skills, Commands, Hooks, MCP server.
- AC3: While loading it shows a skeleton. If the call fails, it shows "The AI Harness could not be loaded" with Try again.

### HARN-2 Versions (WBS 5.15)

As a user, I want to see the versions in play, so that I know whether my plugin matches the server.

- AC1: The card shows the Tessio server version and, when the server was built with `TESSIO_BUILD_COMMIT`, "commit `<commit>`".
- AC2: It shows the plugin version that this Tessio serves and requires, with "Claude Code must run this version or newer."
- AC3: "Your plugins" lists each of the caller's active tokens with the token name, the project key, the plugin version last sent, the last-used date and a state badge. Revoked and expired tokens are left out.
- AC4: The badge is *Current* when the sent version is the required one or newer (compared by number), *Out of date* when it is older or not `MAJOR.MINOR.PATCH`, and *Not used yet* when the token has never sent a version.
- AC5: When any token is *Out of date*, a warning "Update your plugin" shows the update command with a Copy button.
- AC6: With no active token, the card shows "You have no active token" and a Connect Claude link to `/connect-claude`.

### HARN-3 Skills and commands (WBS 5.15)

As a user, I want the list of slash commands, so that I know what to type in Claude Code.

- AC1: Each skill shows its slash command `/tessio:<name>` followed by its `argument-hint`, a Copy button that copies `/tessio:<name>`, and the description from its `SKILL.md` frontmatter.
- AC2: The Commands card lists the files in the plugin's `commands/` folder the same way. With none, it says "The plugin has no separate commands" and "Run a skill with its slash command above."

### HARN-4 Hooks (WBS 5.15)

As a user, I want to see the hooks, so that I know what runs on my machine after Claude calls a tool.

- AC1: Each hook in `hooks/hooks.json` shows its event (`PostToolUse`), the tool it follows without the `mcp__plugin_tessio_tessio__` prefix (or "Any tool" without a matcher), the script path inside the plugin and the timeout in seconds (or "Default").
- AC2: Only `command` hooks are listed.

### HARN-5 MCP server and tools (WBS 5.15)

As a user, I want to see the MCP tools and who may call them, so that I know what Claude can do with my token.

- AC1: The card lists each server in the plugin's `.mcp.json` with its name, transport, address and header names. `${user_config.tessio_url}` is replaced with Tessio's public address (`CLIENT_URL`).
- AC2: The Tools table lists every tool the running MCP server registers, sorted by name, with its description, the capability it checks and the project roles that hold that capability.
- AC3: The capability comes from the tool's `_meta` key `tessio/capability`, which is set from the same constant that the tool checks. The list can't drift from the code.

## Rules

- The server reads the plugin's skills, commands, hooks and MCP servers once at start-up, from `TESSIO_PLUGIN_DIR`. A skill or command with broken frontmatter, or a broken `hooks/hooks.json` or `.mcp.json`, stops the API at start-up, the same as a bad `plugin.json`.
- A skill without frontmatter takes its folder name and an empty description.
- The server version is `TESSIO_SERVER_VERSION` when set, otherwise the `version` in `server/pyproject.toml`.
- On every MCP call, the server saves the `X-Tessio-Plugin-Version` header on the token when it differs from the saved one (up to 32 characters). A call without the header keeps the saved version.
- The order on an MCP call is: check the token, save the version and "last used", check the plugin version (`PLUGIN_OUTDATED`), then check the capability. An older plugin is still refused, but its version is saved, so the page shows *Out of date*.

## Screens and states

| Route | Empty | Loading | Error | No permission | Live refresh |
| --- | --- | --- | --- | --- | --- |
| `/ai-harness` | no active token: "You have no active token" + Connect Claude; no commands: "The plugin has no separate commands" | page skeleton; token table skeleton | "The AI Harness could not be loaded" + Try again; "Your tokens could not be loaded" + Try again | – | – |

## API

| Method and path | Who | Notes |
| --- | --- | --- |
| `GET /api/ai-harness` | signed in | `server`, `plugin` (with `updateCommand`), `skills`, `commands`, `hooks`, `mcpServers`, `mcpTools` (with `capability` and `roles`) |
| `GET /api/me/api-tokens` | signed in | own tokens, with `pluginVersion` |

## Errors

| ErrorCode | When |
| --- | --- |
| `NOT_SIGNED_IN` | No session |

## Later

- None planned.

## Differences from the proposals

- The route is `GET /api/ai-harness` in its own module `ai_harness`, not `/api/plugin/harness`: the `plugin` module sits in the lowest import layer and can't use the session check.
- Hooks show their event, tool, script and timeout instead of a fixed one-line description, so the text can't drift from `hooks.json`.
- Tool permissions are shown in the first version (Peter, 2026-11-02).
- "AI Harness" is a product name and is not translated in French or Vietnamese.

## Open points

- Not checked in a real browser yet (B-13).
- An API token's "last used" is now refreshed even when the call is then refused for a missing capability or an old plugin.

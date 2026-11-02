# 0010. Tessio serves its own Claude plugin and refuses older versions

**Status:** Accepted
**Date:** 2026-11-01

## Context

Everyone uses Tessio through Claude Code with the Tessio plugin (`claude/`: MCP server connection, skills, screenshot hook, helper script). Testers and developers should get the same behaviour and output, so everyone must run the same plugin version.

- The plugin needed a marketplace on a git host. None was chosen (blocker B-11), and every user would need git access to it.
- Claude Code auto-updates plugins from non-Anthropic marketplaces only when the user turns it on.
- Forcing an install for everyone needs managed settings: a Claude Team or Enterprise plan, or MDM. The company uses individual Claude plans.
- Claude Code can add a marketplace from a URL to a hosted `marketplace.json`, and install a plugin from a zip over HTTPS (an `archive` source with a sha256 pin).

## Options considered

1. **A git repository as the marketplace**: the usual setup. But it needs a host and git access for every user, and versions drift unless each user turns on auto-update.
2. **Tessio serves the marketplace and the zip itself, and its MCP server refuses older plugins**: no extra host, the plugin always matches the server, and drift is blocked where it matters. But it needs HTTPS (Claude Code refuses archive downloads over plain HTTP or from loopback), so it can't be used on `localhost`.
3. **Option 2, but only warn on an older plugin**: softer, but people keep running old skills.

## Decision

Option 2.

- The API serves `GET /api/plugin/marketplace.json` and `GET /api/plugin/tessio-<version>.zip`. Both are public: the plugin holds no secrets, and the token is entered at install.
- The zip is built in memory from `claude/` when the API starts (`TESSIO_PLUGIN_DIR`, `/app/plugin` in the image), without tests and caches. It's built the same way every time, so its sha256 is stable.
- The plugin sends `X-Tessio-Plugin-Version` on every MCP call. A missing, unreadable or older version gets `PLUGIN_OUTDATED` with the update command. It was checked before the token; since WBS 5.15 (2026-11-02) it is checked right after the token, so the sent version can be saved on the token and shown on the [AI Harness](../spec/ai-harness.md) page.

## Consequences

- Blocker B-11 is closed. `NEXT_PUBLIC_TESSIO_PLUGIN_MARKETPLACE` and the GitHub variable `TESSIO_PLUGIN_MARKETPLACE` are gone. The Connect Claude page builds `claude plugin install tessio --marketplace <origin>/api/plugin/marketplace.json …` from the page's own address.
- A plugin release means bumping `version` in `plugin.json` and the header in `.mcp.json` together (a test checks this), then deploying the API. From that moment, older plugins are refused until their users run `claude plugin marketplace update tessio && claude plugin update tessio@tessio`.
- The API image needs `claude/` as an extra build context named `plugin`: in CI (`build-contexts`), in the e2e compose file (`additional_contexts`), and for any manual `docker build` (`--build-context plugin=claude`).
- Local development installs with `claude --plugin-dir claude`. The served marketplace works only behind HTTPS.
- The manual setup without the plugin must send the header itself.

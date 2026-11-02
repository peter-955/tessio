# Tessio: rules for Claude

Read this before working in the repository. It holds the project decisions every developer's Claude must follow, so everyone gets the same behaviour. The product and the code are described in [README.md](README.md) and [docs/README.md](docs/README.md).

## Working rules

- **No commits or pushes** until Peter says the work is finished. Leave every change uncommitted and don't offer to commit as a next step. The git repository exists so the husky commitlint hook works.
- **Don't stop on an unclear spec or a blocker.** Pick the common real-world solution, keep going, and record the question and your assumption in [docs/wbs/wbs.md](docs/wbs/wbs.md) under "Assumptions & blockers". Still ask before a decision that is expensive to reverse.
- **Specs describe today's code.** A new design goes into `docs/discussions/` first. When it's built, its behaviour goes into the feature's spec in `docs/spec/`, and its status into the WBS.
- **Another Claude session may be working in the same tree.** Re-read a file before you edit it, and don't undo changes you didn't make.

## Architecture decisions

- **Hosting:** a rented VPS with Docker Compose, not AWS services ([ADR 0007](docs/decisions/0007-hosting-vps-docker.md)).
- **Background jobs and cron:** Redis with BullMQ, never a Postgres-backed queue. Live events also go over Redis pub/sub ([ADR 0006](docs/decisions/0006-background-jobs-redis-bullmq.md)).
- **Folder and name style:** name each app for what it is (`server/`, `client/`, `claude/`), never `backend/` or `frontend/`. The same goes for images and variables (`TESSIO_SERVER_URL`, not `TESSIO_BACKEND_URL`).
- **Claude in Tessio:** every role (Admin, QC, Dev, PM, BA) uses Claude Code in the terminal with the Tessio plugin, signed in with their own Claude plan. The server never calls Claude: no API key, no AI bill on the server and no Claude Desktop connector. The server never runs a browser either. Propose changes to this only if Peter raises it.
- **One plugin for everyone:** the Tessio server serves the plugin from `claude/` at `/api/plugin/marketplace.json`, and MCP calls from an older plugin are refused with `PLUGIN_OUTDATED` ([ADR 0010](docs/decisions/0010-tessio-serves-its-claude-plugin.md)).

## Changing the Claude plugin (`claude/`)

- Any change that users should get means a new version. Bump `version` in `claude/.claude-plugin/plugin.json` **and** `X-Tessio-Plugin-Version` in `claude/.mcp.json` to the same `MAJOR.MINOR.PATCH`. A plugin test fails if they differ.
- Once the server runs the new version, MCP calls from older plugins are refused with the update command. Bump the version only when the server and the plugin really need to change together.
- Skills reference bundled files with `${CLAUDE_PLUGIN_ROOT}`. Hooks and scripts use only the Python standard library, and must run on Python 3.9.

## Checks

Run the checks in [README.md](README.md#checks) for every app you touched: server (ruff, lint-imports, mypy, pytest), client (lint, typecheck, format, Vitest, build) and the plugin (`python3 -m unittest discover -s claude/hooks/tests`, `claude plugin validate claude --strict`). After an API change, run `export_openapi` and `npm run generate:api`.

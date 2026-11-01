# Tessio

An application to manage testing of web applications: test cases linked to Jira stories, readiness review, runs by Claude (through MCP and Claude in Chrome) or by hand, failures and traceability.

## Workspace

| Folder | Purpose |
| --- | --- |
| [claude/](claude/) | The Tessio Claude Code plugin: MCP server connection, screenshot upload hook and skills ([claude/README.md](claude/README.md)). The marketplace file is [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) |
| [client/](client/) | Next.js 16 + Mantine 9 web app on the real API ([client/README.md](client/README.md)) |
| [server/](server/) | Python 3.14 + FastAPI: REST API, MCP server and BullMQ worker on PostgreSQL and Redis ([server/README.md](server/README.md), [ADR 0004](docs/decisions/0004-backend-stack.md)) |
| [e2e/](e2e/) | Playwright end-to-end suite on its own Docker stack |
| [deploy/](deploy/) | Caddyfile, `deploy.sh` and the VPS run book ([deploy/README.md](deploy/README.md)) |
| [docs/](docs/) | Product, specs, architecture, decisions, guides and the WBS. Start at [docs/README.md](docs/README.md) |

## Local ports

Every port this project uses on the host starts with `32`, so it never clashes with other projects.

| Port | Service |
| --- | --- |
| 3201 | Client (Next.js) |
| 3202 | Server (FastAPI API + MCP) |
| 3203 | Postgres |
| 3204 | Redis |
| 3205 | Bull Board |
| 3206 | Mailpit SMTP |
| 3207 | Mailpit web UI |
| 3208 | RustFS (S3 API) |

## Prerequisites

- Docker with the Compose plugin.
- [uv](https://docs.astral.sh/uv/) (it installs Python 3.14 for the server).
- Node.js 24.

## Run locally

1. Start the local services from the repo root: Postgres, Redis, Bull Board, Mailpit, RustFS and a one-off `rustfs-bucket` container that creates the `tessio` bucket.

   ```bash
   docker compose up -d
   ```

2. Start the server and the worker ([server/README.md](server/README.md) has the details):

   ```bash
   cd server
   cp .env.example .env                       # then set TESSIO_ENCRYPTION_KEY (see server/README.md)
   uv sync
   uv run alembic upgrade head
   uv run uvicorn app.main:create_production_app --factory --reload --port 3202
   uv run python -m app.workers.worker        # in a second terminal: email, Jira sync, maintenance jobs
   ```

3. Invite the first user. There is no public sign-up; the worker sends the invite to Mailpit at http://localhost:3207, where you open the link, set a password and set up two-factor.

   ```bash
   cd server
   uv run python -m app.commands.invite_user --email you@example.com --name "Your Name" --role owner
   ```

4. Start the client:

   ```bash
   cd client
   npm install
   npm run dev
   ```

5. Open http://localhost:3201. The client forwards `/api` and `/mcp` to the server on port 3202.

To connect Claude Code, follow the [Claude setup guide](docs/guides/claude-setup.md).

## Checks

```bash
# server/
uv run ruff check . && uv run ruff format --check .
uv run lint-imports
uv run mypy
uv run pytest                                # starts its own Postgres and Redis in Docker

# client/
npm run lint
npm run typecheck
npm run format:check
npm test                                     # Vitest
npm run build

# repo root: the Claude plugin hook
python3 -m unittest discover -s claude/hooks/tests
```

## End-to-end tests

The Playwright suite in [e2e/](e2e/) runs the real app on its own Docker stack (host ports 3211–3219) with a fake Jira. See [e2e/README.md](e2e/README.md) (`cd e2e && npm run stack:up && npm test`).

## CI

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs on pull requests, on pushes to `main` and by hand:

| Job | What it does |
| --- | --- |
| `server` | ruff, ruff format, lint-imports, mypy and pytest; then `alembic upgrade head` + `alembic check` on a Postgres service, and the OpenAPI drift check (`export_openapi`, then `git diff --exit-code` on `client/src/lib/api/openapi.json`) |
| `client` | generated-types drift check (`generate:api`, then `git diff` on `openapi.type.ts`), lint, typecheck, format check, Vitest and `next build` |
| `commitlint` | pull requests only: every commit message follows Conventional Commits |
| `claude-plugin` | compiles the hook and runs its unit tests on Python 3.9 |
| `docker` | after `server` and `client`: builds `tessio-api` and `tessio-client`; on `main` pushes them to GHCR tagged with the commit SHA and `main` |
| `deploy` | on a push to `main` when the repository variable `DEPLOY_ENABLED` is `true`: runs `deploy/deploy.sh` on the VPS over SSH, with the SSH secrets in the `production` environment |

`.github/workflows/e2e.yml` runs the end-to-end suite. CI has not run yet: the repository has no remote and no commits. Branching and commit messages follow [ADR 0008](docs/decisions/0008-branching-strategy.md) (trunk-based, Conventional Commits).

## Deploy

Tessio runs on a rented VPS with Docker Compose ([compose.prod.yml](compose.prod.yml)): Caddy in front, then `client`, `api`, `worker`, Postgres, Redis and RustFS ([ADR 0007](docs/decisions/0007-hosting-vps-docker.md), [ADR 0009](docs/decisions/0009-production-storage-and-proxy.md)).
`deploy/deploy.sh` pulls an image tag from GHCR, runs the migrations once, starts the stack and checks `/api/health/ready`.
The first install, staging, rollback and operations are in [deploy/README.md](deploy/README.md).

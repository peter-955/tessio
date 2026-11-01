# Tessio server

Python 3.14 + FastAPI, PostgreSQL, one app for the REST API, the MCP server (`/mcp`) and live events (`GET /api/events`, server-sent events), plus a BullMQ worker on Redis for background jobs. Decided in [ADR 0004](../docs/decisions/0004-backend-stack.md) and [ADR 0006](../docs/decisions/0006-background-jobs-redis-bullmq.md); the full design is in the [server proposal](../docs/discussions/server-proposal.md), and what each feature does today is in the [functional specs](../docs/spec/README.md).

## Run locally

Requires [uv](https://docs.astral.sh/uv/) and Docker.

```bash
docker compose up -d                       # from the repo root: Postgres, Redis, Bull Board, Mailpit, RustFS (S3)
cd server
cp .env.example .env                       # then set TESSIO_ENCRYPTION_KEY (see below)
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:create_production_app --factory --reload --port 3202
uv run python -m app.workers.worker        # in a second terminal: runs background jobs
```

- API: http://localhost:3202 · OpenAPI docs: http://localhost:3202/docs
- Worker: sends email (`email.send`), runs the Jira sync (`jira.sync_project`) and three maintenance schedules: `runs.abort_stale` every 15 minutes, `files.delete_orphans` at 03:00 and `sessions.delete_expired` at 03:30
- Emails (invites, password reset): queued in Redis, sent by the worker, caught by Mailpit at http://localhost:3207
- Queue: Bull Board at http://localhost:3205 (waiting, active, failed and retried jobs); Redis at localhost:3204 (`docker compose exec redis redis-cli`), BullMQ keys start with `bull:`
- MCP server: http://localhost:3202/mcp, authenticated with a personal `tsio_` API token; Claude Code setup in the [Claude setup guide](../docs/guides/claude-setup.md)
- File storage: RustFS (S3 API) at http://localhost:3208, bucket `tessio`
- Encryption key: `uv run python -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())"`

### Invite the first user

There is no public sign-up. Invite yourself from the command line, then open the link in the email in Mailpit (the worker must be running to send it):

```bash
uv run python -m app.commands.invite_user --email you@example.com --name "Your Name" --role owner
```

### Commands

Run from `server/` with `uv run python -m app.commands.<name>`:

- `invite_user`: invite a user by email (`--role owner` for the first one).
- `export_openapi`: write the OpenAPI document to `../client/src/lib/api/openapi.json`; then run `npm run generate:api` in `client/`.
- `jira_probe --issue SHOP-123`: fetch one issue through the saved Jira connection and print the AC the parser finds (`--raw` adds the description document).
- `seed_e2e`: reset the end-to-end database and seed its owner (guarded; used by the [e2e suite](../e2e/)).

## Checks

```bash
uv run ruff check . && uv run ruff format --check .
uv run lint-imports
uv run mypy
uv run pytest                              # starts its own Postgres and Redis in Docker
```

## Architecture

```
app/
├── main.py              create_app(container), create_production_app(): routers, error handlers, /mcp
├── container.py         the only place that builds adapters, repositories, use cases, MCP tools and jobs
├── config/settings.py   one <Concern>Settings class per concern, read from .env
├── commands/            command-line entrypoints (invite_user, export_openapi, jira_probe, seed_e2e)
├── workers/worker.py    background job worker: python -m app.workers.worker
├── api/                 cross-module HTTP pieces: error handlers, error response, origin check (not routers)
├── modules/<module>/
│   ├── router.py        routes: unpack input, call one use case, return a wire model; extra routers
│   │                    where a module serves several prefixes (auth/users_router.py, auth/me_router.py,
│   │                    runs/manual_router.py)
│   ├── dependencies.py  FastAPI dependencies (use cases from the container, current session)
│   ├── mcp_tools.py     register_<module>_tools: MCP tools calling the same use cases (runs, gaps, story_context)
│   ├── mcp_dependencies.py  API-token authentication for MCP calls (api_tokens)
│   ├── job_handlers/    <Verb><Noun>JobHandler classes run by the worker (auth, files, runs, stories)
│   ├── usecases/        one <Verb><Noun>UseCase per operation, one async execute
│   ├── domains/<name>/  entity.py (frozen Entity) + repository.py (ABC port)
│   ├── ports/           other ABC ports the use cases depend on
│   ├── infrastructure/  tables, Postgres repositories, adapters (argon2, pyotp…)
│   ├── models/          request / response WireModels (camelCase on the wire)
│   ├── utils/           pure helpers
│   ├── typing/          enums/ and constants/
│   └── errors.py        <What>Error(TessioError)
└── shared/              common (Entity, WireModel, TessioError, Transaction), crypto, events, logging, mailer,
                         masking, permissions, postgres, queue, rate_limit, storage, typing
```

- **Transactions:** a use case opens `async with self._transaction.begin():`. Repositories use the session of the open transaction; a nested `begin()` joins the outer one.
- **Import rules** (checked by `lint-imports`): `shared`, `config` and `api` never import `modules`; modules never import `api`; only the container imports a module's `infrastructure`. Modules form layers, lowest first, and a module imports only from lower layers (modules on the same layer never import each other):
  users < auth < projects < files | audit | notifications < api_tokens | jira | test_data < stories < test_cases < gaps < runs < failures < story_context | insights < live_events | health.
  A new module gets a place in `[tool.importlinter]` in `pyproject.toml`, and its sub-packages (never the whole module) are listed in the infrastructure contract.
- **Permissions:** a project use case calls `ProjectAccessResolver.resolve(actor, project_key)` and then `require(access, Capability.X)` from `app/shared/permissions/` (workspace actions use `require_workspace(actor, WorkspaceCapability.X)`). A non-member gets 404 `NOT_FOUND`, a missing capability 403 `PERMISSION_DENIED`, and a write on an archived project 409 `PROJECT_ARCHIVED`. The table is `role_capabilities.py`.
- **Live events:** after the transaction commits, a use case publishes a `LiveEvent` (a `LiveEventType`, a project or user id, and the ids it is about) through the `LiveEventPublisher` port. It goes out on the Redis channel `tessio:events`, and `GET /api/events` forwards it to every user who can see that project (or to that one user).
- **Files:** use the `ObjectStorage` port (`app/shared/storage/`): a signed POST upload with the size and content type enforced by storage, and a signed GET download link valid 5 minutes. Files never pass through the API.
- **MCP:** a module's `mcp_tools.py` has a `register_<module>_tools(server, …)` function that `Container.mcp_server` calls. Each tool authenticates the API token, then calls the same use case as the REST route with the token's `Actor`.
- **Background jobs:** code adds a job through the `JobQueue` port (`shared/queue/`) with a `QueueName` and `JobName` (`shared/typing/enums/queue.py`). A `JobHandler` runs it, and `container.py` maps each job name to its handler in a `BullmqJobWorker`. Email works this way: `QueuedMailer` adds `email.send`, and `SendEmailJobHandler` sends it with `SmtpMailer`.
- **Errors:** use cases raise a `TessioError` subclass; `app/api/error_handlers.py` maps its `ErrorCode` to the HTTP status and returns `{"code", "message"}`. A unique violation that reaches the database becomes 409 `CONFLICT`, and a character Postgres cannot store becomes 422 `INVALID_REQUEST`; translate a constraint into a specific code in the repository when the module has one (see `PostgresRunRepository.add`).
- **Rate limits:** `app/shared/rate_limit/` counts requests in Redis in fixed windows and fails open when Redis is down. Mount `limit_client_requests(<rule>)` from `auth/dependencies.py` with `dependencies=[Depends(...)]` on a route; a refusal is 429 `RATE_LIMITED` with `Retry-After`.
- **Text input:** `WireModel` and `ToolModel` refuse NUL characters (422 or a tool validation error); file imports strip them instead.
- **Security tests:** `tests/api/security/route_catalog.py` classifies every route (public, session, workspace, project read or write, API token) with its capability. A new route fails `test_route_inventory.py` until it is added there, and the sweeps then check it for 401, 404, 403 and 409.

## Adding a feature

1. Entity and repository port in `modules/<module>/domains/<name>/`.
2. Table and `Postgres<Name>Repository` in `infrastructure/`, exported from `infrastructure/__init__.py`.
3. Use case in `usecases/`, depending only on ports.
4. Wire it in `app/container.py` (and, for an MCP tool or job, in `Container.mcp_server` or `job_handlers` / `job_schedules`).
5. Route in `router.py`, dependency in `dependencies.py`, request/response models in `models/`.
6. Migration: add the table to `TABLES` in `migrations/env.py`, then `uv run alembic revision --autogenerate --rev-id <next> -m "<what>"` and remove the generated comment lines. The head is `0014`, so the next rev id is `0015`, chained from `0014`.
7. Tests in `tests/`, then run the checks.

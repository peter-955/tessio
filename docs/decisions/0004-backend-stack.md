# 0004. Backend stack: Python + FastAPI, PostgreSQL, one app for REST and MCP

**Status:** Accepted. Amended by [0005](0005-local-object-storage.md) (RustFS instead of MinIO locally), [0006](0006-background-jobs-redis-bullmq.md) (Redis + BullMQ instead of procrastinate) and [0007](0007-hosting-vps-docker.md) (a VPS with Docker instead of AWS). The app folder `backend/` was renamed to `server/` on 2026-11-01.
**Date:** 2026-10-31

## Context

- Tessio never runs a browser: Claude drives the real application through Claude in Chrome on the developer's machine, and testers run manual cases by hand ([testing workflow proposal](../discussions/testing-workflow-proposal.md)). The backend stores cases and data, takes in results, serves files, syncs Jira and exposes an MCP server.
- That removes the main reason to stay on Node.js (running Playwright ourselves), so the language can be picked on fit and on the team's wish to grow in a second language.
- One company, several projects, roles per project, required 2FA, secrets, screenshots kept forever ([platform features proposal](../discussions/platform-features-proposal.md)).
- Live run progress is needed in MVP ([open question 4](../discussions/open-questions.md)).
- Hosting is AWS (ECS Fargate, RDS, S3, SES); Jira is Jira Cloud with a service-account API token.

## Options considered

1. **Python + FastAPI**: OpenAPI generated from the request and response models; SQLAlchemy 2 and Alembic are very mature; async from the ground up, which fits server-sent events and MCP streaming; strong data and AI libraries for later features (Sheets import, Claude-drafted test cases). Cons: a second language next to the client, and sign-in has to be built from libraries (no Better Auth equivalent).
2. **NestJS + PostgreSQL**: same language as the client and the team's strongest; Better Auth covers most of sign-in. Cons: no learning gain, and OpenAPI needs extra decorators.
3. **Django**: sessions, admin and migrations built in. Cons: synchronous at heart, a poor fit for live events and MCP streaming.
4. **Next.js route handlers only**: fewest moving parts. Cons: background jobs, MCP and live events fit badly, and UI and API code mix.

## Decision

**Python 3.14 + FastAPI**, in `backend/`, as one app that serves the REST API, the MCP server (`/mcp`) and live events, plus a worker process from the same code.

| Concern | Choice |
| --- | --- |
| Tooling | `uv`, `ruff`, `mypy --strict`, `pytest`, `import-linter` (same as our existing Python service) |
| Database | PostgreSQL, SQLAlchemy 2 async (`asyncpg`), Alembic |
| Jobs | `procrastinate` on Postgres (no Redis) |
| MCP | Official `mcp` Python SDK, Streamable HTTP |
| Live updates | Server-sent events fed by Postgres `LISTEN / NOTIFY` |
| Auth | Own code on `argon2-cffi`, `pyotp`, server-side sessions in Postgres; personal API tokens for MCP |
| Encryption | `cryptography` AES-256-GCM |
| Files | `boto3` signed links; MinIO locally, S3 on AWS |
| Email | `aiosmtplib`; Mailpit locally, SES over SMTP on AWS |

The details (layout, schema, endpoints, MCP tools, screenshot flow) are in the [server proposal](../discussions/server-proposal.md).

## Consequences

- Local services stay at three containers: Postgres, MinIO, Mailpit.
- REST routes and MCP tools call the same use cases, so permissions are checked in one place.
- The client gets its API types from the backend's OpenAPI spec (`openapi-typescript`) and replaces the mock data in `client/src/shared/data/`.
- We own the security-critical sign-in code. This is covered by the permission tests (WBS 6.3) and the security review (WBS 6.5), and only well-tested libraries are used, never our own cryptography.
- Claude reports results once per test case, and screenshots go from the developer's machine to S3 through a hook, never through the model.
- Follow-up: the spikes listed in the [server proposal §16](../discussions/server-proposal.md#16-spikes-before-building).

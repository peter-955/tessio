# 0007. Hosting: a rented VPS with Docker instead of AWS

**Status:** Accepted. Amends [0004](0004-backend-stack.md) (the hosting context) and the [server proposal §14](../discussions/server-proposal.md#14-local-development-and-deployment). Amended by [0009](0009-production-storage-and-proxy.md) (storage and reverse proxy).
**Date:** 2026-11-01

## Context

- ADR 0004 and the backend proposal assumed AWS: ECS Fargate, RDS, S3, SES, Secrets Manager, CloudWatch.
- The team deploys its projects on a rented VPS with Docker and uses few AWS services.

## Options considered

1. **VPS + Docker Compose**: the way the team already works; the same containers as local development; one fixed monthly price. Cons: we run backups, TLS and updates ourselves.
2. **AWS ECS Fargate and managed services**: managed scaling and backups. Cons: more services to learn and pay for than Tessio needs.

## Decision

Deploy Tessio with **Docker Compose on a rented VPS**: `client`, `api`, `worker` (the same backend image as `api`, different command), `postgres` and `redis`, behind a reverse proxy that sends `/api/*` and `/mcp` to `api` and everything else to `client`.

## Consequences

- Secrets (`TESSIO_ENCRYPTION_KEY`, database and SMTP passwords) come from the server's environment, not a secrets manager.
- Migrations run as a one-off `docker compose run api alembic upgrade head` before each deploy.
- Redis and Postgres are reachable only inside the Docker network, never published on the VPS's public ports.
- Still to decide: production file storage (RustFS on the VPS, as locally, or a hosted S3-compatible service), the SMTP provider for email, the reverse proxy, and backups.

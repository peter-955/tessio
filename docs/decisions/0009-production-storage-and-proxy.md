# 0009. Production file storage and reverse proxy: RustFS and Caddy on the VPS

**Status:** Accepted. Amends [0005](0005-local-object-storage.md) and [0007](0007-hosting-vps-docker.md).
**Date:** 2026-11-01

## Context

- [ADR 0007](0007-hosting-vps-docker.md) moved hosting to a rented VPS with Docker Compose, but left four things open: production file storage, the reverse proxy, the SMTP provider and backups.
- [ADR 0005](0005-local-object-storage.md) chose RustFS for local development only.
- The production files were then built with RustFS and Caddy: [compose.prod.yml](../../compose.prod.yml), [deploy/Caddyfile](../../deploy/Caddyfile) and [deploy/deploy.sh](../../deploy/deploy.sh). This ADR records that choice.
- Files go straight between the browser (or the Claude upload hook) and storage through signed POST uploads and signed GET downloads, so storage needs its own public HTTPS address.
- Live events (`GET /api/events`) and the MCP endpoint (`/mcp`) stream responses. A proxy that buffers or compresses them holds events back ([server proposal §16](../discussions/server-proposal.md#16-spikes-before-building), spike 3).

## Options considered

Storage:

1. **RustFS on the VPS**: the same image and S3 API as local development, no extra account or bill, and the data stays on our server. Cons: we run the backups ourselves, and there is no lifecycle rule yet.
2. **A hosted S3-compatible service**: managed durability and lifecycle rules. Cons: another provider, account and monthly bill, and the files leave the VPS.

Reverse proxy:

1. **Caddy**: automatic TLS certificates, a short config file, and `flush_interval -1` to stream responses at once.
2. **nginx**: well known, but TLS needs certbot or a companion container, and buffering must be turned off per location.
3. **Traefik**: automatic TLS too, but the routes live in container labels, which is more setup than three routes need.

## Decision

- Run **RustFS 1.0.4** (`rustfs/rustfs:1.0.4`) on the VPS behind Caddy on its own domain, `STORAGE_DOMAIN`. The bucket is private. The one-off `rustfs-bucket` container creates it and sets the bucket CORS rule that allows `POST`, `GET` and `HEAD` from `https://$TESSIO_DOMAIN`.
- Run **Caddy 2.11** (`caddy:2.11.7-alpine`) as the only public service, on ports 80 and 443, with automatic TLS. On `TESSIO_DOMAIN` it sends `/api/*` and `/mcp` to `api:8000` with `flush_interval -1` and no `encode`, and everything else to `client:3000` with `encode zstd gzip`. On `STORAGE_DOMAIN` it sends everything to `rustfs:9000`.
- `api` is reachable only through Caddy on the Docker network, so uvicorn trusts the forwarded headers from any address (`--proxy-headers --forwarded-allow-ips "*"`) and the rate limits see the real client IP.

## Consequences

- The `rustfs-data` volume holds every screenshot and file, so it needs backups. Backups of it and of `postgres-data` are still open ([deploy/README.md](../../deploy/README.md#not-decided-yet)).
- There is no lifecycle rule yet. Screenshots are kept forever on the VPS disk; a 90-day rule is planned but not set up.
- The SMTP provider is still open. The SMTP settings in `.env` are configuration only.
- Switching to a hosted S3-compatible service is configuration: `S3_ENDPOINT_URL`, `S3_PUBLIC_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET` and the access keys, plus the same CORS rule on the new bucket. The `rustfs` and `rustfs-bucket` services and the `STORAGE_DOMAIN` site can then be removed.
- Streaming through Caddy is configured but not yet tested on a VPS.

# Deploying Tessio

Tessio runs on a rented VPS with Docker Compose ([ADR 0007](../docs/decisions/0007-hosting-vps-docker.md)). CI builds `tessio-api` and `tessio-client` images, tags them with the commit SHA and `main`, and pushes them to GHCR. `deploy/deploy.sh` pulls a tag and starts it.

| Service | Image | Reachable from |
| --- | --- | --- |
| `caddy` | `caddy` | the internet, ports 80 and 443 (automatic TLS) |
| `client` | `tessio-client` | Caddy, every path except `/api/*` and `/mcp` |
| `api` | `tessio-api` | Caddy, `/api/*` and `/mcp` (no compression, flushed at once for SSE) |
| `worker` | `tessio-api` | nothing (runs background jobs) |
| `postgres`, `redis` | official images | the Docker network only |
| `rustfs` | `rustfs/rustfs` | Caddy, on `STORAGE_DOMAIN` (signed upload and download links) |
| `bull-board` | `venatum/bull-board` | `127.0.0.1:3205` on the VPS only, through an SSH tunnel |

## VPS prerequisites

- A Linux VPS with Docker Engine and the Compose plugin (`docker compose version` 2.24 or later).
- DNS `A`/`AAAA` records for `TESSIO_DOMAIN` and `STORAGE_DOMAIN` pointing to the VPS.
- Ports 80 and 443 (TCP and UDP) open; every other port closed.
- `docker login ghcr.io` with a token that can read the packages, if the images are private.
- A deploy user that is in the `docker` group and whose SSH key is the `VPS_SSH_KEY` CI secret.

## First install

```bash
sudo mkdir -p /opt/tessio && sudo chown "$USER" /opt/tessio
cd /opt/tessio
# copy compose.prod.yml, deploy/ and .env.production.example from the repository
cp .env.production.example .env
chmod 600 .env
# fill in .env: domains, POSTGRES_PASSWORD (also inside DATABASE_URL), TESSIO_ENCRYPTION_KEY,
# storage keys, SMTP, BULL_BOARD_PASSWORD
./deploy/deploy.sh
```

Generate the encryption key with `python3 -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())"`. Keep a copy outside the VPS: without it, stored secrets cannot be decrypted.

`/opt/tessio` holds only `compose.prod.yml`, `deploy/` (`Caddyfile`, `deploy.sh`) and `.env`. Data lives in the Docker volumes `postgres-data`, `redis-data`, `rustfs-data` and `caddy-data`.

## Deploying a version

`deploy.sh` pulls the images, starts Postgres, Redis and RustFS, runs `alembic upgrade head` once in a throwaway `api` container, starts everything with `up -d --wait`, checks `/api/health/ready` and prunes old images.

```bash
cd /opt/tessio
TESSIO_IMAGE_TAG=<commit sha> ./deploy/deploy.sh   # a specific build
./deploy/deploy.sh                                 # the TESSIO_IMAGE_TAG in .env (main by default)
```

To roll back, deploy the previous SHA. Migrations are not rolled back automatically.

The CI `deploy` job does the same over SSH after each merge to `main`, once the repository variable `DEPLOY_ENABLED` is `true` and the secrets `VPS_HOST`, `VPS_USER` and `VPS_SSH_KEY` exist in the `production` environment.

## Staging

Staging uses the same files with another project name and its own `.env` (other domains, passwords and keys), in its own folder:

```bash
cd /opt/tessio-staging
COMPOSE_PROJECT_NAME=tessio-staging TESSIO_IMAGE_TAG=<commit sha> ./deploy/deploy.sh
```

Only one Caddy can own ports 80 and 443 on a VPS, so staging on the same VPS as production needs its domains added to the production Caddyfile instead of its own `caddy` service. A separate staging VPS needs no change.

## Operations

- Logs: `docker compose -f compose.prod.yml --env-file .env logs -f api worker`. The server writes one JSON object per line; Docker rotates each container's log at 10 MB, keeping 5 files.
- Bull Board (queues and failed jobs): start it with `docker compose -f compose.prod.yml --env-file .env --profile ops up -d bull-board`, open a tunnel with `ssh -L 3205:127.0.0.1:3205 <user>@<vps>`, browse http://localhost:3205 and sign in with `BULL_BOARD_USER` / `BULL_BOARD_PASSWORD`. Stop it when you are done.
- Health: `GET /api/health` (the process is up) and `GET /api/health/ready` (Postgres and Redis answer; 503 otherwise).
- Errors: set `SENTRY_DSN` (Sentry or a compatible service such as GlitchTip) to report errors; leave it empty to turn reporting off.
- Database shell: `docker compose -f compose.prod.yml --env-file .env exec postgres psql -U tessio`.

## Not decided yet

- The VPS provider, the domain and DNS, and whether staging shares the production VPS.
- Backups of the Postgres and RustFS volumes.
- An uptime monitor and the error tracking service.
- A 90-day lifecycle rule for screenshots in RustFS (not set up).

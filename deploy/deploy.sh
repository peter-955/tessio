#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -f .env ]]; then
  echo "deploy: .env is missing in $(pwd); copy .env.production.example to .env and fill it in" >&2
  exit 1
fi

COMPOSE="docker compose -f compose.prod.yml --env-file .env"

echo "deploy: project ${COMPOSE_PROJECT_NAME:-tessio}, image tag ${TESSIO_IMAGE_TAG:-from .env}"

$COMPOSE pull
$COMPOSE up -d --wait postgres redis rustfs
$COMPOSE run --rm --no-deps api alembic upgrade head
$COMPOSE up -d --remove-orphans --wait
$COMPOSE exec -T api python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health/ready', timeout=5)"
docker image prune -f

echo "deploy: done"

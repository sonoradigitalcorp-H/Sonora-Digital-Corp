#!/usr/bin/env bash
# Sonora Digital Corp — Tail logs from a service
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
docker compose \
  -f "$DIR/infra/docker-compose.yml" \
  -f "$DIR/infra/docker-compose.products.yml" \
  -p sdc \
  logs -f "$@"

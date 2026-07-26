#!/usr/bin/env bash
# Sonora Digital Corp — Stop all services (core + products)
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
docker compose \
  -f "$DIR/infra/docker-compose.yml" \
  -f "$DIR/infra/docker-compose.products.yml" \
  -p sdc \
  down "$@"

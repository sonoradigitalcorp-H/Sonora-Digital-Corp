#!/bin/bash
# Test: E2E for specific client
set -e

CLIENT="${1:-}"
if [ -z "$CLIENT" ]; then
  echo "Usage: $0 <client-name>"
  echo "Available clients:"
  ls sonora-digital-corp/tenants/
  exit 1
fi

echo "Running E2E tests for client: $CLIENT"
cd sonora-digital-corp && python -m pytest tests/e2e -k "$CLIENT" -v --tb=short
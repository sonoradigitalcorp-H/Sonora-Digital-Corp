#!/bin/bash
# Client: Provision tenant infrastructure
set -e

CLIENT="${1:-}"
if [ -z "$CLIENT" ]; then
  echo "Usage: $0 <client-name>"
  exit 1
fi

echo "Provisioning infrastructure for client: $CLIENT"

# Run the provision tenant script
cd sonora-digital-corp && python scripts/provision_tenant.py "$CLIENT"

# Also run the shell provisioning for additional setup
bash scripts/provision-tenant.sh "$CLIENT"

echo "Provisioning complete for $CLIENT"
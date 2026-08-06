#!/bin/bash
# Client: Onboard new client with full setup
set -e

CLIENT="${1:-}"
if [ -z "$CLIENT" ]; then
  echo "Usage: $0 <client-name>"
  exit 1
fi

echo "Onboarding client: $CLIENT"
echo ""

# 1. Create tenant directory structure
echo "=== Creating tenant structure ==="
mkdir -p "sonora-digital-corp/tenants/$CLIENT"/{config,secrets,campaigns,analytics,mcp,deployments}

# 2. Generate tenant config
echo "=== Generating tenant config ==="
cat > "sonora-digital-corp/tenants/$CLIENT/config/tenant.json" << EOF
{
  "tenant_id": "$CLIENT",
  "name": "$CLIENT",
  "created_at": "$(date -Iseconds)",
  "status": "provisioning",
  "services": [],
  "mcp_servers": [],
  "domains": [],
  "environment": "staging"
}
EOF

# 3. Run provisioning script
echo "=== Running provisioning ==="
bash scripts/tenant/create.sh "$CLIENT"

# 4. Configure MCPs
echo "=== Configuring MCPs ==="
bash scripts/mcp/connect.sh "$CLIENT"

# 5. Create default landing page
echo "=== Creating default landing ==="
bash scripts/web/create-landing.sh "$CLIENT"

echo ""
echo "Client $CLIENT onboarded successfully!"
echo "Tenant: sonora-digital-corp/tenants/$CLIENT"
echo "Next steps:"
echo "  1. Configure DNS in tenant config"
echo "  2. Add MCP servers: opencode run mcp:connect $CLIENT"
echo "  3. Deploy: opencode run tenant:deploy $CLIENT"
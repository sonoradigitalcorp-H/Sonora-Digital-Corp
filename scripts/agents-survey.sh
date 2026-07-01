#!/bin/bash
# Domain Health Survey — Reporta estado de todos los contenedores por dominio
set -euo pipefail

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         ✦ SDC AGENT SURVEY — Container Health ✦          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Use docker compose if available
COMPOSE_CMD="docker compose -f infra/docker-compose.yml"
if ! docker compose &>/dev/null; then
  COMPOSE_CMD="docker-compose -f infra/docker-compose.yml"
fi

for domain in data core ux; do
  echo "━━━ DOMAIN: $domain ━━━"
  echo ""
  
  # Get containers in this domain (by label or name pattern)
  CONTAINERS=$(docker ps --filter "label=sdc.domain=$domain" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || true)
  if [ -z "$CONTAINERS" ]; then
    echo "  (no containers in this domain)"
  else
    echo "$CONTAINERS"
  fi
  echo ""
done

echo "━━━ HEALTH ENDPOINTS ━━━"
echo ""

# Check key HTTP endpoints
check_endpoint() {
  local name=$1
  local url=$2
  local status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "$url" 2>/dev/null || echo "000")
  if [ "$status" = "200" ]; then
    echo "  ✅ $name → $status"
  elif [ "$status" = "000" ]; then
    echo "  ❌ $name → no response"
  else
    echo "  ⚠️  $name → $status"
  fi
}

check_endpoint "JARVIS WebUI" "http://127.0.0.1:5174/api/enterprise-score"
check_endpoint "n8n" "http://127.0.0.1:5678/healthz"
check_endpoint "MCP Server" "http://127.0.0.1:8000/"
check_endpoint "Langfuse" "http://127.0.0.1:3000/api/public/health"
check_endpoint "Qdrant" "http://127.0.0.1:6333/healthz"
check_endpoint "Neo4j" "http://127.0.0.1:7474"

echo ""
echo "━━━ REDIS STREAMS ━━━"
echo ""
docker exec sdc-redis redis-cli -a "${REDIS_PASSWORD:-sdc2026prod}" \
  INFO streams 2>/dev/null | grep -E "streams|length" | head -5 || echo "  (no stream info available)"

docker exec sdc-redis redis-cli -a "${REDIS_PASSWORD:-sdc2026prod}" \
  XLEN context:history 2>/dev/null && \
docker exec sdc-redis redis-cli -a "${REDIS_PASSWORD:-sdc2026prod}" \
  XLEN events:pipeline 2>/dev/null || echo "  Streams not accessible"

echo ""
echo "━━━ SYSTEM ━━━"
echo ""
echo "  Uptime: $(uptime -p | sed 's/up //')"
echo "  Memory: $(free -h | awk '/Mem:/ {print $3 "/" $2}')"
echo "  Disk:   $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo ""
echo "╚══════════════════════════════════════════════════════════════╝"

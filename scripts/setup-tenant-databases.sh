#!/bin/bash
# setup-tenant-databases.sh
# Creates Qdrant collections and Neo4j databases for all tenants
# Usage: ./scripts/setup-tenant-databases.sh [tenant_id]
#   Without args: create all tenants from registry
#   With tenant_id: create only that tenant

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TENANTS_DIR="$REPO/tenants"
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
NEO4J_URL="${NEO4J_URL:-http://localhost:7474}"
NEO4J_AUTH="${NEO4J_AUTH:-neo4j/password}"
VECTOR_SIZE="${VECTOR_SIZE:-768}"

echo "=== Tenant Database Setup ==="
echo "Qdrant: $QDRANT_URL"
echo "Neo4j:  $NEO4J_URL"
echo ""

# Determine which tenants to process
if [ $# -ge 1 ]; then
    TENANTS=("$1")
else
    TENANTS=()
    for d in "$TENANTS_DIR"/*/; do
        name=$(basename "$d")
        [ "$name" = "_template" ] && continue
        [ -f "$d/config.yaml" ] && TENANTS+=("$name")
    done
fi

for tenant_id in "${TENANTS[@]}"; do
    config_file="$TENANTS_DIR/$tenant_id/config.yaml"
    if [ ! -f "$config_file" ]; then
        echo "⚠️  Skipping $tenant_id — no config.yaml found"
        continue
    fi

    # Extract config values
    qdrant_collection=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file')).get('qdrant_collection', 'tenant_${tenant_id}_memory'))" 2>/dev/null)
    neo4j_database=$(python3 -c "import yaml; print(yaml.safe_load(open('$config_file')).get('neo4j_database', '${tenant_id}'))" 2>/dev/null)

    echo "--- $tenant_id ---"
    echo "  Qdrant collection: $qdrant_collection"
    echo "  Neo4j database:    $neo4j_database"

    # ─── Qdrant: Create collection ───
    echo -n "  Qdrant: "
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X PUT "$QDRANT_URL/collections/$qdrant_collection" \
        -H "Content-Type: application/json" \
        -d "{
            \"vectors\": {
                \"size\": $VECTOR_SIZE,
                \"distance\": \"Cosine\"
            }
        }" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        echo "✅ Created collection '$qdrant_collection'"
    elif [ "$http_code" = "409" ]; then
        echo "⏩ Collection '$qdrant_collection' already exists"
    else
        echo "⚠️  HTTP $http_code (Qdrant may not be running)"
    fi

    # ─── Neo4j: Create database ───
    echo -n "  Neo4j: "
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$NEO4J_URL/db/data/transaction/commit" \
        -H "Content-Type: application/json" \
        -H "Authorization: Basic $(echo -n "$NEO4J_AUTH" | base64)" \
        -d "{\"statements\": [{\"statement\": \"CREATE DATABASE $neo4j_database IF NOT EXISTS\"}]}" \
        2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        echo "✅ Created database '$neo4j_database'"
    elif [ "$http_code" = "000" ]; then
        echo "⚠️  Could not connect to Neo4j (is it running?)"
    else
        echo "⚠️  HTTP $http_code — may need manual Neo4j setup"
    fi

    echo ""
done

echo "=== Done ==="

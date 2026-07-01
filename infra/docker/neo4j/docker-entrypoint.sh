#!/bin/bash
set -e

# Start Neo4j in the background
neo4j start

# Wait for Neo4j to be ready (with timeout)
echo "Waiting for Neo4j to be ready..."
MAX_RETRIES=30
count=0
until cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1" > /dev/null 2>&1; do
  count=$((count + 1))
  if [ $count -ge $MAX_RETRIES ]; then
    echo "WARNING: Neo4j did not become ready after $MAX_RETRIES attempts. Check password or logs."
    break
  fi
  sleep 2
done
echo "Neo4j is ready."

# Run init script if it exists
if [ -f "/init.cypher" ]; then
  echo "Running init.cypher..."
  cypher-shell -u neo4j -p "$NEO4J_PASSWORD" -f /init.cypher || true
  echo "Schema initialization complete."
fi

# Keep Neo4j running in foreground
neo4j stop || true
exec neo4j console

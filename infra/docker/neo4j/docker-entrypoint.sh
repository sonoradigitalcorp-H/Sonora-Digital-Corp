#!/bin/bash
set -e

# Start Neo4j in the background
neo4j start

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready..."
until cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1" > /dev/null 2>&1; do
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
neo4j stop
exec neo4j console

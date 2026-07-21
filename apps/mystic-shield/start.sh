#!/bin/bash
# Mystic Shield — Start all services
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$BASE_DIR/../.." && pwd)"

echo "🚀 Mystic Shield — Starting services..."
echo ""

# ── MCP Shield Server (port 8930) ──
echo "[1/3] Starting MCP Shield server on :8930..."
cd "$REPO_DIR"
python3 -m mcp.servers.shield_mcp --http 8930 &
MCP_PID=$!
echo "  PID: $MCP_PID"

# ── FastAPI Backend (port 8931) ──
echo "[2/3] Starting FastAPI API on :8931..."
cd "$REPO_DIR/apps/mystic-shield/api"
python3 main.py &
API_PID=$!
echo "  PID: $API_PID"

# ── Landing page served by API (already mounted in FastAPI) ──
echo "[3/3] Landing served at http://localhost:8931"
echo ""
echo "✅ Mystic Shield running:"
echo "   Landing + API:  http://localhost:8931"
echo "   MCP Server:     http://localhost:8930"
echo "   Health check:   http://localhost:8931/api/health"
echo ""
echo "Press Ctrl+C to stop all services."

trap "echo ''; echo '🛑 Stopping...'; kill $MCP_PID $API_PID 2>/dev/null; exit 0" INT TERM
wait

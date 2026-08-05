#!/bin/bash
# Harvis OS - System Status Monitor
# Ejecutar: ./status.sh

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              HARVIS OS — SYSTEM STATUS                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "📦 DOCKER"
echo "─────────────────────────────────────────────────────────────"
docker ps --format '  {{.Names}} → {{.Status}}' 2>/dev/null
echo ""

echo "🤖 OLLAMA"
echo "─────────────────────────────────────────────────────────────"
curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d['models']:
    size_gb = m['size'] / (1024**3)
    print(f'  ✅ {m[\"name\"]:25} {size_gb:.1f} GB')
" 2>/dev/null || echo "  ❌ Ollama not responding"
echo ""

echo "🚀 HARVIS OS"
echo "─────────────────────────────────────────────────────────────"
curl -s http://localhost:8001/ 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'  Version:    {d[\"version\"]}')
r = d['components']['registry']
print(f'  Agents:     {r[\"total_agents\"]} registered ({r[\"online_agents\"]} online)')
e = d['components']['event_bus']
print(f'  Events:     {e[\"total_events\"]} published')
p = d['components']['planner']
print(f'  Plans:      {p[\"total_plans\"]} created')
print(f'  API Docs:   http://localhost:8001/docs')
" 2>/dev/null || echo "  ❌ Harvis OS not responding"
echo ""

echo "🔗 PORTS"
echo "─────────────────────────────────────────────────────────────"
for port in 5432 6379 6333 8001 11434 5678; do
    if nc -z localhost $port 2>/dev/null; then
        echo "  ✅ $port"
    else
        echo "  ❌ $port"
    fi
done
echo ""

echo "📊 TESTS"
echo "─────────────────────────────────────────────────────────────"
cd "$(dirname "$0")" && python -m pytest tests/ -q --tb=no 2>/dev/null | tail -1
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  API Docs: http://localhost:8001/docs                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"

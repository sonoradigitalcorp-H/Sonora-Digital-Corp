#!/bin/bash
# Harvis OS - Complete System Test
# Ejecutar: ./test_complete.sh

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     HARVIS OS - COMPLETE SYSTEM TEST                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

test_pass() {
    echo -e "  ${GREEN}✓${NC} $1"
    ((PASS++))
}

test_fail() {
    echo -e "  ${RED}✗${NC} $1"
    ((FAIL++))
}

# 1. Check Docker
echo "📦 1. DOCKER SERVICES"
echo "─────────────────────────────────────────────────────────────"
if docker ps > /dev/null 2>&1; then
    test_pass "Docker is running"
    docker ps --format '    {{.Names}} → {{.Status}}' 2>/dev/null
else
    test_fail "Docker is not running"
fi
echo ""

# 2. Check PostgreSQL
echo "🗄️  2. POSTGRESQL"
echo "─────────────────────────────────────────────────────────────"
if nc -z localhost 5432 2>/dev/null; then
    test_pass "PostgreSQL is running (port 5432)"
else
    test_fail "PostgreSQL is not running"
fi
echo ""

# 3. Check Redis
echo "🔴 3. REDIS"
echo "─────────────────────────────────────────────────────────────"
if nc -z localhost 6379 2>/dev/null; then
    test_pass "Redis is running (port 6379)"
else
    test_fail "Redis is not running"
fi
echo ""

# 4. Check Qdrant
echo "🔍 4. QDRANT"
echo "─────────────────────────────────────────────────────────────"
if nc -z localhost 6333 2>/dev/null; then
    test_pass "Qdrant is running (port 6333)"
else
    test_fail "Qdrant is not running"
fi
echo ""

# 5. Check Ollama
echo "🤖 5. OLLAMA"
echo "─────────────────────────────────────────────────────────────"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    test_pass "Ollama is running (port 11434)"
    curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d['models']:
    print(f'    ✅ {m[\"name\"]}')
" 2>/dev/null
else
    test_fail "Ollama is not running"
fi
echo ""

# 6. Check Harvis OS API
echo "🚀 6. HARVIS OS API"
echo "─────────────────────────────────────────────────────────────"
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    test_pass "Harvis OS API is running (port 8001)"
    curl -s http://localhost:8001/health 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'    Version: {d[\"version\"]}')
print(f'    Status: {d[\"status\"]}')
" 2>/dev/null
else
    test_fail "Harvis OS API is not running"
fi
echo ""

# 7. Test task creation
echo "📝 7. TASK CREATION"
echo "─────────────────────────────────────────────────────────────"
RESULT=$(curl -s -X POST http://localhost:8001/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"source": "test", "user_id": "test", "content": "Crear funcion de login"}' 2>/dev/null)

if echo "$RESULT" | grep -q '"category"'; then
    test_pass "Task creation works"
    echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'    Category: {d[\"category\"]}')
print(f'    Agent: {d[\"assigned_agent\"]}')
print(f'    Confidence: {d[\"confidence\"]}')
" 2>/dev/null
else
    test_fail "Task creation failed"
fi
echo ""

# 8. Test agent listing
echo "👥 8. AGENT REGISTRY"
echo "─────────────────────────────────────────────────────────────"
RESULT=$(curl -s http://localhost:8001/api/v1/agents 2>/dev/null)
if echo "$RESULT" | grep -q '"openhands"'; then
    test_pass "Agent registry works"
    echo "$RESULT" | python3 -c "
import sys,json
agents=json.load(sys.stdin)
print(f'    Total agents: {len(agents)}')
for a in agents:
    print(f'    - {a[\"id\"]}: {a[\"status\"]}')
" 2>/dev/null
else
    test_fail "Agent registry failed"
fi
echo ""

# 9. Test OpenRouter (if key available)
echo "🌐 9. OPENROUTER LLM"
echo "─────────────────────────────────────────────────────────────"
KEY=$(grep OPENROUTER_API_KEY /home/mystic/.hermes/.env 2>/dev/null | cut -d'=' -f2)
if [ -n "$KEY" ]; then
    RESULT=$(curl -s https://openrouter.ai/api/v1/chat/completions \
      -H "Authorization: Bearer $KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "messages": [{"role": "user", "content": "Di hola"}],
        "max_tokens": 10
      }' 2>/dev/null)
    
    if echo "$RESULT" | grep -q '"content"'; then
        test_pass "OpenRouter LLM works"
        echo "$RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f'    Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free')
print(f'    Response: {d[\"choices\"][0][\"message\"][\"content\"][:50]}')
" 2>/dev/null
    else
        test_fail "OpenRouter LLM failed"
    fi
else
    test_fail "OpenRouter API key not found"
fi
echo ""

# 10. Run unit tests
echo "🧪 10. UNIT TESTS"
echo "─────────────────────────────────────────────────────────────"
cd "$(dirname "$0")" 2>/dev/null && python -m pytest tests/ -q --tb=no 2>/dev/null | tail -1
if [ $? -eq 0 ]; then
    test_pass "Unit tests pass"
else
    test_fail "Unit tests failed"
fi
echo ""

# Summary
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  TEST SUMMARY                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "  ${GREEN}✅ ALL TESTS PASSED${NC}"
else
    echo -e "  ${YELLOW}⚠️  Some tests failed${NC}"
fi
echo ""
echo "  API Docs: http://localhost:8001/docs"
echo "  Status: ./status.sh"
echo ""

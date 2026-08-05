#!/bin/bash
# Harvis OS - Quick Start Script
# Verifica servicios y ejecuta Harvis OS

set -e

echo "🚀 Harvis OS - Quick Start"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check functions
check_service() {
    local name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "${RED}✗${NC} $name is not running"
        return 1
    fi
}

echo "📋 Checking services..."
echo ""

# Check Docker
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC} Docker is installed"
else
    echo -e "${RED}✗${NC} Docker is not installed"
fi

# Check services
check_service "PostgreSQL" "http://localhost:5432" || true
check_service "Redis" "http://localhost:6379" || true
check_service "Qdrant" "http://localhost:6333/healthz" || true
check_service "Ollama" "http://localhost:11434/api/tags" || true

echo ""

# Check Ollama models
echo "📋 Checking Ollama models..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "$models" | while read model; do
        echo -e "  ${GREEN}✓${NC} $model"
    done
else
    echo -e "${YELLOW}⚠${NC} Ollama not available"
fi

echo ""

# Check if qwen3:4b is available
if ollama list 2>/dev/null | grep -q "qwen3:4b"; then
    echo -e "${GREEN}✓${NC} qwen3:4b model available"
else
    echo -e "${YELLOW}⚠${NC} qwen3:4b not found. Run: ollama pull qwen3:4b"
fi

echo ""
echo "=========================="
echo ""

# Ask user what to do
echo "What would you like to do?"
echo ""
echo "1) Start Harvis OS API (port 8000)"
echo "2) Run tests"
echo "3) Start with Docker"
echo "4) Check status only"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Harvis OS API..."
        cd "$(dirname "$0")"
        uvicorn src.core.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo ""
        echo "🧪 Running tests..."
        cd "$(dirname "$0")"
        python -m pytest tests/ -v
        ;;
    3)
        echo ""
        echo "🐳 Starting with Docker..."
        cd "$(dirname "$0")"
        docker compose -f docker-compose.local.yml up
        ;;
    4)
        echo ""
        echo "📊 Status check complete."
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

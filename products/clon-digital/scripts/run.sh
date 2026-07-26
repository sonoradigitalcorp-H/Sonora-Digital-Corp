#!/bin/bash
set -e

echo "🚀 Clon Digital - Deployment"
echo "============================"

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example to .env and configure it."
    exit 1
fi

# Build and start
echo "📦 Building containers..."
docker compose build

echo "🐳 Starting services..."
docker compose up -d

echo ""
echo "✅ Clon Digital is running!"
echo "   Dashboard: http://localhost/dashboard"
echo "   API:       http://localhost/api/v1/orders"
echo "   Health:    http://localhost/health"
echo ""
echo "📋 Logs: docker compose logs -f"

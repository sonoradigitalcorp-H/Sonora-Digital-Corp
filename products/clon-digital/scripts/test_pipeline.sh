#!/bin/bash
set -e

BASE="http://localhost:8000"
FAL_BASE="http://localhost:8001"
IMAGE_URL="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
AUDIO_URL="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

echo "🧪 Testing FAL Wrapper..."

echo "1. Health check..."
curl -s "$FAL_BASE/health" | jq .

echo ""
echo "2. Generate TTS..."
TTS_RESULT=$(curl -s -X POST "$FAL_BASE/v1/tts" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hola, este es tu video personalizado. Espero que te guste.", "language": "es", "voice": "seed-audio"}')
echo "$TTS_RESULT" | jq .
AUDIO_URL=$(echo "$TTS_RESULT" | jq -r '.audio_url')

echo ""
echo "3. Generate talking head..."
curl -s -X POST "$FAL_BASE/v1/talking-head" \
    -H "Content-Type: application/json" \
    -d "{\"image_url\": \"$IMAGE_URL\", \"audio_url\": \"$AUDIO_URL\", \"model\": \"sync-lipsync-v3\"}" | jq .

echo ""
echo "🧪 Testing Orchestrator..."

echo "4. Health check..."
curl -s "$BASE/health" | jq .

echo ""
echo "5. Create order..."
ORDER_RESULT=$(curl -s -X POST "$BASE/api/v1/orders" \
    -H "Content-Type: application/json" \
    -d '{
        "client_name": "Test User",
        "client_phone": "+521234567890",
        "script": "Hola, este es un mensaje de prueba para ti.",
        "product_type": "video_bienvenida"
    }')
echo "$ORDER_RESULT" | jq .

echo ""
echo "✅ Tests completed!"

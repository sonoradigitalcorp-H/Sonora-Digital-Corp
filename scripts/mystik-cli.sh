#!/bin/bash
# Mystik CLI — Interfaz de línea de comandos para Mystik AI
# Uso: ./mystik-cli.sh chat "mensaje"
#      ./mystik-cli.sh voice "texto a decir"
#      ./mystik-cli.sh lead "nombre" "email"
#      ./mystik-cli.sh products
#      ./mystik-cli.sh context <key> [value]

MYSTIK_URL="${MYSTIK_URL:-http://127.0.0.1:5200}"
CMD="${1:-help}"

case "$CMD" in
  chat)
    MSG="${2:-Hola}"
    curl -s -X POST "$MYSTIK_URL/api/chat" \
      -H "Content-Type: application/json" \
      -d "{\"message\":\"$MSG\"}" | python3 -m json.tool
    ;;
  voice)
    TEXT="${2:-Hola, soy Mystik}"
    curl -s -o /tmp/mystik-cli.wav \
      "$MYSTIK_URL/api/voice/speak?text=$TEXT"
    echo "Audio guardado en /tmp/mystik-cli.wav"
    ;;
  lead)
    NAME="${2:-Cliente}"
    EMAIL="${3:-cliente@example.com}"
    curl -s -X POST "$MYSTIK_URL/api/leads" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$NAME\",\"email\":\"$EMAIL\"}" | python3 -m json.tool
    ;;
  products)
    curl -s "$MYSTIK_URL/api/products" | python3 -m json.tool
    ;;
  tenants)
    curl -s "$MYSTIK_URL/api/tenants" | python3 -m json.tool
    ;;
  context)
    KEY="${2:-}"
    VAL="${3:-}"
    if [ -n "$VAL" ]; then
      curl -s -X POST "$MYSTIK_URL/api/context" \
        -H "Content-Type: application/json" \
        -d "{\"key\":\"$KEY\",\"value\":$VAL}" | python3 -m json.tool
    elif [ -n "$KEY" ]; then
      curl -s "$MYSTIK_URL/api/context/$KEY" | python3 -m json.tool
    else
      curl -s "$MYSTIK_URL/api/context" | python3 -m json.tool
    fi
    ;;
  agent-bus)
    ACTION="${2:-status}"
    if [ "$ACTION" = "send" ]; then
      TARGET="${3:-all}"
      COMMAND="${4:-ping}"
      curl -s -X POST "$MYSTIK_URL/api/agent-bus/send" \
        -H "Content-Type: application/json" \
        -d "{\"target\":\"$TARGET\",\"command\":\"$COMMAND\"}" | python3 -m json.tool
    else
      curl -s "$MYSTIK_URL/api/agent-bus/status" | python3 -m json.tool
    fi
    ;;
  mcp)
    curl -s "http://127.0.0.1:18989/api/health" | python3 -m json.tool
    ;;
  help|*)
    echo "Mystik CLI — Asistente de ventas inteligente"
    echo ""
    echo "USO:"
    echo "  $0 chat \"mensaje\"              — Chatea con Mystik"
    echo "  $0 voice \"texto\"               — Genera audio TTS"
    echo "  $0 lead \"nombre\" \"email\"      — Crea un lead"
    echo "  $0 products                     — Catálogo de productos"
    echo "  $0 tenants                      — Lista tenants"
    echo "  $0 context [key] [val]          — Contexto compartido"
    echo "  $0 agent-bus [send target cmd]  — Bus de agentes"
    echo "  $0 mcp                          — Estado del MCP Gateway"
    echo ""
    echo "Variables de entorno:"
    echo "  MYSTIK_URL=${MYSTIK_URL}"
    echo ""
    ;;
esac

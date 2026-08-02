#!/bin/bash
# Launcher AstroTech — Inicia todos los servicios 24/7
# Uso: ./scripts/launch-all.sh [start|stop|restart|status]

set -e

BASE_DIR="/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp"
BOT_DIR="$BASE_DIR/tenants/Aztrotech/bot"
TTS_DIR="$BASE_DIR/tenants/Aztrotech"
LOG_DIR="/var/log/sdc"

export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
export NOTIF_BOT_TOKEN="${NOTIF_BOT_TOKEN:-}"
export NOTIF_OWNER_CHAT_ID="${NOTIF_OWNER_CHAT_ID:-5738935134}"

start() {
    echo "🚀 Iniciando servicios AstroTech..."

    # TTS Server
    if ! tmux has-session -t tts-aztrotech 2>/dev/null; then
        tmux new-session -d -s tts-aztrotech \
            "python3 '$TTS_DIR/tts-server.py' > '$LOG_DIR/aztrotech-tts.log' 2>&1"
        echo "  ✅ TTS server iniciado"
    else
        echo "  ⚠️  TTS server ya corriendo"
    fi

    # Main Bot
    if ! tmux has-session -t bot-cesar 2>/dev/null; then
        tmux new-session -d -s bot-cesar \
            "python3 '$BOT_DIR/main.py' > '$LOG_DIR/aztrotech-bot.log' 2>&1"
        echo "  ✅ Bot principal iniciado"
    else
        echo "  ⚠️  Bot principal ya corriendo"
    fi

    # Notification Bot
    if ! tmux has-session -t bot-notif 2>/dev/null; then
        tmux new-session -d -s bot-notif \
            "python3 '$BOT_DIR/notification_bot.py' > '$LOG_DIR/aztrotech-notif.log' 2>&1"
        echo "  ✅ Bot de notificaciones iniciado"
    else
        echo "  ⚠️  Bot de notificaciones ya corriendo"
    fi

    echo "🎉 Todos los servicios iniciados"
}

stop() {
    echo "🛑 Deteniendo servicios AstroTech..."
    tmux kill-session -t tts-aztrotech 2>/dev/null && echo "  ✅ TTS server detenido" || echo "  ⚠️  TTS server no estaba corriendo"
    tmux kill-session -t bot-cesar 2>/dev/null && echo "  ✅ Bot principal detenido" || echo "  ⚠️  Bot principal no estaba corriendo"
    tmux kill-session -t bot-notif 2>/dev/null && echo "  ✅ Bot de notificaciones detenido" || echo "  ⚠️  Bot de notificaciones no estaba corriendo"
    echo "🛑 Todos los servicios detenidos"
}

status() {
    echo "📊 Estado de servicios AstroTech:"
    for session in tts-aztrotech bot-cesar bot-notif; do
        if tmux has-session -t "$session" 2>/dev/null; then
            echo "  ✅ $session — corriendo"
        else
            echo "  ❌ $session — detenido"
        fi
    done
}

case "${1:-start}" in
    start)   start ;;
    stop)    stop ;;
    restart) stop; sleep 2; start ;;
    status)  status ;;
    *)       echo "Uso: $0 [start|stop|restart|status]"; exit 1 ;;
esac

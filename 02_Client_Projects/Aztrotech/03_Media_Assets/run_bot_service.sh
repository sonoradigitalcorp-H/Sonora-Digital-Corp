#!/bin/bash
# Multi-Tenant Bot Service — Run 24/7 locally until you have a VPS
# Usage: ./run_bot_service.sh start|stop|status

LOG_DIR="$HOME/.openclaw/logs"
PID_FILE="$HOME/.openclaw/multi-tenant-bot.pid"
WEBHOOK_PORT=5289
SCRIPT_DIR="$HOME/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects/Aztrotech/03_Media_Assets/webhooks"

mkdir -p "$LOG_DIR"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Service already running (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    echo "🚀 Starting Multi-Tenant Bot Service..."
    
    # Start webhook server directly
    cd "$SCRIPT_DIR" && nohup python3 multi_tenant_webhook.py > "$LOG_DIR/webhook.log" 2>&1 &
    
    sleep 2
    if kill -0 $! 2>/dev/null; then
        echo $! > "$PID_FILE"
        echo "✅ Service started on port $WEBHOOK_PORT"
        echo "   PID: $(cat $PID_FILE)"
        echo "   Logs: $LOG_DIR/webhook.log"
    else
        echo "❌ Failed to start. Check logs:"
        tail -10 "$LOG_DIR/webhook.log"
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Service not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    kill $PID 2>/dev/null && echo "✅ Service stopped" || echo "Process not found"
    rm -f "$PID_FILE"
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✅ Service running (PID: $(cat $PID_FILE))"
        echo "   Port: $WEBHOOK_PORT"
        echo "   Log: $LOG_DIR/webhook.log"
        curl -s http://localhost:$WEBHOOK_PORT/health 2>&1 || echo "   Not responding on health check"
    else
        echo "❌ Service not running"
        rm -f "$PID_FILE"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    status) status ;;
    restart) stop; sleep 2; start ;;
    *) echo "Usage: $0 {start|stop|status|restart}" ;;
esac
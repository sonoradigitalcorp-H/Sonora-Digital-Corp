#!/bin/bash
# Browser-Based Video Creator
# Opens Seedance/Kling in browser, automates prompt entry and download

set -euo pipefail

PLATFORM="${1:-seedance}"
PROMPT="${2:-Epic cinematic coming soon video for Sonora Digital Corp}"
OUTPUT_DIR="/home/mystic/sonora-digital-corp/webui/static/videos"

mkdir -p "$OUTPUT_DIR"

case "$PLATFORM" in
    seedance)
        echo "🎬 Abriendo Seedance..."
        google-chrome "https://www.seedance.ai" --new-window 2>/dev/null &
        sleep 5
        # Type the prompt (requires browser focus)
        xdotool type "$PROMPT"
        sleep 1
        xdotool key Return
        echo "   ✅ Prompt enviado a Seedance"
        ;;
    kling)
        echo "🎬 Abriendo Kling..."
        google-chrome "https://www.klingai.com" --new-window 2>/dev/null &
        sleep 5
        xdotool type "$PROMPT"
        sleep 1
        xdotool key Return
        echo "   ✅ Prompt enviado a Kling"
        ;;
    runway)
        echo "🎬 Abriendo Runway..."
        google-chrome "https://app.runwayml.com" --new-window 2>/dev/null &
        echo "   ✅ Runway abierto (requiere login manual)"
        ;;
esac

echo "📥 Cuando el video esté listo, descárgalo a: $OUTPUT_DIR"

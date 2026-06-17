#!/bin/bash
# Wrapper for Aider — AI pair programming on JARVIS codebase
# Usage: ./aider-session.sh [files...]
# Reads OPENROUTER_API_KEY from .env

set -euo pipefail

cd /home/mystic/jarvis
source .env 2>/dev/null || true

export OPENROUTER_API_KEY
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

aider --model openrouter/deepseek/deepseek-v4-flash \
      --auto-commits \
      --yes \
      "$@"

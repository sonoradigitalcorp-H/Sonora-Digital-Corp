#!/usr/bin/env bash
set -euo pipefail

AGE_KEY="${AGE_KEY:-$HOME/.age/key.txt}"

# Works both sourced (. scripts/decrypt-env.sh) and called directly
if [ -n "${BASH_SOURCE[0]:-}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
else
  SCRIPT_DIR="$(pwd)"
fi

decrypt_and_source() {
  local encrypted="$1"
  if [ ! -f "$encrypted" ]; then
    echo "[decrypt-env] WARN: $encrypted not found" >&2
    return
  fi
  local decrypted
  decrypted="$(age -d -i "$AGE_KEY" "$encrypted" 2>/dev/null)" || {
    echo "[decrypt-env] ERROR: failed to decrypt $encrypted" >&2
    return
  }
  eval "$decrypted"
}

decrypt_and_source "$SCRIPT_DIR/.env.age"

if [ -f "$SCRIPT_DIR/config/.secrets/clients.json.age" ]; then
  export CLIENTS_JSON
  CLIENTS_JSON="$(age -d -i "$AGE_KEY" "$SCRIPT_DIR/config/.secrets/clients.json.age")"
fi

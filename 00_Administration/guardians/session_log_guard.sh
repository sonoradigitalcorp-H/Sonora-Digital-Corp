#!/usr/bin/env bash
# Guardián de Memoria Histórica - Sonora Digital Corp
# Ley: Session_Logs/ es INMUTABLE. Solo se appenda, nunca se reescribe.
# Uso: bash 00_Administration/guardians/session_log_guard.sh [--staged]
cd "$(dirname "$0")/../.." || exit 1

LOGS="00_Administration/Session_Logs"
fail=0

if [ "$1" = "--staged" ]; then
  # Modo pre-commit: bloquea reescrituras de archivos EXISTENTES en Session_Logs
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    echo "🚫 [GUARDIÁN] Reescritura de memoria histórica: $f"
    fail=1
  done < <(git diff --cached --name-status | awk '$1=="M" && $2 ~ /^00_Administration\/Session_Logs\// {print $2}')
else
  # Modo auditoría: reporta archivos del working tree modificados vs HEAD
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "⚠️ No es repo git; solo registro la regla."
  else
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      echo "⚠️ Memoria modificada en working tree: $f"
      fail=1
    done < <(git diff --name-only | grep "^$LOGS/" || true)
    [ $fail -eq 0 ] && echo "✅ Memoria histórica intacta (nada reescrito)"
  fi
  [ -d "$LOGS" ] || echo "ℹ️ Session_Logs aún no existe (se creará en primer uso)"
fi

exit $fail

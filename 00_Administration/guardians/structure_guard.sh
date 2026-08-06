#!/usr/bin/env bash
# Guardián de Esqueleto - Sonora Digital Corp
cd "$(dirname "$0")/../.." || exit 1
fail=0
for bad in 00_Admin 01_Core 02_Clientes 03_Sandbox; do
  [ -e "$bad" ] && { echo "🚫 Duplicado resucitado: $bad/"; fail=1; }
done
for f in *; do
  case "$f" in
    00_Administration|01_Core_Platform|02_Client_Projects|03_Sandbox_and_RnD|README.md|AGENTS_MANIFEST.md|SYSTEM_MANIFEST.md) ;;
    *) echo "🚫 Deriva en raíz: $f"; fail=1;;
  esac
done
for f in .git .github .githooks .gitignore; do
  [ -e "$f" ] || { echo "⚠️ Falta elemento vital: $f"; fail=1; }
done
for d in 00_Administration 01_Core_Platform 02_Client_Projects 03_Sandbox_and_RnD; do
  [ -d "$d" ] || { echo "🚫 Órgano ausente: $d/"; fail=1; }
done
[ $fail -eq 0 ] && echo "✅ ESQUELETO CANÓNICO INTACTO" || { echo "❌ DERIVAS DETECTADAS"; exit 1; }

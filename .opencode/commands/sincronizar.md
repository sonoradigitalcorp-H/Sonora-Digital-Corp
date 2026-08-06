---
description: Sincroniza todo el sistema: guarda estado en Engram, analiza cambios, self-improve
---
1. engram save "auto-estado-$(date +%Y%m%d-%H%M)" "$(git log --oneline -3) | $(cat ESTADO.md | head -5)" --type state
2. bash 00_Administration/guardians/structure_guard.sh
3. git status --short
4. echo "Self-improve: revisa ESTADO.md y .opencode/skills/mystic/ para mejoras"

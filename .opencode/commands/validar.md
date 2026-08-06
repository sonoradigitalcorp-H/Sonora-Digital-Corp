---
description: Validar código, estructura y seguridad antes de commitear
---
1. bash 00_Administration/guardians/structure_guard.sh
2. Tests: SDK_Python/tests + Evals OKF.
3. grep -rE "sk-or-|ghp_|TOKEN\s*=" en el diff (cero secretos).
4. git status limpio.
5. Reporte: ✅ OK o ❌ ROTO con fix exacto en 1 línea.

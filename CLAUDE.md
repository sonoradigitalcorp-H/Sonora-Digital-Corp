# CLAUDE.md — Protocolo de Operación

## Regla Absoluta #1: Directorio de Trabajo

Siempre debes ejecutarte DESDE `/home/mystic/sonora-digital-corp/`. Tu alias `sdc` ya hace eso.

Si no estás en ese directorio, el agente NO tendrá acceso a:
- `opencode.json` (agentes, comandos, constitution)
- `process/` (pipeline de SPECs)
- `sonora-enterprise-os/constitution/` (reglas, TRUTH, OMEGA-PROMPT)
- `.github/hooks/` (gates de git)

## Regla Absoluta #2: MEMORIA DE SESIONES ANTERIORES

Al INICIAR una sesión, debés leer automáticamente el resumen de la última sesión desde Engram:

```python
python3 -c "
import sys; sys.path.insert(0, '/home/mystic/sonora-digital-corp/apps/jarvis')
from src.core.engram import engram
results = engram.query_context('session summary', limit=3)
for r in results:
    print(f\"[{r['spec_id']}] {r['summary']}\")
"
```

Esto te da contexto de qué se hizo en la sesión anterior.

## Regla Absoluta #3: ESTRUCTURA

Leé `docs/MAPA-SDC.md` para entender la organización del repositorio:

```
~/sdc/
├── constitution/     Reglas, prompts, OMEGA-PROMPT
├── core/             apps/ + infra/ + scripts/
├── platforms/        Telegram, WhatsApp
├── products/         mystika, yami, etc.
├── clients/          abe-music, azrec
├── tests/            442 tests
├── memory/           state/ + process/ (SPECs)
└── docs/             MAPA, session summary, presentaciones
```

## Si detectas que NO estás en el directorio correcto:
1. Informa al usuario inmediatamente
2. No ejecutes ninguna acción hasta que el usuario cambie al directorio correcto
3. Sugiere: `cd ~/sdc && opencode`

## Archivo de configuración maestro:
`/home/mystic/sonora-digital-corp/opencode.json`

## Referencia rápida:
@AGENTS.md

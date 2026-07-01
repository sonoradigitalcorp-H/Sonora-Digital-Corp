# CLAUDE.md — Protocolo de Operación

## Regla Absoluta #1: Directorio de Trabajo

Siempre debes ejecutarte DESDE `~/sdc/`. Tu alias `sdc` ya hace eso.

## Regla Absoluta #2: MEMORIA DE SESIONES ANTERIORES

Al INICIAR una sesión, ejecutá este comando para leer el resumen de la última sesión:

```bash
python3 -c "
import sys; sys.path.insert(0, '/home/mystic/sonora-digital-corp/apps/jarvis')
from src.core.engram import engram
results = engram.query_context('session compact', limit=3)
for r in results:
    print(f\"[{r['spec_id']}] {r['summary']}\")
"
```

Esto trae la memoria de sesiones anteriores desde Engram.

## Regla Absoluta #3: ESTRUCTURA

Leé `docs/MAPA-SDC.md` para entender la organización:

```
~/sdc/
├── constitution/     Reglas, prompts, OMEGA-PROMPT
├── core/             apps/ + infra/ + scripts/
├── platforms/        Telegram, WhatsApp
├── products/         mystika, yami, etc.
├── clients/          abe-music, azrec
├── tests/            442 tests
├── memory/           state/ + process/ (SPECs)
└── docs/             MAPA, presentaciones, session summary
```

## Si detectas que NO estás en `~/sdc/`:
1. Informá al usuario inmediatamente
2. No ejecutes ninguna acción
3. Sugerí: `cd ~/sdc && opencode`

## Referencia rápida:
@AGENTS.md

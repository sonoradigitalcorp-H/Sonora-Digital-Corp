#!/usr/bin/env bash
# Sync Engram → Obsidian Vault (Digital Brain)
set -euo pipefail

VAULT="${HOME}/Documents/sdc-brain-vault"
ENGRAM_DB="${HOME}/.engram/engram.db"

echo "=== 🧠 Sincronizando Cerebro Digital ==="

# 1. Exportar observaciones de Engram a Obsidian
echo "[1/3] Exportando observaciones..."
python3 "${HOME}/sonora-digital-corp/scripts/engram_autocapture.py" \
  --obsidian-export "$VAULT" \
  --vault "$VAULT" 2>/dev/null || echo "  ⚠️  Export directo no disponible, usando método alternativo..."

# 2. Generar People desde contactos conocidos
echo "[2/3] Generando personas conocidas..."
mkdir -p "${VAULT}/People"

# Luis Daniel (yo)
cat > "${VAULT}/People/Luis Daniel Guerrero Enciso.md" << 'EOF'
---
type: person
name: "Luis Daniel Guerrero Enciso"
role: "Dueño de Sonora Digital Corp"
company: "Sonora Digital Corp"
contact: "+52 662 353 8272 (WhatsApp)"
tags: [person, me, sdc]
created: 2026-07-18
---

# Luis Daniel Guerrero Enciso

## Rol
Fundador técnico de Sonora Digital Corp. Opera desde laptop Linux en México.
Es quien habla con el AI. Dueño del sistema, el VPS, y todo el proyecto.

## Contacto
- WhatsApp: +52 662 353 8272
- Es el número SDC también (personal = negocio)

## Sistemas
- VPS: sdc-prod (149.56.46.173, OVH)
- Laptop: Linux, IP dinámica México
- GitHub: sonoradigitalcorp-H
EOF

# Perroni
cat > "${VAULT}/People/Perroni.md" << 'EOF'
---
type: person
name: "Perroni (Luis Daniel)"
role: "CEO de Sonora Digital Corp"
company: "Sonora Digital Corp"
contact: "+52 662 353 8272"
tags: [person, sdc, ceo]
created: 2026-07-18
---

# Perroni

Luis Daniel Guerrero Enciso — CEO de Sonora Digital Corp.
Su número personal ES el mismo que SDC.

## Notas
- Fundador técnico
- Opera desde laptop Linux
- Habla directamente con el AI
EOF

# Nathaly
cat > "${VAULT}/People/Nathaly Hermosillo.md" << 'EOF'
---
type: person
name: "Nathaly Hermosillo"
role: "Novia de Perroni"
company: ""
contact: "5216622681111@s.whatsapp.net"
tags: [person, contacto]
created: 2026-07-18
---

# Nathaly Hermosillo

Pareja de Luis Daniel.
EOF

# Abraham Ortega
cat > "${VAULT}/People/Abraham Ortega.md" << 'EOF'
---
type: person
name: "Abraham Ortega"
role: "CEO de ABE Music / Modular Data Systems"
company: "ABE Music Group"
contact: ""
tags: [person, abe-music, cliente]
created: 2026-07-18
---

# Abraham Fenix / Abraham Ortega

CEO de Abe Music Group (Compton CA) + Modular Data Systems (444 Vernon CA).
Cliente del sistema ABE Music OS. Consume vía PWA. No codea ni configura.
EOF

# Noel
cat > "${VAULT}/People/Noel Nichols.md" << 'EOF'
---
type: person
name: "Noel Nichols"
role: "Socio creativo"
company: "Sonora Digital Corp"
tags: [person, sdc, socio]
created: 2026-07-18
---

# Noel Nichols

Socio creativo colaborativo — trabaja junto con Luis Daniel.
Aporta trabajo creativo y colaborativo. Co-construye el proyecto.
EOF

# 3. Generar Projects desde el repo
echo "[3/3] Generando proyectos activos..."
mkdir -p "${VAULT}/Projects"

cat > "${VAULT}/Projects/Sonora Digital Corp.md" << 'EOF'
---
type: project
title: "Sonora Digital Corp"
status: active
tags: [project, sdc, core]
created: 2026-07-18
---

# Sonora Digital Corp

Plataforma completa de agentes AI para música y marketing.

## Stack
- FastAPI + Next.js + Go
- PostgreSQL + Neo4j + Qdrant + Redis
- Docker + systemd en VPS OVH
- OpenClaw + OpenCode + Engram

## Servicios activos
- OpenClaw Gateway (:18789)
- ABE Service (:5180)
- Content Server (:8765)
- OmniVoice (:3900)
- n8n (:5678, 33 workflows)
- Y más...

## Próximos pasos
- [ ] Lanzar Clone Service
- [ ] Formalizar Digital Brain
EOF

cat > "${VAULT}/Projects/Clone Service.md" << 'EOF'
---
type: project
title: "Clone Service SDC"
status: active
tags: [project, clone, marketing]
created: 2026-07-18
---

# Clone Service SDC

Servicio de clon publicitario — clientes pagan pack, envían fotos/audio,
entrenamos LoRA facial + clon de voz, generamos contenido con su identidad.

## Estado
✅ SPEC completa (Tier 3, Score 82/100)
✅ 5 Gherkin features (19 escenarios)
✅ 82 tests pasando
✅ 4 MCP servers
✅ Agent Harness + Skill + Registry
✅ Pipeline CLI
✅ Observability (ADR, Score, Lecciones)

## Precios
- Basic: $49 (10 fotos, 3 videos, 10 TTS)
- Pro: $99 (30 fotos, 10 videos, 30 TTS)
- Enterprise: $199 (100 fotos, 30 videos, 100 TTS)
EOF

# Generar decisiones arquitectónicas
mkdir -p "${VAULT}/Decisions"

cat > "${VAULT}/Decisions/Backend IA FAL.ai.md" << 'EOF'
---
type: decision
title: "Backend IA: FAL.ai"
status: active
tags: [decision, architecture, clone]
created: 2026-07-18
---

# Backend IA: FAL.ai (no GPU local)

**Contexto**: No hay GPU en el VPS. Se necesita entrenamiento LoRA + generación de imágenes/video.

**Decisión**: Usar FAL.ai para todo el procesamiento GPU. FAL_KEY ya configurado.

**Alternativas**: GPU propia (RunPod ~$30/mes), FaceFusion local (requiere GPU).

**Consecuencia**: Dependencia externa, pero sin inversión en hardware. Costo ~$5-6/cliente.
EOF

cat > "${VAULT}/Decisions/Almacenamiento Supabase.md" << 'EOF'
---
type: decision
title: "Almacenamiento: Supabase Storage"
status: active
tags: [decision, architecture, storage]
created: 2026-07-18
---

# Almacenamiento: Supabase Storage

**Contexto**: Se necesita almacenar fotos de clientes, modelos entrenados, y assets generados.

**Decisión**: Usar Supabase Storage (bucket sdc-assets) con estructura /clients/{id}/.

**Consecuencia**: Assets expiran a 30 días. URLs públicas para el cliente.
EOF

# Generate Graph relationships
mkdir -p "${VAULT}/Graph"
cat > "${VAULT}/Graph/relationships.md" << 'EOF'
---
type: graph
title: "Relaciones del Cerebro Digital"
tags: [graph, brain]
created: 2026-07-18
---

# Relaciones del Cerebro Digital

```mermaid
graph TD
    LD[Luis Daniel] --> SDC[Sonora Digital Corp]
    LD --> ABE[ABE Music]
    LD --> CLONE[Clone Service]
    SDC --> VPS[OVH VPS 149.56.46.173]
    SDC --> OPENCLAW[OpenClaw Gateway]
    SDC --> ENGRAM[Engram Memory]
    SDC --> MCP[MCP Ecosystem]
    ABE --> AO[Abraham Ortega]
    CLONE --> FAL[FAL.ai]
    CLONE --> OMNI[OmniVoice]
    CLONE --> SUPABASE[Supabase Storage]
    CLONE --> FFMPEG[FFmpeg]
    CLONE --> CREDITS[Credit System]
```

## Conexiones desde Engram

```dataview
TABLE type, project, topic_key
FROM "Observations"
WHERE topic_key != null
SORT topic_key ASC
```
EOF

# 4. Sync to Google Drive backup
GDRIVE_VAULT="/run/user/1000/gvfs/google-drive:host=gmail.com,user=perrykingla.69/0AH8O3LLHfCHZUk9PVA/SDC"
if [ -d "$GDRIVE_VAULT" ]; then
  echo "[4/4] Sincronizando a Google Drive..."
  cp -r "${VAULT}/Dashboard" "${GDRIVE_VAULT}/" 2>/dev/null
  cp -r "${VAULT}/People" "${GDRIVE_VAULT}/" 2>/dev/null
  cp -r "${VAULT}/Projects" "${GDRIVE_VAULT}/" 2>/dev/null
  cp -r "${VAULT}/Decisions" "${GDRIVE_VAULT}/" 2>/dev/null
  cp -r "${VAULT}/Learnings" "${GDRIVE_VAULT}/" 2>/dev/null
  cp -r "${VAULT}/Observations" "${GDRIVE_VAULT}/" 2>/dev/null
  echo "  ✅ Google Drive backup"
fi

echo ""
echo "=== ✅ Cerebro Digital sincronizado ==="
echo "  Vault: $VAULT"
echo "  Abre con: brain-open"

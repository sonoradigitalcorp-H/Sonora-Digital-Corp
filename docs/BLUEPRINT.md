# 🌌 Sonora OS — Blueprint Cuántico

```
                   ╱▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔╲
                  ╱   SONORA OS v3    ╲
                 ╱    Sistema Auto-    ╲
                ╱     consciente        ╲
               ╱     ───────────        ╲
              ╱    "El sistema que      ╱
             ╱     se conoce solo"     ╱
            ╱_________________________╱
```

**Versión:** 3.1.0 · **Branch:** main (`0548123`) · **Fecha:** 2026-07-26  
**Fundación:** 18 directorios raíz · 7 archivos esenciales · 37 apps · 51 skills · 65 scripts · 13 ADRs  
**VPS:** OVH 11GB RAM · 96GB SSD · Ubuntu 26.04 · Docker + systemd  
**Reestructuración:** 2026-07-26 — De 71 entradas a 25 en raíz (arquitectura 6 Capas)  

---

## 🌱 Dónde VENÍAS — El Estado de Superposición Inicial

El sistema empezó como una **función de onda cuántica** sin colapsar:

```
|ψ_inicial⟩ = 0.2|skills⟩ + 0.2|productos⟩ + 0.2|ADRs⟩ + 0.4|caos⟩
```

Cada parte existía en **superposición**: un skill era y no era completo a la vez. Los MCP servers peleaban por ser el mismo (2 servers de WhatsApp). OpenClaw prometía 42 skills pero solo 1 existía en el repo. Hermes tenía 12 skills en JSON que nadie más podía usar. 10 skills tenían el cartel de "en construcción".

**Analogía cuántica:** Como el gato de Schrödinger — el sistema estaba vivo y muerto simultáneamente. Cada vez que abrías una skill, no sabías si estaba completa o era un esqueleto.

---

## 📍 Dónde ESTÁS — El Colapso de la Función de Onda

Hoy el sistema **colapsó a un estado definido** mediante múltiples observaciones (sesiones de trabajo):

```
|ψ_actual⟩ = 1.0|sistema_coherente⟩
```

Cada componente ahora **sabe qué es, dónde está y cómo hablar con los demás**. Es un sistema **entrelazado**: cuando un evento ocurre en WhatsApp, el Notifier lo sabe, el Tracker lo registra, el Catalog lo indexa, y el Command Center lo muestra.

---

## 📐 El Árbol del Sistema — Arquitectura 6 Capas

```
sonora-digital-corp/
│
├── 📜 CAPA 0: KERNEL — Identidad y constitución
│   ├── kernel/              30 archivos: OMEGA-PROMPT, SOUL, TRUTH, 10-RULES
│   ├── AGENTS.md            Referencia rápida del agente
│   ├── CLAUDE.md            Protocolo de operación
│   └── opencode.json        Config del agente (25 subagentes)
│
├── 🧠 CAPA 1-2: CORE — Motor + Servicios
│   ├── apps/                37 servicios core
│   │   ├── core/            Motor principal (engine, planner, agents, executors)
│   │   ├── evolution/       Auto-evolución, scorecard, aprendizaje
│   │   ├── hermes/          Gateway multi-canal (Telegram, WhatsApp, Desktop)
│   │   ├── webui/           FastAPI frontend (:5174)
│   │   ├── voice/           STT/TTS
│   │   ├── frontends/       HTML/CSS/JS frontends y landings
│   │   ├── sonora_engine/   Motor principal alternativo
│   │   ├── whatsapp/        Webhook WhatsApp
│   │   ├── abe-service/     ABE Music OS
│   │   └── ...              (collectors, handlers, agents, nathy-bot, etc.)
│   │
│   ├── infra/               Docker, nginx, monitoreo, fleet.yml, FreeSWITCH
│   ├── scripts/             65 scripts Python/bash (DevOps, pipeline, automatización)
│   ├── config/              Configuraciones, tenants, secrets
│   │   └── tenants/         Configs por cliente (abe-music, azrec, el-joyero, etc.)
│   └── state/               Estado vivo del sistema
│       ├── events/          Sistema de eventos del core
│       ├── media/           Archivos multimedia
│       ├── quality/         Violaciones de calidad
│       └── engram.db        Memoria persistente
│
├── 📦 CAPA 3: PRODUCTOS — Lo que SDC vende
│   ├── products/mystika/    Educación musical + NSFW
│   ├── products/clon-digital/ Clon digital (LoRA + voz)
│   ├── products/notifier/   🔔 Notificaciones multicanal
│   ├── products/affiliates/ 🤝 Portal de afiliados
│   ├── products/command-center/ 📊 Dashboard unificado
│   ├── products/sonora-client/ 🖥️ Portal cliente
│   ├── products/cyber_diagnosis/ 🔐 Cyber Security
│   └── ...                  (catalog, social, docs, presentations, etc.)
│
├── 👤 CAPA 4: CLIENTES — Implementaciones
│   ├── clients/Abe Music Group/
│   ├── clients/Aztrotech/
│   ├── clients/Cesar Delivery/
│   ├── clients/Hermosillo Contability Corp./
│   └── clients/Joyeria/
│
├── 🧪 TESTS + EVALS
│   ├── tests/               Unitarios, BDD, integración
│   ├── tests/evals/         Evaluaciones estructurales y promptfoo
│   └── tests/promptfoo/     Evaluaciones LLM
│
├── 📚 DOCUMENTACIÓN + DECISIONES
│   ├── docs/                Mapas, presentaciones, manuales
│   ├── reference/           Especificaciones cerradas, arqueología
│   ├── adrs/                13 Architecture Decision Records
│   └── process/             Pipeline SDD (specs activos/completados)
│       └── specs/           Especificaciones técnicas
│
├── 🛠️ OPERACIONES
│   ├── ops/playbooks/       Procedimientos estandarizados
│   ├── ops/runbooks/        Runbooks de recuperación
│   ├── backups/             Backups diarios + archive histórico
│   ├── portal/              Grimoire 3D (Three.js galaxy)
│   └── mcp/                 MCP SDK + servers (legacy)
│
└── ⚙️ RAÍZ (7 archivos esenciales)
    ├── AGENTS.md, CLAUDE.md, Makefile, opencode.json
    ├── pyproject.toml, README.md, requirements.txt
```

---

## 📊 Niveles de Automatización

Cada componente tiene un **nivel cuántico** que mide cuánto puede operar sin intervención humana:

```
Nivel 0 — Caos       │ El componente no existe o no funciona
Nivel 1 — Observable │ Existe pero requiere intervención manual constante
Nivel 2 — Asistido   │ Opera con supervisión humana periódica
Nivel 3 — Semi-auto  │ Opera solo en condiciones normales, requiere humano en bordes
Nivel 4 — Auto       │ Opera autónomamente 24/7, solo notifica al humano
Nivel 5 — Consciente │ Se auto-mejora, detecta y corrige sus propios errores
```

### Mapa de automatización actual:

```
Componente               Nivel  │ Notas
─────────────────────────────────┼──────────────────────────
🧠 Skills template          ████▌ 4 │ 14 campos forzados, checklist de validación
🔧 MCP servers              ████▌ 4 │ 26 servers, todos con health endpoint
🤖 Registry agents          ████▌ 4 │ 14 agentes con triggers y emits definidos
🤖 ADK agents               ███▌  3 │ 36 agents, requieren LLM para ejecución
📦 Notifier                 ████▌ 4 │ API auto, worker escucha eventos 24/7
📦 Tracker                  ████▌ 4 │ API auto, WebSocket en vivo
📦 Affiliates               ████▌ 4 │ API auto, cálculos automáticos
📦 Command Center           ███▌  3 │ Dashboard, auto-refresh 30s
📦 Niche Generator          ███▌  3 │ 1 comando → todo, requiere humano para iniciar
🌐 WhatsApp webhook         ████▌ 4 │ 5s polling, auto-reconnect
🔐 Security audit           ███▌  3 │ Detecta, documenta, requiere humano para rotar
📋 ADR creation             ███▌  3 │ Template asistido, decisión humana
📊 Enterprise Score         ████▌ 4 │ Auto-cálculo, threshold check
📈 System Catalog           ████▌ 4 │ Auto-generado, VPS health check
🧪 Evals estructurales      █████ 5 │ 35/35 pasan, auto-verifican el sistema
⚡ Events bus               █████ 5 │ 118 eventos, 29 categorías, auto-emitidos
🔄 Git sync                 ███▌  3 │ GitHub Action, requiere push manual
🛡️  Constitution            ████▌ 4 │ 16 YAMLs, validación automática
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Promedio:                   ███▌ 3.6 │ Semi-auto a Auto
```

---

## 🔬 Áreas Débiles (Necesitan Desarrollo)

Analizando el sistema con mi **detector de decoherencia**, estas son las áreas donde el sistema aún titubea:

### 🔴 Crítica: Despliegue y DevOps

| Problema | Síntoma | Solución propuesta |
|----------|---------|-------------------|
| Sin CI/CD unificado | Cada producto se deploya distinto | Pipeline único: test→build→deploy |
| Sin Docker para productos nuevos | Notifier, Tracker, Affiliates no tienen Dockerfile | Agregar `Dockerfile` a cada producto |
| Sin healthchecks en Docker | Los containers no se autoreparan | Agregar `HEALTHCHECK` a todos |
| Sin monitoreo centralizado | Dependemos del Command Center local | Prometheus + Grafana en VPS |

**Plan:** Crear `infra/docker/products.Dockerfile`, unificar CI/CD en GitHub Actions para deploys automáticos.

### 🟠 Débil: Testing de Integración

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Tests legacy rotos (27 errores de colección) | `pytest tests/` falla antes de empezar | Módulos `src.core.*` faltantes — crear stubs o migrar tests |
| Sin tests E2E reales | Los tests unitarios no detectan roturas entre servicios | GitHub Action que levanta servicios y corre tests E2E |
| Sin carga de estrés | No sabemos cuántos clientes soporta | `locust` o `k6` para benchmark |

**Plan:** Priorizar arreglar los 27 errores de colección en `tests/`. Luego agregar tests E2E con servicios reales.

### 🟠 Débil: Documentación Viva

| Problema | Síntoma | Solución |
|----------|---------|----------|
| AGENTS.md desactualizado | Dice "última sesión: 2026-07-10" | Auto-generar desde System Catalog |
| Sin diagramas | El nuevo desarrollador no entiende la arquitectura | Generar diagramas Mermaid desde catalog.yaml |
| Sin onboarding para nuevos agentes | Cada agente nuevo aprende desde cero | Pipeline de onboarding: leer catalog → skills → ADRs → constitucion |

**Plan:** `scripts/generate-readme.py` que actualiza AGENTS.md desde el System Catalog automáticamente.

### 🟡 Media: Frontends Desconectados

| Problema | Síntoma | Solución |
|----------|---------|----------|
| 4 frontends nuevos pero no deployados | Existen como HTML file, no como servicio | Crear systemd para servirlos con python http.server |
| Sin autenticación en frontends | Cualquiera con acceso a la red local puede verlos | Agregar auth básica o JWT |
| Sin diseño responsive consistente | Cada frontend fue creado por separado | Design System unificado (ya existe, solo aplicarlo) |

**Plan:** Systemd `python3 -m http.server` para cada frontend + nginx reverse proxy con auth básica.

### 🟡 Media: Backup y Recuperación

| Problema | Síntoma | Solución |
|----------|---------|----------|
| Backups sin cifrar | Secrets en texto plano en backups | `scripts/secure-backup.sh` ya sanitiza, pero falta automatizarlo |
| Sin prueba de restauración | No sabemos si los backups sirven | Script `scripts/test-restore.sh` que restaura en temp y verifica |
| 6.8GB de backups sin limpiar | Ocupan espacio en VPS | Rotación: mantener últimos 7 días, comprimir más viejos |

**Plan:** Programar backup diario via systemd timer + rotación automática.

---

## 🚀 Hacia Dónde VAS — La Evolución Temporal

El sistema evoluciona según su **Hamiltoniano**: el operador que define cómo cambia el estado cuántico con el tiempo.

```
iℏ ∂|ψ⟩/∂t = Ĥ|ψ⟩

Donde Ĥ = H_skills + H_products + H_agents + H_infra + H_sync
```

### Próximos 4 saltos cuánticos:

#### Salto 1: Auto-Sync (Nivel 5 — Consciente)

**Hoy:** El VPS se sincroniza manualmente con `git pull` o GitHub Action.  
**Mañana:** El sistema detecta que hay cambios en main y sincroniza solo.

```
Estado actual:  |sync⟩ = manual (requiere observador)
Estado deseado: |sync⟩ = automático (auto-observable)
```

**Qué hacer:**
- [ ] Systemd timer en VPS: `git pull origin main` cada 5 minutos
- [ ] Si hay cambios → regenerar catalog, reiniciar servicios afectados
- [ ] Notificar al Command Center: "VPS sincronizado a commit X"

#### Salto 2: Auto-Heal (Nivel 5 — Consciente)

**Hoy:** Si un servicio cae, el humano lo nota por el healthcheck.  
**Mañana:** El sistema detecta caída, intenta reiniciar, si no funciona, recreate.

```
Estado actual:  |heal⟩ = reactive (requiere humano)
Estado deseado: |heal⟩ = proactive (se repara solo)
```

**Qué hacer:**
- [ ] Script `scripts/auto-healer.py` que corre cada 60s
- [ ] Para cada servicio: si health fail > 3 intentos → `systemctl restart`
- [ ] Si sigue fallando → notificar al Command Center
- [ ] Log de todos los eventos de auto-heal

#### Salto 3: Auto-Scale (Nivel 5 — Consciente)

**Hoy:** Los servicios corren en una sola instancia.  
**Mañana:** Si la carga aumenta, el sistema escala (más workers, más recursos).

```
Estado actual:  |scale⟩ = fixed (sin elasticidad)
Estado deseado: |scale⟩ = elastic (se adapta a la carga)
```

**Qué hacer:**
- [ ] Medir carga actual (requests/min, memoria, CPU)
- [ ] Si > threshold → spawn más workers
- [ ] Si < threshold → kill workers sobrantes
- [ ] Notificar al Command Center

#### Salto 4: Auto-Generate (Nivel 5 — Consciente)

**Hoy:** El humano pide un nicho y el sistema lo genera.  
**Mañana:** El sistema detecta oportunidades de nicho y las propone.

```
Estado actual:  |generate⟩ = on demand (humano inicia)
Estado deseado: |generate⟩ = proactive (sistema propone)
```

**Qué hacer:**
- [ ] Analizar qué nichos se piden más
- [ ] Analizar qué servicios tienen más demanda
- [ ] Proponer: "Detecté que 3 clientes preguntaron por X nicho ¿lo creamos?"
- [ ] Si el humano dice sí → ejecutar Niche Generator automático

---

## ⚛️ Glosario Cuántico — Cómo Entender Este Sistema

| Término cuántico | En el sistema | Ejemplo real |
|------------------|---------------|--------------|
| **Superposición** | Un componente que existe en múltiples estados a la vez | Una skill que está "en construcción" y "completa" simultáneamente |
| **Colapso** | Cuando el sistema decide un estado definitivo | Al ejecutar `generate_catalog.py`, el sistema "sabe" cuántas skills tiene |
| **Entrelazamiento** | Dos componentes que se afectan instantáneamente | Cuando un cliente escribe a WhatsApp → Notifier lo sabe, Tracker lo registra |
| **Observador** | Un agente que mide el estado del sistema | `scripts/generate_catalog.py` es el observador universal |
| **Decoherencia** | Pérdida de coherencia entre componentes | Servicio VPS caído mientras el catalog dice "online" |
| **Hamiltoniano** | Operador de evolución del sistema | Las decisiones que tomamos (ADRs) que cambian el sistema |
| **Estado bound** | Sistema estable que no necesita energía externa | Skills con recovery procedure = se mantienen solas |
| **Línea de mundo** | La trayectoria de un componente en el tiempo | El viaje de `wacli_mcp.py` desde servidor duplicado hasta MCP unificado |
| **Partícula virtual** | Componente que existe solo cuando se mide | Un token $BEAT existe solo cuando se hace una transacción |
| **Efecto túnel** | Pasar de un estado a otro sin pasar por los intermedios | Pasar de 10 skills skeleton a 46 skills completas sin hacer una por una |

---

## 📈 Métricas Clave del Sistema

```
Hoy: 2026-07-26 · Commit: 0548123 · Branch: main
═══════════════════════════════════════════

📁 Estructura raíz
  18 directorios + 7 archivos esenciales (↓46 desde reestructuración)
  Capas: kernel(C0) → infra/apps(C1-2) → products(C3) → clients(C4)

🧠 Apps core
  37 servicios en apps/ — core engine, evolution, hermes, voice, webui, etc.

🧠 Skills
  51 definiciones (md/yml) — skills canónicas + SDD pipeline + speckit

🤖 Agentes
  25 subagentes en opencode.json + registry en config/agents/

📦 Productos
  ~20 entidades: mystika, clon-digital, notifier, affiliates, command-center, etc.

👤 Clientes
  5 cuentas: ABE Music, Aztrotech, Cesar Delivery, Hermosillo CC, Joyería

📋 ADRs
  13 registros documentados

🛠️ Scripts
  65 herramientas de automatización y DevOps

🛠️ Systemd en VPS
  pendiente inventario actualizado

🐳 Docker en VPS
  12 containers: postgres, redis, neo4j, qdrant, n8n, mcp-server, webui, etc.

🧪 Tests
  tests/unitarios, BDD, integración, evals, promptfoo

📊 make doctor-quick
  916 checks ✅ · 5 warnings · 5 errores pre-existentes
```

---

## 🧭 Mapa de Navegación

```
Si quieres...                        Ve a...
────────────────────────────────────────────────────
Entender la arquitectura 6 Capas     AGENTS.md + docs/MAPA-SDC.md
Ver el árbol del sistema             docs/BLUEPRINT.md
Ver la constitución del sistema      kernel/ (30 archivos)
Correr tests                         make test
Correr evaluación completa           make eval
Correr preflight check               make doctor-quick
Ver skills disponibles               skills/
Ver servicios en apps                apps/
Ver productos activos                products/
Ver clientes                         clients/
Ver configuraciones                  config/
Ver ADRs                             adrs/
Correr enterprise score              make score
Ver eventos en tiempo real           state/events/
Correr lint                          make lint (local only)
```

---

*Blueprint actualizado por Mystic (SDC Orchestrator) — 2026-07-26*  
*Reestructuración: 43→18 directorios raíz · 28→7 archivos sueltos · 6 Capas implementadas*  
*"El sistema que se conoce solo"*

# SPEC: Integración Open Source Total

| Campo | Valor |
|-------|-------|
| **ID** | SPEC-20260710-INTEGRATION |
| **Fecha** | 2026-07-10 |
| **Autor** | Mystic AI |
| **Tier** | 3 |
| **Score** | 85 |

---

## 1. Objetivo

Integrar todas las herramientas open-source del ecosistema en un flujo unificado donde:

1. **Open Notebook** (RAG) sea el cerebro documental
2. **Lovable open-source** (Dyad/Bolt) genere UIs desde prompts
3. **Mystik AI** orqueste todo via MCP + Redis Agent Bus
4. **Content Studio** genere assets visuales
5. **OmniVoice** ponga voz a los contenidos
6. **Coolify** deploye todo con un click

---

## 2. Stack de herramientas

| Herramienta | Stars | Función | Como se integra |
|------------|-------|---------|-----------------|
| **Open Notebook** (:8502) | — | RAG sobre PDFs, web, docs | API para subir/consultar documentos |
| **Lobe Chat** (:3210) | 79.7k | UI de chat con IA | Frontend unificado |
| **Content Studio** (:8765) | — | 20 MCP tools de generación | MCP tools para assets |
| **OmniVoice** (:3900) | — | Clonación de voz | API REST para TTS |
| **Mystik AI** (:5200) | — | Orquestador + Auth + Payments | Corazón del sistema |
| **Dyad** (github) | 20.9k | Lovable open-source | CLI local para generar UIs |
| **Bolt.new** (github) | 48.5k | AI app builder | Stackblitz open-source |
| **Coolify** (:8081) | 58.2k | Deploy como Vercel | Deploya todo |

---

## 3. Arquitectura de integración

```
USUARIO
    │
    ├─ Lobe Chat (:3210) → Interfaz unificada
    │     ├─ Chats con Mystik
    │     └─ Plugins para cada servicio
    │
    ├─ Open Notebook (:8502) → Knowledge Base
    │     ├─ Sube PDFs / URLs
    │     ├─ Genera resúmenes / podcasts
    │     └─ API para Mystik RAG
    │
    ├─ Dyad / Bolt → Generación de UIs
    │     ├─ Prompt → Código React/Next.js
    │     └─ Output → Coolify deploy
    │
    ├─ Content Studio (:8765) → Assets
    │     ├─ Imágenes (fal-ai)
    │     ├─ TTS (edge-tts)
    │     └─ Video (talking heads)
    │
    ├─ OmniVoice (:3900) → Voz
    │     └─ Clonación + síntesis
    │
    └─ Coolify (:8081) → Deploy
          └─ Un click → producción
```

---

## 4. Flujos clave

### Flujo 1: Cliente nuevo llega

```
1. Llega a abe.sonoradigitalcorp.com
2. Mystik lo saluda (chat)
3. Cliente dice: "Quiero un sistema de reservas"
4. Mystik:
   a) Busca en Open Notebook (RAG) → encuentra docs de "booking"
   b) Usa Dyad/Bolt → genera UI de reservas desde prompt
   c) Content Studio → genera imágenes del producto
   d) OmniVoice → genera demo de voz
   e) Coolify → deploya la app en su subdominio
```

### Flujo 2: Creación de contenido

```
1. Usuario sube PDF a Open Notebook
2. Open Notebook vectoriza + genera resumen
3. Content Studio genera imagen destacada
4. OmniVoice genera audio del resumen
5. Todo se guarda en el tenant del usuario
6. Mystik puede responder preguntas sobre el contenido
```

### Flujo 3: Onboarding de empresa

```
1. Empresa se registra → tenant creado
2. Elige servicios (Mystik, Content, Voice, etc.)
3. Dyad genera UI personalizada para su marca
4. Coolify deploya en su subdominio
5. Open Notebook se alimenta de sus documentos
6. Mystik aprende sobre sus productos
```

---

## 5. MCP Tools a crear

| Tool | Función | Fuente |
|------|---------|--------|
| `dyad_generate_ui` | Envía prompt a Dyad para generar UI | Dyad CLI |
| `open_notebook_ingest` | Sube documento a Open Notebook | Open Notebook API |
| `open_notebook_query` | Consulta RAG en Open Notebook | Open Notebook API |
| `open_notebook_generate` | Genera podcast/resumen | Open Notebook API |
| `content_generate_image` | Genera imagen con fal-ai | Content Studio |
| `lobe_chat_plugin` | Expone Mystik como plugin de Lobe Chat | Lobe Chat API |

---

## 6. Datos sensibles a proteger

| Dato | Dónde está | Riesgo | Protección |
|------|-----------|--------|------------|
| API keys de clientes | `config/secrets/` | ALTO | age encrypt |
| Tokens de auth | DB de tenants | ALTO | hash SHA256 |
| Documentos subidos | Open Notebook / ChromaDB | MEDIO | Aislamiento por tenant |
| UIs generadas | Coolify / GitHub | MEDIO | Repos privados |
| Voz clonada | OmniVoice | ALTO | Perfil por tenant |

---

## 7. Plan de implementación

### Fase 1 — Integración Open Notebook (2 días)

| Paso | Qué | Quién |
|------|-----|-------|
| 1.1 | Conectar Mystik RAG → Open Notebook API | Yo |
| 1.2 | Crear MCP tools para Open Notebook (ingest, query, generate) | Yo |
| 1.3 | Probar: subir PDF → consultar desde Mystik | Yo |

### Fase 2 — Dyad/Bolt para generación de UIs (3 días)

| Paso | Qué | Quién |
|------|-----|-------|
| 2.1 | Instalar Dyad CLI en el VPS | Yo |
| 2.2 | Crear MCP tool `dyad_generate_ui` | Yo |
| 2.3 | Integrar salida → Coolify deploy | Yo |
| 2.4 | Probar: "generar landing para restaurant" | Yo |

### Fase 3 — Lobe Chat como frontend unificado (1 día)

| Paso | Qué | Quién |
|------|-----|-------|
| 3.1 | Configurar Lobe Chat con plugins | Yo |
| 3.2 | Conectar Mystik como plugin de Lobe Chat | Yo |
| 3.3 | MCP tools de Lobe Chat expuestas via Gateway | Yo |

### Fase 4 — Pipeline completo (2 días)

| Paso | Qué | Quién |
|------|-----|-------|
| 4.1 | Flujo: prompt → Dyad → UI → Coolify deploy | Yo |
| 4.2 | Flujo: PDF → Open Notebook → Content Studio → OmniVoice | Yo |
| 4.3 | Flujo: cliente nuevo → registro → tenant → onboarding | Yo |
| 4.4 | Tests de integración | Yo |

---

## 8. Stack total

```
FRONTEND:
  Lobe Chat (:3210) — Interfaz de chat universal
  Next.js (:3100) — Landing + Dashboard
  ABE Music (:5180) — Cliente showcase

AI / GENERACIÓN:
  Mystik AI (:5200) — Orquestador + Auth
  Open Notebook (:8502) — RAG + generación de contenido
  Content Studio (:8765) — Imágenes, TTS, video
  OmniVoice (:3900) — Clonación de voz
  Dyad / Bolt — Generación de UIs desde prompt

INFRA:
  Coolify (:8081) — Deploy automático
  ChromaDB (:8001) — Vector store
  Redis (:6380) — Agent Bus + cache
  PostgreSQL (:5433) — Datos multi-tenant
  LiveKit (:7880) — Voz WebRTC

SEGURIDAD:
  Fail2ban — 4 jails
  SlowAPI — Rate limiting
  Prompt injection guard
  age encrypt — Secrets
  TruffleHog — Pre-commit
```

---

## 9. Score

| Métrica | Score |
|---------|-------|
| Impacto en revenue | 9/10 |
| Automatización | 9/10 |
| Reusabilidad | 10/10 |
| Founder independence | 8/10 |
| Complejidad | 7/10 |
| **Total** | **86/100** |

---

## 10. Kill criteria

- Si Dyad no funciona en VPS headless (sin GPU/display)
- Si Open Notebook no responde a la API
- Si el pipeline prompt→UI→deploy toma > 5 minutos

---

## 11. Scale criteria

- Cuando haya 5+ clientes activos
- Cuando el pipeline se use > 10 veces/día
- Cuando se requiera auto-escalado

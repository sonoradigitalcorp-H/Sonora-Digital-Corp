# Auditoría técnica completa del proyecto

**Session ID:** ses_037ad6741ffekW4XAV1PcOqfm8
**Created:** 8/3/2026, 8:51:24 AM
**Updated:** 8/3/2026, 8:57:23 AM

---

## User

# SYSTEM
Actúa como Principal Software Architect, Platform Engineer y AI Systems Auditor.

NO modifiques ningún archivo.
NO ejecutes cambios.
NO instales dependencias.

Tu única tarea es inspeccionar TODO el workspace actual y generar una auditoría técnica completa.

Piensa como si fueras a recibir este proyecto para mantenerlo durante los próximos 5 años.

---

# OBJETIVO

Quiero conocer absolutamente TODO lo que existe en este proyecto.

No omitas nada.

Si encuentras inconsistencias, duplicados o deuda técnica, repórtalos.

Si algo no existe, indícalo claramente.

No inventes información.

---

# AUDITORÍA

## 1. Arquitectura General

Describe:

- propósito del proyecto
- arquitectura
- bounded contexts
- dominios
- subdominios
- arquitectura física
- arquitectura lógica
- arquitectura de agentes
- arquitectura MCP
- arquitectura AI
- arquitectura frontend
- arquitectura backend
- arquitectura infraestructura

---

## 2. Árbol del Proyecto

Genera el árbol completo.

Explica cada carpeta.

Por ejemplo:

apps/
core/
packages/
modules/
services/
agents/
skills/
specs/
docs/
scripts/
infra/
docker/
.github/
tests/
database/
storage/
assets/
configs/
prompts/
memory/
rag/
mcp/
telemetry/
monitoring/

Indica:

- propósito
- dependencias
- responsable
- estado

---

## 3. Apps

Lista todas las apps.

Para cada una:

- nombre
- objetivo
- estado
- puerto
- framework
- lenguaje
- dependencias
- cliente
- producción o desarrollo

---

## 4. Core

Describe completamente el Core.

Qué responsabilidades tiene.

Qué NO debería contener.

Qué servicios ofrece.

Qué módulos dependen de él.

---

## 5. Modules

Lista todos.

Para cada módulo:

- objetivo
- quién lo consume
- dependencias
- APIs
- estado
- reutilización

---

## 6. Packages

Lista todos los packages internos.

SDKs.

Shared UI.

Shared Types.

Utilities.

Libraries.

---

## 7. Servicios

Lista todos los servicios.

Locales.

Docker.

Cloud.

systemd.

Background jobs.

Cron.

Workers.

---

## 8. Agentes

Lista todos los agentes AI.

Para cada uno:

- nombre
- propósito
- herramientas
- MCPs
- memoria
- prompts
- modelo
- autonomía
- estado

---

## 9. MCP Servers

Detecta TODOS los MCP.

Para cada uno:

- nombre
- endpoint
- puerto
- transporte
- autenticación
- herramientas
- estado
- dependencias

---

## 10. Herramientas

Lista todas las tools.

Playwright

Git

Filesystem

Terminal

Browser

Telegram

Discord

Slack

Supabase

OpenRouter

etc.

Explica quién las usa.

---

## 11. Specs

Detecta todas las SPECs.

Resume cada una.

Estado.

Versionado.

Pendientes.

---

## 12. Metodologías

Detecta si existen prácticas como:

SDD

DDD

TDD

BDD

ADR

RFC

Architecture Decision Records

Conventional Commits

GitFlow

Semantic Versioning

Release Notes

CI/CD

Feature Flags

Code Review

Monorepo

Workspace

Nx

Turborepo

pnpm workspaces

etc.

---

## 13. Stack Tecnológico

Frontend

Backend

Base de datos

Cache

Queue

LLMs

Embeddings

Vector DB

Storage

Cloud

IaC

Containers

Reverse Proxy

Observabilidad

Analytics

Seguridad

Testing

Build

Deploy

---

## 14. Infraestructura

Describe completamente:

Docker

Docker Compose

systemd

Nginx

Redis

Postgres

Neo4j

Qdrant

Chroma

Supabase

Coolify

Vercel

OVH

Hostinger

Cloudflare

Cron

Workers

Backups

SSL

DNS

Firewall

---

## 15. Versionado

Git

Tags

Branches

Releases

Versiones

Historial

Convenciones

---

## 16. Bases de Datos

Lista todas.

Schemas.

Migraciones.

Tablas.

Relaciones.

ORM.

Seeds.

---

## 17. APIs

Todas las APIs.

REST

GraphQL

WebSockets

gRPC

MCP

Internas

Externas

---

## 18. Variables de Entorno

NO mostrar secretos.

Solo indicar:

nombre

descripción

dónde se usa

si falta

si está duplicada

---

## 19. Seguridad

JWT

OAuth

API Keys

Secrets

Permisos

Roles

RBAC

Logs

Auditoría

---

## 20. Observabilidad

Logs

Tracing

Metrics

Dashboards

Alertas

Healthchecks

---

## 21. Automatizaciones

n8n

Cron

Workers

Pipelines

GitHub Actions

CI

CD

Bots

---

## 22. Dependencias

Detecta:

dependencias obsoletas

duplicadas

sin usar

rotas

conflictos

---

## 23. Deuda Técnica

Enumera:

duplicados

módulos muertos

código muerto

TODOs

FIXMEs

riesgos

acoplamientos

problemas arquitectónicos

---

## 24. Oportunidades

Qué puede modularizarse.

Qué puede convertirse en plugin.

Qué debería ser Core.

Qué debería salir del Core.

Qué debería ser Package.

Qué debería ser App.

---

## 25. Roadmap

Genera un roadmap dividido en:

Crítico

Alta prioridad

Media

Baja

Futuro

---

# FORMATO FINAL

Entrega un documento organizado con:

1. Executive Summary

2. Architecture Overview

3. Repository Tree

4. Inventory

5. Infrastructure Map

6. AI Ecosystem

7. MCP Ecosystem

8. Dependency Graph

9. Risk Report

10. Technical Debt

11. Recommendations

12. Roadmap

13. Score del proyecto (0-100)

14. Madurez de Arquitectura

15. Madurez DevOps

16. Madurez AI

17. Madurez Seguridad

18. Madurez Escalabilidad

19. Checklist de mejoras

20. Próximas acciones recomendadas

No hagas modificaciones. Solo inspecciona y documenta. 

---

## Assistant (Build · MiMo V2.5 · 7.5s)

_Thinking:_

The user wants a comprehensive technical audit of the entire workspace. I need to inspect everything without making any modifications. Let me start by exploring the directory structure to understand the project.

Let me begin by examining the root directory and then systematically explore each area.

I'll conduct a comprehensive technical audit of the entire workspace. Let me start by exploring the directory structure systematically.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/mystic/Documentos/Sonora Digital Corp"
}
```

**Output:**
```
<path>/home/mystic/Documentos/Sonora Digital Corp</path>
<type>directory</type>
<entries>
.pytest_cache/
Audiovisuales/
Clientes/
Finanzas/
ops/
Prototipos/
Referencia/
session-ses_03b6.md
session-ses_045c.md
session-ses_04ae.md
session-ses_04cccc.md
sonora-digital-corp/
tenants/

(13 entries)
</entries>
```

**Tool: filesystem_list_allowed_directories**

**Input:**
```json
{}
```

**Error:**
```
Tool 'list_allowed_directories' has an invalid outputSchema: JSON Schema declares an unsupported dialect ("$schema": "http://json-schema.org/draft-07/schema#"). The default validator supports JSON Schema 2020-12 only; pass a pre-configured Ajv instance to AjvJs
```

---

## Assistant (Build · MiMo V2.5 · 2.8s)

_Thinking:_

Let me explore the workspace more systematically. I need to look at all the directories and files.

**Tool: filesystem_list_directory**

**Input:**
```json
{
  "path": "/home/mystic/Documentos/Sonora Digital Corp"
}
```

**Error:**
```
Tool 'list_directory' has an invalid outputSchema: JSON Schema declares an unsupported dialect ("$schema": "http://json-schema.org/draft-07/schema#"). The default validator supports JSON Schema 2020-12 only; pass a pre-configured Ajv instance to AjvJs
```

**Tool: glob**

**Input:**
```json
{
  "pattern": "**/*",
  "path": "/home/mystic/Documentos/Sonora Digital Corp"
}
```

**Output:**
```
/home/mystic/Documentos/Sonora Digital Corp/Referencia/prompt kimi.txt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/psw.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/untitled_2.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/untitled_1.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/untitled_0.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/coniguracion qween ultima 29 marzo.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/untitled_0_1.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/hostingerR.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/recuperacion mys.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/deepseek abe music.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/deploy sonora.sh.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/hostinguer api.odt
/home/mystic/Documentos/Sonora Digital Corp/Referencia/SONORA_DIGITAL_CORP_ v3 16 marzo.odt
/home/mystic/Documentos/Sonora Digital Corp/session-ses_04ae.md
/home/mystic/Documentos/Sonora Digital Corp/ops/state/skill-registry.json
/home/mystic/Documentos/Sonora Digital Corp/ops/state/engram_aztrotech.db
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Nóminas/NOMINA SEMANAL NO 23 06 JUNIO 2026
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Nóminas/MONTAJES Y MAQUINADOS TORAGUICO 06 JUNIO 2026
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Nóminas/OSVALDO CHAVEZ 06 JUNIO 2026
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/report.pdf
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/230-3680-6000156-N.PDF
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/SAT-FIEL/Requerimiento_FIEL_HEUO9402195R4_20250911_142333.req
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/SAT-FIEL/Opinion de cumplimiento Negativa 29 abril 2026.pdf
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/SAT-FIEL/Constancia de situación fiscal .pdf
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/SAT-FIEL/heuo9402195r4.cer
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/SAT-FIEL/Claveprivada_FIEL_HEUO9402195R4_20250911_142333.key
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Facturas/Factura-186.pdf
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Facturas/Factura-180 (1).pdf
/home/mystic/Documentos/Sonora Digital Corp/Finanzas/Contrato_tyc_aviso_de_privacidad_Swap.pdf
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/thumbnails-1.jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/social_UnklD____._______________________________________--ar_11_--mo_fbfb4f4b-9e44-4e22-b854-498099402c9f_0.mp4
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/P5XD7.jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/1778837016.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/grok-video-64d8f694-c763-44e6-854a-e2e1b3520171.mp4
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/thumbnails-1 (1).jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/photo_5116518832796273789_y.jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/image-1778601966912.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/image.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/grok-video-df713ba9-cd96-45fc-9777-bcdc0ea60879.mp4
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/olgaifu9921851413_sphere_--profile_emzi4g9_--v_8.1_c1c4ee66-246c-4977-8e5f-22fd4aac6066_2.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/Lyts9.jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/253a6a4c-d8d0-4d9e-8cc1-f99675021cf1_hd.mp4
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/General/lucid-origin_hyperrealistic_portrait_of_a_confident_34-year-old_Mexican_woman_elegant_and_pow-0.jpg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/ABE Music/VÍCTOR PIÑERO CON LOS MELODICOS - 18 TEMAS INOLVIDABLES. [qvsR54cCUys].mp3
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sub y pick up negro abe.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_32701a5f-00c5-474e-9138-8f779a1a72f1_2.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_95827c19-19c3-4305-ba42-50eec26673fc_0.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/output_439676762_0_1783195326335.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_194e9184-6a5b-430b-a72c-f59a3bd98c51_3.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/ChatGPT Image May 12, 2026, 01_15_13 PM (1).png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/FUNDILLUDA2.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/ChatGPT Image May 12, 2026, 01_15_16 PM (3).png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_32701a5f-00c5-474e-9138-8f779a1a72f1_0.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_4ddf973e-e46a-4650-9f15-b171fbe51c91_0.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_93f5eaaf-6398-40e8-af1d-155593eb3ad7_1.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/accent-bar.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_95827c19-19c3-4305-ba42-50eec26673fc_2.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/equipo de trabajo.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/produccion interna.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/chat-export-1781551199880.json
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/ChatGPT Image May 12, 2026, 01_15_17 PM (4).png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/logoyami.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_4ddf973e-e46a-4650-9f15-b171fbe51c91_2.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/templetes 1.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/Gemini_Generated_Image_n40vw5n40vw5n40v.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/FUNDILLUDA.jpeg
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/oficina central estudio.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/Gemini_Generated_Image_7sqpng7sqpng7sqp.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/Gemini_Generated_Image_jy5fvijy5fvijy5f.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/ChatGPT Image May 12, 2026, 01_15_15 PM (2).png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Sonora Digital Corp/sontoken666996_Ultra-detailed_cinematic_portrait_of_a_norther_194e9184-6a5b-430b-a72c-f59a3bd98c51_1.png
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/debian-binary
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/control/md5sums
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/control/control
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/control.tar.gz
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/data/usr/bin/OpenCode
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/data/usr/bin/opencode-cli
/home/mystic/Documentos/Sonora Digital Corp/Audiovisuales/Instaladores/opencode-desktop-linux-amd64/data/usr/share/metainfo/ai.opencode.opencode.metainfo.xml
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/Makefile
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/portal/index.html
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/conftest.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/test_provisioning.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/test_onboarding_memory.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/test_onboarding_codes.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/test_abe_service.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/conftest.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/__pycache__/test_receiver.cpython-310-pytest-9.0.3.pyc
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/__pycache__/test_edge_client.cpython-310-pytest-9.0.3.pyc
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/__pycache__/conftest.cpython-310-pytest-9.0.3.pyc
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/test_receiver.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/openclaw-edge/test_edge_client.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/test_pricing_engine.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/redteam/README.md
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/redteam/redteam.yaml
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/__init__.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/structural/conftest.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/structural/test_unification_evals.py
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/structural/__pycache__/test_specs_schema.cpython-310-pytest-9.0.3.pyc
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/structural/__pycache__/conftest.cpython-310-pytest-9.0.3.pyc
/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tests/evals/structural/__pycache__/test_registry.cpython-310-pytest-9.0.3.pyc

(Results are truncated: showing first 100 results. Consider using a more specific path or pattern.)
```

---

## Assistant (Build · MiMo V2.5 · 174.2s)

_Thinking:_

There are a lot of files. Let me explore more systematically by looking at the main directories.

**Tool: task**

**Input:**
```json
{
  "description": "Explore sonora-digital-corp repo",
  "prompt": "Explore the directory /home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp thoroughly. I need:\n\n1. Full directory tree structure (recursive) - list ALL directories and files\n2. Read these key files if they exist: Makefile, package.json, pyproject.toml, requirements.txt, docker-compose.yml, Dockerfile, .env, .env.example, README.md, AGENTS.md, opencode.json, opencode.jsonc, any config files\n3. List all Python source files (*.py) and their imports\n4. List all YAML/JSON config files\n5. Find any MCP server configurations\n6. Find any agent definitions\n7. Find any skill definitions\n8. Find any spec files\n9. Find any prompt files\n10. Find any database schemas or migrations\n\nReturn ALL findings in full detail. Do NOT summarize or omit anything.",
  "subagent_type": "explore"
}
```

**Output:**
```
<task id="ses_037ad20b9ffek6m765wZvbYrAB" state="completed">
<task_result>
Now I have enough data to compile the full report. Here is the complete exploration of the project:

---

# COMPREHENSIVE EXPLORATION REPORT: sonora-digital-corp

## 1. TOP-LEVEL DIRECTORY STRUCTURE

```
sonora-digital-corp/
├── .agents/                    # Agent definitions (OpenCode)
├── .engram/                    # Engram memory state
├── .env.example                # Root environment variables template
├── .flake8                     # Flake8 config
├── .git/                       # Git repository
├── .githooks/                  # Git hooks
├── .github/                    # GitHub Actions workflows
├── .gitignore                  # Git ignore rules
├── .hermes/                    # Hermes agent config
├── .opencode/                  # OpenCode config
├── .opencodeignore             # OpenCode ignore rules
├── .planning/                  # Planning artifacts
├── .pre-commit-config.yaml     # Pre-commit hooks config
├── .pytest_cache/              # Pytest cache
├── .specify/                   # Specify config
├── .vercel.json                # Vercel project config
├── .vercelignore               # Vercel ignore rules
├── adrs/                       # Architecture Decision Records
├── AGENTS.md                   # Agent governance document
├── apps/                       # Core applications (Layer 2)
├── BLUEPRINT.md                # Full system architecture blueprint
├── capabilities/               # Business capabilities
├── CHANGELOG.md                # Project changelog
├── CLAUDE.md                   # Claude Code session workflow
├── clients/                    # External clients (Layer 4)
├── config/                     # Configuration files (SSOT)
├── docs/                       # Documentation
├── infra/                      # Infrastructure (Layer 1)
├── kernel/                     # System constitution (Layer 0)
├── Makefile                    # Development commands
├── opencode.json               # OpenCode main config
├── ops/                        # Operations playbooks
├── portal/                     # Grimoire 3D portal (Three.js)
├── process/                    # SPEC pipeline (active/completed)
├── products/                   # SDC products (Layer 3)
├── pyproject.toml              # Python project config
├── README.md                   # Project README
├── reference/                  # Closed specs, archaeology
├── requirements.txt            # Python dependencies
├── scripts/                    # 70+ utility scripts
├── sdc-brain-vault/            # Brain vault
├── SDC-STATUS-COMPLETO.md      # Full system status
├── shared/                     # Shared utilities
├── skills/                     # All skills + reusable tools
├── skills-lock.json            # Skills lockfile
├── state/                      # Live system state
├── tenants/                    # Tenant deployments
└── tests/                      # Test suite
```

---

## 2. KEY CONFIG FILES

### 2.1 Makefile
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/Makefile`
- **87 lines** with targets: `test`, `test-all`, `test-v`, `test-integration`, `sdd-test`, `sdd-eval`, `sdd-init`, `eval`, `eval-structural`, `eval-promptfoo`, `eval-dashboard`, `score`, `constitution-gate`, `doctor`, `doctor-fix`, `doctor-quick`, `doctor-json`, `alias`, `validate-configs`, `clean`
- Uses `PYTHONPATH=. python3 -m pytest` for all test commands

### 2.2 requirements.txt
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/requirements.txt`
- **38 lines** - Key deps: `fastapi>=0.139.0`, `uvicorn>=0.51.0`, `neo4j>=6.2.0`, `qdrant-client>=1.18.0`, `fastmcp>=0.2.0`, `faster-whisper>=1.2.1`, `edge-tts>=6.1.0`, `ollama>=0.6.2`, `pytest>=9.1.0`, `pytest-bdd>=8.0.0`, `tiktoken>=0.13.0`

### 2.3 pyproject.toml
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/pyproject.toml`
- Project: `sonora-digital-corp` v2.0.0, requires Python >=3.10
- Ruff: line-length=160, select=E,F,I,UP,B
- pytest: testpaths=["tests"], asyncio_mode="auto"
- Coverage: source=["apps","scripts","skills"], fail_under=60

### 2.4 .env.example
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.env.example`
- **56 lines** - Secrets for: Postgres, Neo4j, Redis, Telegram bots (AZTROTECH_BOT_TOKEN, NOTIF_BOT_TOKEN, TELEGRAM_BOT_TOKEN), WhatsApp (WACLI_STORE, WACLI_AUTH_TOKEN, SDC_WA_API_KEY), OpenRouter, Hermes, MercadoPago, NextAuth, Sonora Client, OpenClaw, n8n, Google Sheets/Drive

### 2.5 .vercel.json
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.vercel.json`
- projectId: `prj_PT9F2uqXoNvbzHbHWOgmdWnxEzCc`, orgId: `team_3K3rRmf4gHFN7V4gPMKTYv2T`

### 2.6 opencode.json (Root)
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/opencode.json`
- **467 lines** - Main OpenCode configuration
- **20 agents defined**: mystic (primary/god autonomy), hermes, openclaw, sdd, sdd-spec, sdd-design, sdd-apply, sdd-verify, sdd-archive, sales, dev, support, agent-os, knowledge, finance, security, ops, quality, strategy, builder, reviewer, social, content, music
- **7 MCP servers**: openclaw (localhost:18789), engram (149.56.46.173:7437), qdrant (149.56.46.173:6333), neo4j (149.56.46.173:7687), n8n (149.56.46.173:5678), adk (149.56.46.173:6401), shield (149.56.46.173:8930)
- **24 commands defined**: status, backup, brain, sdd-new, build, sales, dev, support, agent, knowledge, finance, security, ops, quality, strategy, social, content, music, doc, plan, verify, adk, sdk, adr, skill, inbox, openclaw, shield

### 2.7 opencode.jsonc (Skills)
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/skills/opencode.jsonc`
- Model: `opencode/deepseek-v4-flash-free`, complex: `opencode/kimi-k2.6`
- skillsDir: `.opencode/skills`, agentsDir: `.opencode/agents`

### 2.8 CLAUDE.md
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/CLAUDE.md`
- Session workflow: check folder, run `start-session.sh`, create branch `session/YYYYMMDD-*`
- Always communicate in Spanish, be brief (5 lines max)
- Memory via Engram between sessions

### 2.9 AGENTS.md
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/AGENTS.md`
- **136 lines** - Full system documentation
- VPS: sdc-prod at 149.56.46.173, Ubuntu 26.04, 11GB RAM
- 6 concentric layers architecture documented
- Docker commands, gotchas, key paths

### 2.10 BLUEPRINT.md
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/BLUEPRINT.md`
- **594 lines** - Complete system architecture document
- Tech stack: PostgreSQL 15, Redis 7, Qdrant, n8n, FastAPI, Vue 3 + Vite, Three.js, edge-tts, faster-whisper
- Active clients: Aztrotech (partner_pro), ABE Music (partner_pro), Nathy Conta (pro), El Joyero (basic)

### 2.11 SDC-STATUS-COMPLETO.md
- **Path**: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/SDC-STATUS-COMPLETO.md`
- **353 lines** - Full system status as of 2026-08-02
- 30 recent commits, 19 ADRs, 7 specs/SDD, 40+ MCP servers
- Voice: TTS (edge-tts DaliaNeural :8765), STT (faster-whisper :8766)

---

## 3. ALL OPencode.json FILES

| Path | Purpose |
|------|---------|
| `/home/mystic/.../opencode.json` | Root - main config (20 agents, 7 MCPs, 24 commands) |
| `/home/mystic/.../skills/opencode.jsonc` | Skills directory config |
| `/home/mystic/.../clients/Abe Music Group/hub/opencode.json` | ABE Music Hub |
| `/home/mystic/.../clients/Hermosillo Contability Corp./opencode.json` | Nathy Conta |
| `/home/mystic/.../clients/Joyeria/opencode.json` | El Joyero |
| `/home/mystic/.../config/tenants/mds-corp/opencode.json` | MDS Corp tenant |
| `/home/mystic/.../config/tenants/el-joyero/opencode.json` | El Joyero tenant |
| `/home/mystic/.../config/tenants/nathy-conta/opencode.json` | Nathy Conta tenant |
| `/home/mystic/.../tenants/hermosillo-contabilidad/config/opencode.json` | Hermosillo config |
| `/home/mystic/.../tenants/hermosillo-contabilidad/opencode.json` | Hermosillo root |
| `/home/mystic/.../tenants/abe-music/hub/opencode.json` | ABE Music tenant hub |

---

## 4. ALL DOCKER-COMPOSE FILES

| Path | Services |
|------|----------|
| `/home/mystic/.../infra/docker-compose.yml` | **Core**: postgres:15, redis:7-alpine, neo4j, qdrant, mcp-server, n8n, telegram-bot, langfuse, langfuse-db (275 lines) |
| `/home/mystic/.../infra/docker-compose.vps.yml` | VPS override |
| `/home/mystic/.../infra/docker-compose.data.yml` | Data services |
| `/home/mystic/.../infra/docker-compose.scrapers.yml` | Scraper services |
| `/home/mystic/.../infra/docker-compose.omnivoice.yml` | OmniVoice |
| `/home/mystic/.../infra/supabase/docker-compose.yml` | Supabase |
| `/home/mystic/.../clients/Abe Music Group/docker-compose.yml` | ABE Music full stack |
| `/home/mystic/.../clients/Abe Music Group/hub/docker-compose.yml` | ABE Hub |
| `/home/mystic/.../clients/Abe Music Group/studio/docker-compose.yml` | ABE Studio |
| `/home/mystic/.../products/clon-digital/docker-compose.yml` | Clone Digital |
| `/home/mystic/.../products/nsfw-ai-studio/docker-compose.yml` | NSFW AI Studio |
| `/home/mystic/.../products/agent-marketplace/docker-compose.yml` | Agent Marketplace |
| `/home/mystic/.../products/production/omnivoice/docker-compose.yml` | OmniVoice production |
| `/home/mystic/.../products/production/content-studio/docker-compose.yml` | Content Studio |
| `/home/mystic/.../products/production/google-mcp/docker-compose.yml` | Google MCP |
| `/home/mystic/.../apps/hermes/hermes-agent/docker-compose.yml` | Hermes Agent |
| `/home/mystic/.../tenants/abe-music/docker-compose.yml` | ABE tenant |
| `/home/mystic/.../tenants/Aztrotech/infra/docker-compose.yml` | Aztrotech |

---

## 5. ALL DOCKERFILES (39 total)

| Path | Purpose |
|------|---------|
| `/home/mystic/.../infra/Dockerfile` | Core infra |
| `/home/mystic/.../infra/mcp-server/Dockerfile` | MCP server |
| `/home/mystic/.../infra/neo4j/Dockerfile` | Neo4j custom |
| `/home/mystic/.../infra/telegram/Dockerfile` | Telegram bot |
| `/home/mystic/.../infra/wacli/Dockerfile` | WhatsApp CLI |
| `/home/mystic/.../infra/qdrant/Dockerfile` | Qdrant custom |
| `/home/mystic/.../skills/mcp/Dockerfile` | MCP skills server |
| `/home/mystic/.../skills/openclaw/Dockerfile` | OpenClaw |
| `/home/mystic/.../apps/hermes/hermes-agent/Dockerfile` | Hermes Agent |
| `/home/mystic/.../apps/frontends/sonora-web/Dockerfile` | Sonora Web |
| `/home/mystic/.../apps/sonora_engine/Dockerfile` | Sonora Engine |
| `/home/mystic/.../products/clon-digital/orchestrator/Dockerfile` | Clone orchestrator |
| `/home/mystic/.../products/agent-marketplace/Dockerfile` | Agent Marketplace |
| `/home/mystic/.../products/production/mystik/Dockerfile` | Mystik |
| Plus 25 more across clients/ and tenants/ | Various client services |

---

## 6. KERNEL (Layer 0 - Constitution)

**Path**: `/home/mystic/.../kernel/` - **30 files**

| File | Purpose |
|------|---------|
| `SOUL.md` | System identity - "We are builders of systems that serve life" |
| `OMEGA-PROMPT.md` | Enterprise Operating Constitution v10.0 (651 lines) |
| `TRUTH.md` | System truth |
| `10-RULES.md` | 10 core rules |
| `MANIFESTO.md` | Company manifesto |
| `CONTRATO.md` | Contract |
| `AI-ETHICS.md` | AI ethics |
| `hermes-soul.md` | Hermes soul |
| `CHECKSUMS.sha256` | File integrity |
| `000-governance.md` | Governance |
| `010-agent-rules.md` | Agent rules |
| `020-data-policy.md` | Data policy |
| `030-security.md` | Security |
| `040-evolution.md` | Evolution |
| `00-index.yaml`, `01-mission.yaml`, `02-vision.yaml` | Mission/vision |
| `10-principles.yaml`, `20-engineering.yaml`, `30-architecture.yaml` | Principles |
| `40-security.yaml`, `50-quality.yaml`, `60-agents.yaml` | Security/quality |
| `70-memory.yaml`, `80-events.yaml`, `90-governance.yaml` | Memory/events |
| `100-cost.yaml`, `110-brand.yaml`, `120-ux.yaml`, `130-ethics.yaml` | Cost/brand/UX |

---

## 7. AGENT DEFINITIONS

### 7.1 OpenCode Agents (from opencode.json)
20 agents defined in the root `opencode.json`:

| Agent | Mode | Description |
|-------|------|-------------|
| **mystic** | primary/god | Primary agent - alma de SDC, god autonomy |
| hermes | subagent | Multi-channel gateway (Telegram, WhatsApp, Desktop) |
| openclaw | subagent | 42 specialized skills gateway |
| sdd | subagent | SDD Orchestrator - 6 phases pipeline |
| sdd-spec | subagent | Spec generation from briefings |
| sdd-design | subagent | Plan + tasks from specs |
| sdd-apply | subagent | Implementation execution |
| sdd-verify | subagent | Constitution/checklist/tests validation |
| sdd-archive | subagent | Results documentation |
| sales | subagent | Lead gen, qualification, proposals |
| dev | subagent | Software delivery, CI/CD |
| support | subagent | Tickets, SLAs |
| agent-os | subagent | Harness lifecycle, skill registry |
| knowledge | subagent | 7-layer memory, ADRs |
| finance | subagent | FinOps, revenue tracking |
| security | subagent | Secrets, audit, incidents |
| ops | subagent | Infrastructure, monitoring |
| quality | subagent | Test frameworks, audits |
| strategy | subagent | Initiatives, enterprise score |
| builder | subagent | Feature implementation |
| reviewer | subagent | Code review, security |
| social | subagent | Social media publishing |
| content | subagent | Blogs, designs, presentations |
| music | subagent | Beats, lyrics, covers, distribution |

### 7.2 ADK Agents (from config/registry.json)
36+ agents defined in YAML under `skills/mcp/adk/agents/`:

**Core agents**: booking-agent, content-agent, onboarding-agent, research-agent, sales-agent, support-agent

**ABE Music agents**: abe-agent, abe-analytics-agent, abe-crm-agent, abe-marketing-agent, abe-revenue-agent, abe-scheduler-agent

**ABE subsystem agents**: abe-artist-management-{analytics,crm,marketing,revenue,scheduler}-agent, abe-content-factory-{analytics,crm,marketing,scheduler,support}-agent, abe-fan-crm-{analytics,crm,marketing,scheduler}-agent, abe-music-saas-{analytics,crm,revenue,scheduler,support}-agent, abe-revenue-engine-{analytics,crm,revenue,scheduler,support}-agent

### 7.3 Client Agent YAMLs
- **ABE Music**: `clients/Abe Music Group/skills/agents/booking-agent.yaml`, `executive-agent.yaml`, `marketing-agent.yaml`
- **Nathy Conta**: `clients/Hermosillo Contability Corp./skills/agents/nathy-{conta,cfdi,nominas,resico}-agent.yaml`
- **Template**: `skills/_template/agents/agent.yaml`

---

## 8. SKILL DEFINITIONS

### 8.1 Skills Directory (`skills/`)
**138 entries** including:

**Business Skills** (`.skill.md` files):
- `validate-quality.skill.md`, `openclaw-policy.skill.md`, `capture-knowledge.skill.md`
- `hermes-auditor.skill.md`, `openclaw-telegram.skill.md`, `sdk-python.skill.md`
- `clone-service.skill.md`, `deploy-code.skill.md`, `incident-response.skill.md`
- `whatsapp-onboarding.skill.md`, `whatsapp-catalog.skill.md`
- `niche-tacos-el-fogon-catalog.skill.md`, `niche-barberking-studio-catalog.skill.md`
- `niche-mystik-music-catalog.skill.md`, `niche-bufete-juridico-catalog.skill.md`
- `plan-strategy.skill.md`, `qualify-lead.skill.md`, `track-finance.skill.md`
- `sdc-social-publish.skill`, `skill-create.skill.md`, `spawn-agent.skill.md`

**Process Skills** (`skills/process/`):
- `sdd-design.skill.md`, `sdd-verify.skill.md`, `sdd-orchestrator.skill.md`
- `sdd-spec.skill.md`, `sdd-apply.skill.md`, `sdd-archive.skill.md`
- `auto-doc.skill.md`, `gsd.skill.md`, `page-fix.skill.md`

**Tech Skills** (language/framework directories):
- `python/`, `javascript/`, `html/`, `css/`, `go/`, `nuxt/`, `nextjs-react/`
- `pytest/`, `pydantic/`, `pandas/`, `numpy/`, `sqlmodel/`
- `playwright-cli/`, `bash-shell/`, `github-actions/`, `git-hooks/`
- `eslint/`, `tailwind-css/`, `htmx/`, `alpinejs/`

**Capability Skills** (business capabilities):
- `sync-artist-data/`, `analyze-artist/`, `generate-video/`
- `search-knowledge/`, `score-artist/`, `manage-crm/`
- `process-payment/`, `publish-track/`

### 8.2 Skill YAML Files
- `skills/_template/skills/skill.yaml` - Template
- `skills/templates/skill-spec.yaml` - Spec template
- `clients/Abe Music Group/skills/skills/{streams,booking,promotion,finance,releases}/skill.yaml`
- `clients/Hermosillo Contability Corp./skills/skills/{contpaq-polizas,nominas,sat-declaraciones,organizar-carpetas,cfdi-timbrado,conciliacion-bancaria,resico-calculo}.yaml`

### 8.3 Capability Registry (skills/index.yaml)
10 capabilities registered:
1. `sync-artist-data` (active, collector agent)
2. `analyze-active` (active, research-agent)
3. `generate-video` (experimental, video-agent)
4. `search-knowledge` (active, null agent)
5. `score-artist` (active, research-agent)
6. `manage-crm` (experimental, sales-agent)
7. `publish-track` (experimental, marketing-agent)
8. `process-payment` (experimental, finance-agent)
9. `multi-tenant-platform` (draft, mystic)
10. `clone-person` (active, clone-agent)

### 8.4 Skills Lockfile (skills-lock.json)
**335 lines** - 40+ skills from `the-perfect-developer/the-perfect-opencode` GitHub source, including: agent-configuration, alembic, alpinejs, bash-shell, capacitor, claude-agent-sdk, command-creation, conventional-git-commit, copilot-sdk, css, eslint, git-hooks, github-actions, go, go-testing, golangci-lint, google-adk, html, htmx, interactive-questions, javascript, json-style, markdown, nextjs-react, numpy, nuxt, pandas, pandera, perfectcode-zen-{evaluation,ideation,implement,plan}, playwright-cli, pydantic, pytest, python, python-{aiomysql,bandit,bigquery-sdk,dependency-injection,flet,mcp,mypy,pip-audit,pymysql,ruff,uv}, rules-creation, seo-best-practices, skill-creation, sqlmodel, tailwind-css, turso-libsql, typescript-style, unit-testing

---

## 9. MCP SERVER CONFIGURATIONS

### 9.1 MCP Ecosystem (skills/mcp/mcp-ecosystem.json)
- **Gateway**: sonora-mcp-gateway (HTTP, port 18989, 108 tools, 9 resources)
- **8 servers registered**: postgres, qdrant, neo4j, redis, n8n (inactive), uptime (inactive), hermes, openclaw

### 9.2 MCP Servers (skills/mcp/servers/)
**30+ MCP server files**:
- **Python MCP servers**: `engram_mcp.py`, `rag_mcp.py`, `llm_mcp.py`, `voice_clone_mcp.py`, `kokoro_mcp.py`, `whisper_mcp.py`, `crm_mcp.py`, `payments_mcp.py`, `commissions_mcp.py`, `pricing_mcp.py`, `credit_mcp.py`, `playwright_mcp.py`, `wacli_mcp.py`, `twilio_mcp.py`, `onboarding_mcp.py`, `provision_mcp.py`, `content_mcp.py`, `fal_ai_mcp.py`, `lora_mcp.py`, `generate_mcp.py`, `omnivoice_mcp.py`, `firecrawl_mcp.py`, `hasura_mcp.py`, `supabase_mcp.py`, `ffmpeg_mcp.py`, `upload_mcp.py`, `cost_tracker_mcp.py`, `routing_mcp.py`, `sdc_mcp_stdio.py`, `openlovable_mcp.py`, `mercadopago_mcp.py`
- **JSON MCP configs**: `postgres-mcp.json`, `qdrant-mcp.json`, `neo4j-mcp.json`, `redis-mcp.json`, `n8n-mcp.json`, `metabase-mcp.json`, `uptime-mcp.json`, `paperclip-mcp.json`
- **Gateway JS**: `gateway/mcp-gateway.js`, `gateway/mcp-server-http.js`

### 9.3 Tenant MCP Configs
- `config/tenants/_template/mcp.yaml` - Template (calendar + crm)
- `config/tenants/{abe-music,sonora-digital,nathy-conta,el-joyero,azrec,mds-corp,r1}/mcp.yaml`

### 9.4 OpenCode MCP Config (from opencode.json)
7 MCP servers configured:
| Name | URL | Description |
|------|-----|-------------|
| openclaw | localhost:18789 | 42 skills gateway |
| engram | 149.56.46.173:7437 | Persistent memory |
| qdrant | 149.56.46.173:6333 | Vector DB |
| neo4j | 149.56.46.173:7687 | Graph DB |
| n8n | 149.56.46.173:5678 | Workflow automation |
| adk | 149.56.46.173:6401 | 36 ADK agents |
| shield | 149.56.46.173:8930 | Security diagnostics |

---

## 10. SPEC FILES

### 10.1 Active Specs (process/active/)
- `SPEC-20260702-001.md`, `SPEC-20260703-A.md`, `SPEC-20260703-B.md`, `SPEC-20260703-C.md`
- `SPEC-20260704-ABE-001.md`, `SPEC-20260704-EXECUTION.md`, `SPEC-20260704-EVOLUTION.md`
- `SPEC-20260710-INTEGRATION.md`, `SPEC-20260712-SONORA-001.md`, `SPEC-20260712-SONORA-002.md`
- `SPEC-20260718-CLONE-SERVICE.md`, `SPEC-20260718-ENGRAM-AUTOCAPTURE.md`, `SPEC-20260718-ONBOARDING.md`
- `SPEC-20260719-SOCIAL-001.md`, `SPEC-20260719-WHATSAPP-OS-FASE1.md`
- `SPEC-20260722-001.md`, `SPEC-20260726-4PILARES.md`, `SPEC-20260726-ECOSYSTEM.md`
- `sdd-kit-ecosystem/SPEC-ECOSYSTEM.md`

### 10.2 Completed Specs (process/completed/)
25+ completed spec directories with SPEC.md, gherkin/, SCORE.md, ADR.md files

### 10.3 Capability Specs (process/specs/capabilities/)
- `sync-artist-data/`, `process-payment/`, `multi-tenant-platform/`, `manage-crm/`
- `score-artist/`, `analyze-artist/`, `clone-person/`, `search-knowledge/`, `generate-video/`

---

## 11. PROMPT FILES

### 11.1 Kernel Prompts
- `/home/mystic/.../kernel/OMEGA-PROMPT.md` - Master prompt (651 lines)
- `/home/mystic/.../kernel/SOUL.md` - Identity prompt
- `/home/mystic/.../kernel/TRUTH.md` - System truth

### 11.2 Skills Prompts
- `skills/prompts/OS/` - OS-level prompts (Sales-OS.md, Dev-OS.md, Support-OS.md, Agent-OS.md, Knowledge-OS.md, Finance-OS.md, Security-OS.md, Ops-OS.md, Quality-OS.md, Strategy-OS.md)
- `skills/prompts/evolution-agent.md`, `skills/prompts/optimizer.md`, `skills/prompts/self-heal.md`

### 11.3 Tenant Prompts
- `config/tenants/{_template,abe-music,sonora-digital,nathy-conta,el-joyero,azrec,mds-corp,r1}/prompt.md`
- `config/tenants/abe-music/skills/booking-flow.md`
- `config/tenants/sonora-digital/skills/infra-manage.md`

### 11.4 Agent Prompts (ABE Music)
- `clients/Abe Music Group/skills/prompts/{booking-agent,marketing-agent,executive-agent}.md`
- `clients/Abe Music Group/agents/{content-agent,sales-agent,ceo-agent,support-agent,marketing-agent,voice-agent}.md`

### 11.5 Promptfoo Test Prompts
- `tests/promptfoo/niches/{music,agencies,ecommerce,real_estate,prof_services}/prompts/{call_agent,lead_scoring,objection_handler}.txt`

### 11.6 Skill Prompt Templates
- `skills/sync-artist-data/prompts/system.md`
- `skills/process-payment/prompts/system.md`
- `skills/templates/seed-data.sql`

---

## 12. GHERKIN / BDD FEATURE FILES

### 12.1 Test Features (tests/gherkin/)
22 feature files:
- `onboarding-{flow,codes,memory,routing,agentic}.feature`
- `clone-{delivery,generation,pricing,recollection,training}.feature`
- `engram-{autocapture,context-recovery,obsidian-sync,versioning}.feature`
- `cost-intelligence.feature`
- `SPEC-20260702-001.feature`, `SPEC-20260703-A.feature`, `SPEC-20260704-ABE-001.feature`
- `SPEC-20260712-SONORA-{001,002}.feature`
- `SPEC-20260719-{WHATSAPP-OS-FASE1,NEXT-SESSION}.feature`

### 12.2 Promptfoo Features
- `tests/promptfoo/gherkin/FEATURE-001-content-pipeline.feature`
- `tests/promptfoo/gherkin/FEATURE-002-agent-registry.feature`
- `tests/promptfoo/gherkin/FEATURE-003-mcp-tools.feature`

### 12.3 Capability Features (process/specs/capabilities/)
- `sync-artist-data/gherkin/sync-artist-data.feature`
- `process-payment/gherkin/process-payment.feature`
- `multi-tenant-platform/gherkin/multi-tenant-platform.feature`
- `manage-crm/gherkin/manage-crm.feature`
- `score-artist/gherkin/score-artist.feature`
- `analyze-artist/gherkin/analyze-artist.feature`
- `clone-person/gherkin/clone-person.feature`
- `search-knowledge/gherkin/search-knowledge.feature`
- `generate-video/gherkin/generate-video.feature`

### 12.4 Client Features
- **ABE Music**: `skills/tests/features/{finance,booking,releases,promotion,streams}.feature`
- **Nathy Conta**: `skills/use-cases/{declarar,organizar-archivos,facturar,calcular-isr,conciliar,procesar-nomina}.feature`
- **El Joyero**: `skills/use-cases/{cotizacion,venta,atencion-cliente}.feature`
- **Joyeria**: `skills/use-cases/{cotizacion,venta,atencion-cliente}.feature`

---

## 13. DATABASE SCHEMAS AND MIGRATIONS

### 13.1 SQL Schema Files
| Path | Description |
|------|-------------|
| `config/clone-schema.sql` | Clone Service schema (SQLite): clients, photos, audio, assets tables |
| `config/migrations/001_brand_schema.sql` | Brand schema migration |
| `skills/templates/seed-data.sql` | Seed data template |

### 13.2 Supabase SQL
- `infra/supabase/volumes/db/realtime.sql`
- `infra/supabase/volumes/db/jwt.sql`
- `infra/supabase/volumes/db/pooler.sql`
- `infra/supabase/volumes/db/_supabase.sql`
- `infra/supabase/volumes/db/logs.sql`
- `infra/supabase/volumes/db/roles.sql`
- `infra/supabase/volumes/db/webhooks.sql`

### 13.3 ABE Music Migrations
- `clients/Abe Music Group/hub/infra/migrations/008_abe_music_hub.sql`
- `clients/Abe Music Group/db/008_abe_music_hub.sql`
- `clients/Abe Music Group/studio/schema.sql`

### 13.4 Infrastructure Migrations
- `infra/migrations/010_sonora_os.sql`

### 13.5 Product Migrations
- `products/production/content-studio/migrations/001_init_content.sql`
- `products/production/content-studio/migrations/002_storage_webhooks.sql`
- `products/production/content-studio/migrations/003_lora_omnivoice.sql`
- `products/production/content-studio/migrations/009_content_system.sql`

### 13.6 Tenant Migrations
- `tenants/Aztrotech/bot/migrations/001_mvp_identity_conversations.sql`

---

## 14. PYTHON SOURCE FILES

### 14.1 MCP Servers (skills/mcp/servers/)
30 Python MCP server files: `engram_mcp.py`, `rag_mcp.py`, `llm_mcp.py`, `voice_clone_mcp.py`, `kokoro_mcp.py`, `whisper_mcp.py`, `crm_mcp.py`, `payments_mcp.py`, `commissions_mcp.py`, `pricing_mcp.py`, `credit_mcp.py`, `playwright_mcp.py`, `wacli_mcp.py`, `twilio_mcp.py`, `onboarding_mcp.py`, `provision_mcp.py`, `content_mcp.py`, `fal_ai_mcp.py`, `lora_mcp.py`, `generate_mcp.py`, `omnivoice_mcp.py`, `firecrawl_mcp.py`, `hasura_mcp.py`, `supabase_mcp.py`, `ffmpeg_mcp.py`, `upload_mcp.py`, `cost_tracker_mcp.py`, `routing_mcp.py`, `sdc_mcp_stdio.py`, `openlovable_mcp.py`, `mercadopago_mcp.py`

### 14.2 Test Files (tests/)
**100+ Python test files** across:
- `tests/unit/` - 30+ unit tests (engram, graph_builder, llm, payments, rag, router, schema, etc.)
- `tests/gherkin/` - 6 BDD test files
- `tests/integration/` - 8 integration tests
- `tests/evals/structural/` - 5 structural eval tests
- `tests/collectors/` - 8 collector tests (spotify, youtube, deezer, tiktok, etc.)
- `tests/agents/` - 2 agent tests
- `tests/brain/` - 1 unified query test
- `tests/ce_son/` - 2 CE Son tests
- `tests/e2e/` - 1 e2e test
- `tests/sdk/` - 1 SDK test
- `tests/planner/` - 5 planner tests
- `tests/mcp/` - 1 MCP test
- `tests/quality/` - 2 quality tests
- `tests/openclaw-edge/` - 2 edge tests
- `tests/apps/` - 4 app tests + prompt tests

### 14.3 Mock Files (tests/mocks/)
- `llm.py`, `neo4j.py`, `qdrant.py` - Mock implementations

### 14.4 Test Steps (tests/steps/)
- `clone_person_steps.py`, `common_steps.py`, `generate_video_steps.py`
- `manage_crm_steps.py`, `multi-tenant-platform_steps.py`
- `process_payment_steps.py`, `search_knowledge_steps.py`, `sync_artist_data_steps.py`

---

## 15. INFRASTRUCTURE (Layer 1)

**Path**: `/home/mystic/.../infra/` - 23 entries

| Entry | Purpose |
|-------|---------|
| `docker-compose.yml` | Core services (postgres, redis, neo4j, qdrant, mcp-server, n8n, telegram, langfuse) |
| `docker-compose.vps.yml` | VPS override |
| `docker-compose.data.yml` | Data services |
| `docker-compose.scrapers.yml` | Scrapers |
| `docker-compose.omnivoice.yml` | OmniVoice |
| `fleet.yml` | Fleet SSOT - 291 lines, all services, machines, secrets |
| `Dockerfile` | Core Dockerfile |
| `mcp-server/` | MCP server Dockerfile |
| `migrations/` | SQL migrations |
| `neo4j/` | Neo4j Dockerfile + config |
| `qdrant/` | Qdrant Dockerfile |
| `nginx/` | Nginx config |
| `systemd/` | Systemd service units |
| `telegram/` | Telegram bot Dockerfile |
| `wacli/` | WhatsApp CLI Dockerfile |
| `whatsapp/` | WhatsApp config |
| `monitoring/` | Monitoring config |
| `observability/` | Observability config |
| `n8n-workflows/` | n8n workflow exports |
| `supabase/` | Supabase config |
| `freeswitch/` | FreeSWITCH config |

---

## 16. APPS (Layer 2)

**Path**: `/home/mystic/.../apps/` - 24 entries

| App | Purpose |
|-----|---------|
| `core/` | Core engine (planner, executors, agents) |
| `evolution/` | Auto-evolution, scorecard, learning |
| `hermes/` | Hermes Agent Gateway (full repo with tests) |
| `frontends/` | Frontend apps (sonora-web, app, platform) |
| `grimoire/` | Grimoire 3D portal |
| `monitor/` | Monitoring dashboard |
| `voice/` | Voice pipeline (TTS/STT) |
| `whatsapp/` | WhatsApp integration |
| `telegram_scheduler/` | Telegram scheduler |
| `instagram/` | Instagram integration |
| `tiktok/` | TikTok integration |
| `youtube/` | YouTube integration |
| `spotify/` | Spotify integration |
| `twilio-voice/` | Twilio voice |
| `voice-realtime/` | Real-time voice |
| `openclaw_edge/` | OpenClaw edge |
| `SIGNAL/` | Signal processing |
| `sonora_engine/` | Sonora Engine |
| `webui/` | Web UI |
| `stt/` | Speech-to-Text |
| `tts/` | Text-to-Speech |
| `jarvis-dashboard/` | JARVIS Dashboard |

---

## 17. PRODUCTS (Layer 3)

**Path**: `/home/mystic/.../products/` - 23 entries

| Product | Purpose |
|---------|---------|
| `clon-digital/` | Digital Clone (facial LoRA + voice clone) |
| `mystika/` | Mystika product (api, web, telegram-bot) |
| `agent-marketplace/` | Agent Marketplace |
| `nsfw-ai-studio/` | NSFW AI Studio |
| `production/` | Production services (omnivoice, content-studio, google-mcp, mystik) |
| `ce_son/` | CE Son |
| `sonora-client/` | Sonora Client |
| `client_api/` | Client API |
| `call-system/` | Call System |
| `voice-service/` | Voice Service |
| `marketing/` | Marketing tools |
| `social/` | Social tools |
| `catalog/` | Catalog |
| `order_tracker/` | Order Tracker |
| `affiliates/` | Affiliates |
| `archive/` | Archive |
| `cyber_diagnosis/` | Cyber Diagnosis |
| `notifier/` | Notifier |
| `web/` | Web products |
| `sdc/` | SDC products |

---

## 18. CLIENTS (Layer 4)

**Path**: `/home/mystic/.../clients/` - 5 clients

| Client | Contents |
|--------|----------|
| `Abe Music Group/` | Full stack: api, bot, hub (frontend+bots+mcp), studio (api+mock+webhook+worker), skills (5 skills: streams, booking, promotion, finance, releases), artists (javier-arvayo, hector-rubio, jesus-urquijo), agents (6), config, docker-compose |
| `Hermosillo Contability Corp./` | Accounting: agents (nathy_mcp_server), config (11 agent YAMLs), skills (7 skills + 6 use-cases), bot, requirements.txt |
| `Joyeria/` | Jewelry: config (cotizar, sales-joyeria, atender-cliente, catalogar-producto), skills (3 skills + 3 use-cases), opencode.json |
| `Cesar Delivery/` | Delivery: config.yaml, menu.json |
| `r1/` | Client r1 |

---

## 19. TENANTS

**Path**: `/home/mystic/.../tenants/` - Deployed tenant instances

| Tenant | Contents |
|--------|----------|
| `abe-music/` | Full ABE Music deployment (studio, hub, bot, web, skills, db, docker-compose) |
| `hermosillo-contabilidad/` | Full Nathy Conta deployment (config, skills, use-cases, web) |
| `Aztrotech/` | Aztrotech bot + infra + migrations |
| `hermosillo-contabilidad/` | Hermosillo Contabilidad Corp. |

---

## 20. CONFIGURATION (SSOT)

**Path**: `/home/mystic/.../config/` - 44 entries

| File | Purpose |
|------|---------|
| `tenants.json` | 6 tenants: sdc-core (enterprise), abe-fenix (pro), free, joyeria_el-joyero (basic), nathy-conta (pro) |
| `registry.json` | 8 capabilities + 16 skills + 36+ agents defined |
| `tenant-routing.yaml` | Phone number routing (Luis Daniel, Nathy) |
| `hermes-config.yaml` | Hermes configuration |
| `cost-rates.yaml` | Cost rates |
| `pricing-tiers.yaml` | Pricing tiers |
| `providers.json` | Provider configs |
| `plugins.json` | Plugin configs |
| `ambassadors.yaml` | Ambassador configs |
| `onboarding.yaml` | Onboarding flow |
| `schedule.json` | Schedule |
| `packages.yaml` | Package configs |
| `design-tokens.json` | Design tokens |
| `content-agenda.json` | Content agenda |
| `artists.json` | Artist configs |
| `clone-events.yaml` | Clone events |
| `client-signals.yaml` | Client signals |
| `whatsapp-product.yaml` | WhatsApp product |
| `sonora-redis.yml` | Redis config |
| `config.toml` | General config |
| `design-systems/` | Design systems (zamora, abe-music, sonoran-sunset) |
| `agents/` | Agent configs |
| `n8n-sdc/` | n8n SDC workflows |
| `n8n-workflows/` | n8n workflow exports |
| `n8n-zero-token/` | n8n zero-token configs |
| `n8n/` | n8n configs |
| `openclaw/` | OpenClaw configs |
| `secrets/` | Secrets (encrypted) |
| `wacli/` | WhatsApp CLI configs |
| `migrations/` | SQL migrations |
| `tenants/` | Per-tenant configs (abe-music, sonora-digital, nathy-conta, el-joyero, azrec, mds-corp, r1, _template) |

---

## 21. .env FILES

| Path | Purpose |
|------|---------|
| `.env.example` | Root template (56 lines) |
| `config/.env.example` | Config template |
| `config/secrets/.env.example` | Secrets template |
| `infra/.env.example` | Infra template |
| `infra/.env.backup` | Infra backup |
| `skills/infra/.env.example` | Skills infra |
| `clients/Abe Music Group/.env.example` | ABE Music |
| `products/clon-digital/.env.example` | Clone Digital |
| `products/mystika/telegram-bot/.env.example` | Mystika bot |
| `products/mystika/api/.env.example` | Mystika API |
| `products/mystika/web/.env.local` | Mystika web |
| `products/mystika/web/.env.production` | Mystika production |
| `apps/SIGNAL/.env.local.example` | SIGNAL |
| `apps/hermes/hermes-agent/.env.example` | Hermes Agent |
| `apps/frontends/app/.env.example` | Frontend app |
| `apps/frontends/platform/.env.example` | Platform |
| `tenants/Aztrotech/bot/.env.example` | Aztrotech bot |
| `tenants/abe-music/.env.example` | ABE tenant |
| `tenants/abe-music/hub/frontend/app/.env.local` | ABE hub frontend |
| `tenants/abe-music/hub/frontend/app/.env.local.example` | ABE hub template |

---

## 22. DOCS AND DOCUMENTATION

| Path | Content |
|------|---------|
| `BLUEPRINT.md` | Full architecture (594 lines) |
| `SDC-STATUS-COMPLETO.md` | System status (353 lines) |
| `CHANGELOG.md` | Changelog |
| `docs/MAPA-SDC.md` | SDC map |
| `docs/mcp-servers.json` | MCP servers catalog |
| `docs/planning/blueprint/` | Blueprint planning docs |
| `docs/specs/` | Specifications |
| `docs/process/` | Process documentation |
| `config/INCIDENT-RESPONSE.md` | Incident response |
| `config/coming-soon-script.md` | Coming soon script |
| `tests/quality/UNBREAKABLE-RULES.md` | Unbreakable rules |
| `skills/core-reference/AGENT-SPEC.md` | Agent spec reference |
| `skills/core-reference/SKILL-SPEC.md` | Skill spec reference |
| `skills/core-reference/AGENTS.md` | Agents reference |
| `skills/README.md` | Skills README |
| `adrs/` | Architecture Decision Records |

---

## 23. SKILL TEMPLATE

**Path**: `skills/SKILL-TEMPLATE.md` (183 lines)

Every skill must define 14 fields:
1. Business Objective
2. Inputs (Gherkin)
3. Outputs (Gherkin)
4. Events
5. Dependencies
6. Tools
7. Policies
8. Success Metrics
9. Failure Conditions
10. Recovery Procedure
11. Business Value
12. Parent OS
13. Version
14. Audit Trail

---

## SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| Top-level directories | 33 |
| Docker Compose files | 30 |
| Dockerfiles | 39 |
| Python MCP servers | 30+ |
| OpenCode agents | 20 |
| ADK agents (YAML) | 36+ |
| Client agents (YAML) | 15+ |
| Skills (directories) | 138 |
| Skill YAML files | 12+ |
| Feature files (Gherkin) | 80+ |
| SQL schema/migration files | 24 |
| .env files | 20 |
| opencode.json files | 11 |
| Test Python files | 100+ |
| Prompt files | 25+ |
| Active specs | 18 |
| Completed specs | 25+ |
| Kernel files | 30 |
| Config entries | 44 |
| Active tenants | 6 |
| Active clients | 5 |
</task_result>
</task>
```

**Tool: task**

**Input:**
```json
{
  "description": "Explore ops tenants configs",
  "prompt": "Explore these directories thoroughly and return ALL content:\n\n1. /home/mystic/Documentos/Sonora Digital Corp/ops/ - full tree and all files\n2. /home/mystic/Documentos/Sonora Digital Corp/tenants/ - full tree and all files\n3. /home/mystic/Documentos/Sonora Digital Corp/Prototipos/ - full tree and all files\n4. /home/mystic/Documentos/Sonora Digital Corp/Clientes/ - full tree and all files\n\nFor each directory:\n- Complete recursive file listing\n- Read ALL configuration files, JSON files, YAML files, Python files, shell scripts\n- Read any README or documentation files\n- List any database files (.db, .sqlite)\n\nReturn ALL findings in complete detail. Do NOT summarize or omit anything.",
  "subagent_type": "explore"
}
```

**Output:**
```
<task id="ses_037ad17ebffePTcV1nTjGYFs6T" state="completed">
<task_result>
I have now read all the key files across the four directories. Given the enormous volume of content (100+ files), let me compile the complete findings. Here is the exhaustive report:

---

# COMPLETE EXPLORATION REPORT

---

## 1. `/home/mystic/Documentos/Sonora Digital Corp/ops/`

### Complete File Tree

```
ops/
  state/
    skill-registry.json
    engram_aztrotech.db          (database file)
```

### Database Files

- `/home/mystic/Documentos/Sonora Digital Corp/ops/state/engram_aztrotech.db` -- SQLite database for Emerge Memory system (Aztrotech tenant)

### skill-registry.json (COMPLETE)

```json
{
  "version": "1.0",
  "updated": "2026-08-02T03:24:08.080959",
  "skills": {
    "hermes:autonomous-ai-agents": {
      "name": "autonomous-ai-agents",
      "source": "hermes",
      "description": "---\ndescription: Skills for spawning and orchestrating autonomous AI coding agents and multi-agent workflows",
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/autonomous-ai-agents/hermes-agent/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/autonomous-ai-agents/codex/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/autonomous-ai-agents/claude-code/SKILL.md"
      ],
      "type": "reference"
    },
    "hermes:devops": {
      "name": "devops",
      "source": "hermes",
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/devops/kanban-orchestrator/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/devops/kanban-worker/SKILL.md"
      ],
      "type": "reference"
    },
    "hermes:productivity": {
      "name": "productivity",
      "source": "hermes",
      "description": "Skills for document creation, presentations, spreadsheets, and other productivity workflows.",
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/productivity/nano-pdf/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/productivity/notion/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/productivity/maps/SKILL.md"
      ],
      "type": "reference"
    },
    "hermes:dogfood": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/dogfood/SKILL.md"] },
    "hermes:email": {
      "description": "Skills for sending, receiving, searching, and managing email from the terminal.",
      "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/email/himalaya/SKILL.md"]
    },
    "hermes:software-development": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/software-development/plan/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/software-development/hermes-agent-skill-authoring/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/software-development/spike/SKILL.md"
      ]
    },
    "hermes:data-science": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/data-science/jupyter-live-kernel/SKILL.md"] },
    "hermes:smart-home": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/smart-home/openhue/SKILL.md"] },
    "hermes:social-media": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/social-media/xurl/SKILL.md"] },
    "hermes:note-taking": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/note-taking/obsidian/SKILL.md"] },
    "hermes:github": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/github/github-pr-workflow/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/github/codebase-inspection/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/github/github-issues/SKILL.md"
      ]
    },
    "hermes:index-cache": { "skill_files": [] },
    "hermes:mlops": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/mlops/inference/vllm/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/mlops/inference/llama-cpp/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/mlops/huggingface-hub/SKILL.md"
      ]
    },
    "hermes:yuanbao": { "skill_files": ["/home/mystic/.hermes/hermes-agent/skills/yuanbao/SKILL.md"] },
    "hermes:media": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/media/heartmula/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/media/gif-search/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/media/songsee/SKILL.md"
      ]
    },
    "hermes:research": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/research/research-paper-writing/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/research/blogwatcher/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/research/arxiv/SKILL.md"
      ]
    },
    "hermes:apple": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/apple/apple-notes/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/apple/macos-computer-use/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/apple/apple-reminders/SKILL.md"
      ]
    },
    "hermes:creative": {
      "skill_files": [
        "/home/mystic/.hermes/hermes-agent/skills/creative/manim-video/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/creative/pretext/SKILL.md",
        "/home/mystic/.hermes/hermes-agent/skills/creative/baoyu-infographic/SKILL.md"
      ]
    }
  }
}
```

---

## 2. `/home/mystic/Documentos/Sonora Digital Corp/tenants/`

### Complete File Tree

```
tenants/
  demo-client/
    config.yaml
  demo_client/
    .env
    config.yaml
    sdc-bot.service
```

### tenants/demo-client/config.yaml (COMPLETE)

```yaml
channels:
  telegram:
    bot_token: TEST_TOKEN
    enabled: true
    owner_chat_id: '12345'
  whatsapp:
    enabled: false
    provider: wacli
company: Demo Client
default_model: deepseek/deepseek-v4-flash
display_name: Demo Client
language: es
max_tokens: 4096
models:
  default: deepseek/deepseek-v4-flash
  embeddings:
    model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    provider: fastembed
  premium: moonshotai/kimi-k2.7-code
  reasoning: z-ai/glm-5.2
openrouter:
  base_url: https://openrouter.ai/api/v1
  max_retries: 3
  timeout: 30
owner: Juan Perez
rag:
  chunk_overlap: 64
  chunk_size: 512
  min_score: 0.65
  top_k: 5
tenant_id: demo-client
timezone: America/Mexico_City
voice:
  stt:
    language: es
    model: small
    provider: faster-whisper
  tts:
    provider: edge-tts
    voice: es-MX-DaliaNeural
white_label:
  domain: ''
  mode: platform
  pricing:
    description: Bot en infra compartida de SDC (Telegram/WhatsApp/Web)
    implementation: 75000
    includes:
    - Bot Telegram/WhatsApp en dominio SDC
    - RAG compartido (Qdrant)
    - Postgres compartido (schema separado)
    - TTS/STT compartido (edge-tts + whisper)
    - Soporte estandar
    - Actualizaciones incluidas
    limits:
      agents: 2
      channels: [telegram, whatsapp]
      conversations_month: 5000
      rag_docs: 50
      voice: true
    monthly: 25000
    name: Plataforma SDC
  provisioned_at: '2026-08-02T03:46:49.073160'
```

### tenants/demo_client/.env (COMPLETE)

```
# Demo Client - White Label Environment
TENANT_ID=demo_client
OPENROUTER_API_KEY=[REDACTED]
TELEGRAM_BOT_TOKEN=TEST_TOKEN
OWNER_CHAT_ID=12345
```

### tenants/demo_client/sdc-bot.service (COMPLETE)

```ini
[Unit]
Description=Demo Client Bot - White Label
After=network.target

[Service]
Type=simple
User=mystic
WorkingDirectory=/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tenants/demo_client/bot
Environment="OPENROUTER_API_KEY=[REDACTED]"
Environment="TENANT_ID=demo_client"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/sdc/demo_client-bot.log
StandardError=append:/var/log/sdc/demo_client-bot-error.log

[Install]
WantedBy=multi-user.target
```

### tenants/demo_client/config.yaml (COMPLETE)

Identical to `demo-client/config.yaml` but with `tenant_id: demo_client` and `provisioned_at: '2026-08-02T03:47:11.739989'`.

---

## 3. `/home/mystic/Documentos/Sonora Digital Corp/Prototipos/`

### Complete File Tree

**This directory is EMPTY. No files or subdirectories found.**

---

## 4. `/home/mystic/Documentos/Sonora Digital Corp/Clientes/`

### Top-Level Subdirectories

```
Clientes/
  Fourgea Mexico/
    Fourgea_IA_Estrategia_v2_Completo.docx     (binary - Word doc)
    Fourgea_AgentTeams_ModeloNegocio_v3.docx   (binary - Word doc)
    Invoice-BKUCFSKM-0001.pdf                  (binary - PDF)

  ABE Music Group/
    (see full tree below)

  Aztrotech/
    (see full tree below)
```

---

### 4A. `Clientes/Fourgea Mexico/`

Binary files only (2 Word documents + 1 PDF). Not readable as text.

---

### 4B. `Clientes/ABE Music Group/` -- COMPLETE FILE TREE

```
ABE Music Group/
  docs/
    config.yml
    ABE-EXPANSION.md
  tenant/
    .env.example
    CLAUDE.md
    onboard-artist.sh
    weekly-report.py
    index.html
    javier-arvayo.html
    hector-rubio.html
    jesus-urquijo.html
    config/
      config.yaml
      mcp.yaml
      tools.yaml
      policies.yaml
      prompt.md
      branding/
        branding.json
      skills/
        booking-flow.md
    db/
      008_abe_music_hub.sql
    api/
      __init__.py
      main.py
      main.py.bak
      config.py
      database.py
      models.py
      seed.py
      start.sh
      requirements.txt
      api.log
      api/
        __init__.py
        middleware.py
        rest.py
        ws.py
      avatar/
        index.html
        manager.js
      bridges/
        __init__.py
        collectors.py
        engram.py
        mcp.py
        neo4j.py
        openclaw.py
        stt.py
        tts.py
      core/
        __init__.py
        abe_service.py
        chat_engine.py
        contract_engine.py
        crm.py
        distribution.py
        rag_engine.py
        revenue_ledger.py
        sync_engine.py
        voice_pipeline.py
      models/
        __init__.py
        artists.py
        auth.py
        contact.py
        dashboard.py
        health.py
        services.py
      pwa/
        app.js
        estado.html
        icon-192.svg
        icon-512.svg
        index.html
        manifest.json
        style.css
      routes/
        __init__.py
        admin.py
        ai.py
        artists.py
        auth.py
        contact.py
        dashboard.py
        health.py
        services.py
        stats.py
        track.py
      services/
        __init__.py
        auth.py
        scraper_pipeline.py
        storage.py
      web/
        api.html
        hector-rubio.html
        index.html
        javier-arvayo.html
        jesus-urquijo.html
    hub/
      README.md
      abe-studio-deck.html
      docker-compose.yml
      index.html
      frontend/
        dashboard.html
        index.html
        app/
          package.json
          package-lock.json
          tsconfig.json
          tailwind.config.ts
          next.config.ts
          next-env.d.ts
          postcss.config.mjs
          vercel.json
          middleware.ts
          .env.local
          .env.local.example
          app/
            globals.css
            layout.tsx
            page.tsx
            login/
              page.tsx
              LoginForm.tsx
            dashboard/
              layout.tsx
              page.tsx
            api/auth/
              login/route.ts
              logout/route.ts
          components/
            KPICard.tsx
            Sidebar.tsx
            StatRow.tsx
          lib/
            api.ts
            auth.ts
          studio/
            page.tsx
      bots/
        package.json
        tsconfig.json
        Dockerfile
        abe-music-bot.ts
      mcp/
        package-lock.json
        tsconfig.json
        .gitignore
        src/
          index.ts
        dist/
          index.js
          index.d.ts
      infra/
        migrations/
          008_abe_music_hub.sql
    skills/
      README.md
      manifest.yaml
      prompts/
        booking-agent.md
        executive-agent.md
        marketing-agent.md
      agents/
        booking-agent.yaml
        executive-agent.yaml
        marketing-agent.yaml
      skills/
        booking/
          skill.py
          skill.yaml
        finance/
          skill.py
          skill.yaml
        promotion/
          skill.py
          skill.yaml
        releases/
          skill.py
          skill.yaml
        streams/
          skill.py
          skill.yaml
      dashboard/
        lovable-prompt.md
      tests/features/
        booking.feature
        finance.feature
        promotion.feature
        releases.feature
        streams.feature
    studio/
      spec.md
      schema.sql
      docker-compose.yml
      docker-compose.test.yml
      api/
        requirements.txt
        Dockerfile
        app/
          main.py
          config.py
          db.py
          models.py
          services/
            seedance.py
            storage.py
          routes/
            generate.py
            poll.py
            tasks.py
            usage.py
            webhook.py
      mock/
        requirements.txt
        Dockerfile
        app/main.py
      webhook/
        requirements.txt
        Dockerfile
        app/main.py
      worker/
        Dockerfile
        app/
          config.py
          main.py
      __tests__/
        test_mock.py
        test_integration.py
        run_all.py
      studio/ (nested duplicate)
        spec.md
        schema.sql
        docker-compose.yml
        docker-compose.test.yml
        api/...
        mock/...
        webhook/...
        worker/...
        __tests__/...
    web/
      static/
        dashboard.html
        index.html
        studio.html
```

---

### 4C. `Clientes/Aztrotech/` -- COMPLETE FILE TREE

```
Aztrotech/
  docs/
    prompt.md
    pricing-plan.md
    checklist-arquitectura.md
    config.yaml
  whatsapp/
    config.yaml
    wacli_stdio.py
  openclaw/
    docker-compose.vps.yml
  audiovisuales/
    presentacion-cesar.pdf       (binary)
    presentacion-cesar.html
    presentacion-logros.html
  web/
    web/
      server.py
      static/
        index.html
  telegram-bot/
    bot/
      .env.example
      requirements.txt
      main.py
      router.py
      prompt_builder.py
      conversation_engine.py
      emerge_memory.py
      emotion_analyzer.py
      lead_classifier.py
      rag_retriever.py
      identity_resolver.py
      persistence.py
      token_tracker.py
      test_engine_e2e.py
      handlers/
        __init__.py
        telegram.py
      models/
        identity.py
      migrations/
        001_mvp_identity_conversations.sql
      prompts/
        lead_classifier_fewshot.yaml
```

---

### DATABASE FILES FOUND (across workspace)

| Path | Type |
|------|------|
| `/home/mystic/Documentos/Sonora Digital Corp/ops/state/engram_aztrotech.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/execution/queue.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/engram_astrotech.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/engram_aztrotech.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/social_schedule.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/data/cost_tracker.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/memory/00-working.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/memory/01-project.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/memory/02-organization.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/economics.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/social_sessions.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/apps/hermes/hermes-agent/sqlite_mcp_server.db` | SQLite |
| `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/apps/telegram_scheduler/telegram_scheduler.db` | SQLite |

---

### KEY FILE CONTENTS -- ABE Music Group

**docs/config.yml** -- ABE Music configuration: client=abe-music, owner=Abraham Ortega, language=es, timezone=America/Hermosillo, artists: Hector Rubio, Jesus Urquijo, Javier Arvayo. Revenue split: 70% artist, 20% label, 10% reserve.

**docs/ABE-EXPANSION.md** -- 316-line expansion plan covering ABE Films (AI video content), ABE Records (AI music production), ABE IA Services (digital clones, fan CRM, content factory). Architecture diagram, revenue model, pricing tiers ($300-$5,000/mo), projection: $804,000 new revenue in Year 1.

**tenant/CLAUDE.md** -- 191-line project instructions for Claude Code. Backend: HERMES OS API at localhost:8000. Frontend: Next.js 15. Bot: Telegraf. Stack: PostgreSQL, Redis, Qdrant, FastAPI. 20+ hub services. $RESO gamification token. Plans: Basico $99, Pro $299, Elite $999 MXN/mo.

**tenant/config/config.yaml** -- tenant_id: abe-music, model: claude-3.5-sonnet, qdrant_collection: tenant_abe_music_memory, neo4j_database: abe_music

**tenant/config/mcp.yaml** -- MCP servers: calendar (Google), crm (HTTP), telegram (local)

**tenant/config/tools.yaml** -- Allowed: telegram_send_message, calendar_create_event, crm_create_lead, web_search, knowledge_base_query, music_analytics_query, booking_lookup, studio_schedule, contact_form_submit. Blocked: github_create_issue, vps_execute_command, internal_billing_access, social_publish.

**tenant/config/policies.yaml** -- Prompt injection protection enabled, rate limits: 60/min telegram, 500/hr API. PII auto-redact for credit_card and password. Tool sandbox enabled.

**tenant/config/prompt.md** -- System prompt: "Eres ABE Music AI." Manages artists, booking, studio sessions, promotions. Never reveals Sonora Digital Corp.

**tenant/config/branding/branding.json** -- primary_color: #FF6B35, tone: creative, language: es

**tenant/config/skills/booking-flow.md** -- Booking agent flow: check availability, review technical requirements, propose date, generate contract, follow-up.

**tenant/.env.example** -- Environment template: HERMES_API_URL, ABE_MUSIC_BOT_TOKEN, STRIPE keys, NEXT_PUBLIC vars, ABRAHAM_CHAT_ID.

**tenant/db/008_abe_music_hub.sql** -- 187-line SQL migration creating: hub_services, hub_bookings, token_ledger ($RESO), v_token_balance view, vr_sessions, hub_suscripciones tables with RLS policies and triggers.

**tenant/api/main.py** -- FastAPI app "ABE Music OS" v1.0.0 with CORS, REST router, WebSocket, mounts: /pwa, /avatar, /web. Port 5180.

**tenant/api/config.py** -- ABEConfig class reading from env vars and JSON config. Properties: name, tenant_id, jwt_secret, mcp_gateway_url, qdrant_url, ws_port (5180), royalty_split defaults (70/20/10 streaming).

**tenant/api/database.py** -- SQLAlchemy setup using ABE_DATABASE_URL env var. SessionLocal + query_db helper.

**tenant/onboard-artist.sh** -- 141-line bash script for artist onboarding: creates JSON data entry, generates landing page HTML, deploys to VPS (149.56.46.173), sends Telegram notification.

**tenant/weekly-report.py** -- 108-line Python script for automated weekly KPI report via Telegram. Fetches from localhost:8080 API, formats artist stats, sends to Abraham's chat.

---

### KEY FILE CONTENTS -- Aztrotech

**docs/config.yaml** -- tenant_id: astrotech, owner: Cesar Holguin, models: deepseek/glm-5.2/kimi-k2.7-code, voice: faster-whisper + edge-tts (es-MX-DaliaNeural), rate_limiting by package (despertar/elevar/soberano/oraculo).

**docs/prompt.md** -- System prompt template with {{DISPLAY_NAME}}, {{COMPANY_NAME}}, {{OWNER_NAME}} placeholders. Anti-SDC-reveal rules.

**docs/pricing-plan.md** -- 145-line pricing document. Plans: Despertar ($299 MXN/mo), Elevar ($1,499 MXN/mo), Soberano ($50,000+ MXN/mo), Oraculo (custom). Partner tiers: Visionario ($150K), Arquitecto ($500K), Guardian ($1.5M). Real costs: <$0.05/call.

**docs/checklist-arquitectura.md** -- 176-line architecture checklist. Active MCPs: OpenClaw(:18789), Sonora MCP(:18989), Hermes(:8000), PostgreSQL, Redis, Neo4j, Qdrant, n8n, Twilio Voice(:8700), FreeSWITCH(:5060). Pending: Agent Control MCP, Evolution Engine MCP, Infra MCP, Twilio tenant routing.

**whatsapp/config.yaml** -- Same as docs/config.yaml (duplicate).

**whatsapp/wacli_stdio.py** -- 191-line FastMCP server for WhatsApp messaging via wacli CLI. Tools: check_status, send_text, send_file, send_voice (with MP3-to-OGG conversion), get_contacts, create_wa_me_link, create_qr.

**openclaw/docker-compose.vps.yml** -- 104-line Docker Compose VPS override. Services: postgres, redis, neo4j, qdrant, mcp-server, n8n, telegram-bot, langfuse, openclaw, hermes. All with shared environment variables.

**web/web/server.py** -- 90-line FastAPI server "AstroTech AI - Mysticgrimoire". POST /api/chat routes to OpenRouter (deepseek/glm/kimi). System prompt: Cesar Holguin's assistant, never reveals SDC, never gives prices.

**web/web/static/index.html** -- 231-line single-page chat interface with Three.js particle background, microphone support (Web Speech API), speech synthesis, dark theme (#080c18), cyan/purple accent colors.

**telegram-bot/bot/main.py** -- Bot entry point. Loads config, creates ModelRouter, creates ConversationEngine (RAG-first), registers handlers for text, voice, callbacks.

**telegram-bot/bot/router.py** -- ModelRouter with pattern-based model selection (reasoning patterns -> glm-5.2, premium patterns -> kimi-k2.7-code). Fallback chain. Rate limiting by package.

**telegram-bot/bot/prompt_builder.py** -- 177-line prompt construction with guardrails: anti-price-reveal, anti-SDC-reveal, anti-aggressive-tone. Builds system prompt with RAG context, memory, emotion, lead classification, history.

**telegram-bot/bot/conversation_engine.py** -- 359-line orchestrator: 10-step pipeline per message (identity -> memory -> RAG -> emotion -> classify -> prompt -> LLM -> guardrails -> persist -> notify).

**telegram-bot/bot/emerge_memory.py** -- 380-line multi-layer memory system (7 layers: working/task/project/customer/business/historical/strategic). SQLite-based. Auto-promotion logic with inactivity and action detection.

**telegram-bot/bot/emotion_analyzer.py** -- 262-line multi-language emotion analysis. Lexicon-based for es/en/pt/fr. LLM fallback for ambiguous cases. Emotions: frustration, urgency, genuine interest, price objection, buying signal, joy, doubt.

**telegram-bot/bot/lead_classifier.py** -- 324-line hybrid lead classifier. Rules-first (deterministic), LLM few-shot for ambiguous. Output: cold/warm/hot with confidence, reasons, next action, missing data.

**telegram-bot/bot/rag_retriever.py** -- 166-line RAG retriever using FastEmbed (paraphrase-multilingual-MiniLM-L12-v2, 384-dim) + Qdrant. Tenant-filtered search with score threshold.

**telegram-bot/bot/identity_resolver.py** -- 329-line cross-channel identity resolver (WhatsApp/Telegram/Web -> unified internal user). Merge logic by phone/email match. Uses asyncpg + PostgreSQL.

**telegram-bot/bot/persistence.py** -- 257-line dual persistence writer (Postgres + Engram SQLite). Async batched writes. Stores messages, conversations, daily metrics, emerge memories.

**telegram-bot/bot/token_tracker.py** -- 104-line token cost tracker. Pricing: deepseek $0.14/M, glm-5.2 $0.50/M, kimi-k2.7 $1.00/M. Daily budget: $5 USD.

**telegram-bot/bot/handlers/telegram.py** -- 528-line Telegram handler. Pattern-matched responses for greetings, services, pricing objections, human contact, voice mode. RAG-first engine integration with fallback to simple mode. Voice messages via STT. Lead notifications to Cesar.

**telegram-bot/bot/models/identity.py** -- 86-line Pydantic models: Platform enum (WHATSAPP/TELEGRAM/WEB), LeadType (COLD/WARM/HOT), InternalUser, IdentityResolutionResult, IdentityRow.

**telegram-bot/bot/migrations/001_mvp_identity_conversations.sql** -- 105-line SQL migration creating: user_identities, conversations, messages (with token/emotion/RAG tracking), daily_metrics, emerge_promotions tables.

**telegram-bot/bot/prompts/lead_classifier_fewshot.yaml** -- 10 few-shot examples for lead classification (cold/warm/hot).

**telegram-bot/bot/requirements.txt** -- python-telegram-bot>=20.0, httpx>=0.25, pyyaml>=6.0, numpy>=1.24, speechrecognition>=3.10.

---

This completes the exhaustive exploration of all four directories. The `Prototipos/` directory is empty. All other directories contain extensive multi-tenant AI platform infrastructure for Sonora Digital Corp's clients (ABE Music Group, Aztrotech, Fourgea Mexico) and a demo tenant configuration.
</task_result>
</task>
```

**Tool: task**

**Input:**
```json
{
  "description": "Explore session files and docs",
  "prompt": "Read and analyze these files in /home/mystic/Documentos/Sonora Digital Corp/:\n\n1. All session files: session-ses_03b6.md, session-ses_045c.md, session-ses_04ae.md, session-ses_04cccc.md\n2. All .odt reference files in /home/mystic/Documentos/Sonora Digital Corp/Referencia/ (read them if possible)\n3. The file \"prompt kimi.txt\" in Referencia/\n\nAlso check:\n- Is there a .git directory anywhere?\n- Any .opencode directory?\n- Any .github directory?\n- Any docker/ directory?\n- Any systemd service files?\n- Any cron configurations?\n\nReturn ALL findings in complete detail.",
  "subagent_type": "explore"
}
```

**Output:**
```
<task id="ses_037ad0e6effe7fNIoDqkc4SuAf" state="completed">
<task_result>
Here is the complete analysis of all files and directory checks in `/home/mystic/Documentos/Sonora Digital Corp/`.

---

## 1. SESSION FILES ANALYSIS

### session-ses_03b6.md (2843+ lines)
- **Path:** `/home/mystic/Documentos/Sonora Digital Corp/session-ses_03b6.md`
- **Session ID:** ses_03b612944fferaI8htvZf63rnt
- **Created:** 8/2/2026, 3:36 PM
- **Updated:** 8/3/2026, 1:08 AM
- **AI Model:** MiMo V2.5 (Build mode)
- **Topic:** "Verificar estado de PC lenta" -- despite the title, this session is entirely about building and iterating the **Aztrotech voice assistant** for client Cesar Holguin
- **Key Activities:**
  - Built a guided booking flow with auto-greeting, step-by-step data collection (name, company, service, phone, email, date/time)
  - Modified `server.py` and `dist/index.html` for the voice assistant at `tenants/Aztrotech/web/voice-app/`
  - Added WhatsApp confirmation messages and Telegram notifications via the "Mystic channel"
  - Saved leads to PostgreSQL `leads` table with fields: phone, name, source, lead_score, lead_type, notes
  - Sent a quantum-physics-themed voice message to Cesar via wacli (WhatsApp CLI) and Telegram
  - Fixed TTS server by adding full path for edge-tts (systemd PATH issue)
  - Configured dual Telegram bot system: @AztroTechBot (conversation) + @MysticUnity_bot (notifications)
  - Generated 6 voice test samples (saludo, servicios, objecion, lead-hot, lead-warm, lead-cold)
  - Ran lead classifier tests (6/6 correct: cold/warm/hot classification)
  - Inserted 30 test leads (10 cold, 10 warm, 13 hot) into PostgreSQL
  - Created Gherkin test features: lead_classification (32 scenarios), voice_pipeline (11), conversation_flow (28), notification_system (21) = 92 total
  - Fixed Gherkin parser (stripped whitespace before matching "Scenario:")
  - All tests passed: conversation flow, lead classification, voice pipeline, notifications
  - Git commits pushed to `https://github.com/sonoradigitalcorp-H/Sonora-Digital-Corp.git`
  - Systemd services: sdc-aztrotech-bot, sdc-aztrotech-tts, sdc-aztrotech-notif, sdc-aztrotech-voice, sdc-aztrotech-dashboard, sdc-n8n-bridge

### session-ses_045c.md (1035+ lines)
- **Path:** `/home/mystic/Documentos/Sonora Digital Corp/session-ses_045c.md`
- **Session ID:** ses_045ced021ffeGqzlddrM10RjgB
- **Created:** 7/31/2026, 3:00 PM
- **Updated:** 8/1/2026, 11:44 AM
- **AI Model:** Ling-3.0-flash Free (Build mode)
- **Topic:** "Blueprint y arquitectura en arbol del proyecto"
- **Key Activities:**
  - Full directory tree exploration of the Sonora Digital Corp workspace
  - Mapped complete project structure including:
    - Top-level: Audiovisuales/, Clientes/, Finanzas/, Prototipos/, Referencia/, sonora-digital-corp/
    - Core project: `sonora-digital-corp/` with tenants (Aztrotech, hermosillo-contabilidad), apps (frontends/agentic-os, hermes/hermes-agent), skills (calendar, crm, marketing, rag, realtime-voice, voice), tests (gherkin, unit, integration, e2e, promptfoo), scripts, infra, config, ops
    - Tenants: Aztrotech (voice-app, bot, skills, comercial, knowledge, tts-server, voice-clone), hermosillo-contabilidad (nathy bot, MCP server, accounting skills: cfdi-timbrado, conciliacion-bancaria, contpaq-polizas, nominas, resico-calculo, sat-declaraciones)
  - Referencia folder contains 12 .odt files and 1 .txt file (prompt kimi.txt)
  - Finanzas/ contains invoices, nomina, SAT-FIEL certificates

### session-ses_04ae.md (1703+ lines)
- **Path:** `/home/mystic/Documentos/Sonora Digital Corp/session-ses_04ae.md`
- **Session ID:** ses_04ae3aacbffeE4rB6EFLpy4y9o
- **Created:** 7/30/2026, 3:19 PM
- **Updated:** 7/30/2026, 3:24 PM
- **AI Model:** DeepSeek V4 Flash (Build mode)
- **Topic:** "No veo carpeta de aztrotech en clientes"
- **Key Activities:**
  - Discovered Aztrotech was missing from Clientes/ (only existed in Audio Visuales/)
  - Found duplicate folders: "Audio Visuales/" and "Audiovisuales/"
  - Created `Clientes/Aztrotech/` with standard subfolders: landing-page, telegram-bot, openclaw, whatsapp, web, audiovisuales
  - Merged Audio Visuales/ into Audiovisuales/ (combined 10+18 files from Sonora Digital Corp folders)
  - Deleted the empty Audio Visuales/ directory
  - Final state: Clientes/ now has 6 clients (Aztrotech, Conrado, Fourgea Mexico, Milenius Construcasa, Solutech Intercomm, Sonora Digital Corp)

### session-ses_04cccc.md (2297+ lines)
- **Path:** `/home/mystic/Documentos/Sonora Digital Corp/session-ses_04cccc.md`
- **Session ID:** ses_045ced021ffeGqzlddrM10RjgB (same as ses_045c -- appears to be a continuation/variant)
- **Created:** 7/31/2026, 3:00 PM
- **Updated:** 8/2/2026, 3:50 AM
- **AI Model:** MiMo V2.5 (Build mode)
- **Topic:** Continuation of system building -- TTS fix, notification bot, testing
- **Key Activities:**
  - Fixed TTS server: edge-tts was not found in systemd PATH; added full path `/home/mystic/.local/bin/edge-tts`
  - Committed fix to GitHub: `2e8505f fix: TTS server full path para edge-tts`
  - Configured @MysticUnity_bot notification bot with valid token `8851813996:AAHwuIwhMlI0GW3FKFQGqcjKXgwI2QpXLK8`
  - Created systemd service `sdc-aztrotech-notif.service` and enabled it
  - Updated AGENTS.md with dual bot configuration
  - System status report showing all services active:
    - PostgreSQL: 3 users, 2 leads, 3 conversations, 20 messages
    - Qdrant: 3 collections, 16 points
    - Redis: PONG
    - Engram: 41 memories (later 18)
    - Voice pipeline: OK
    - n8n bridge: OK
    - OpenClaw: OFFLINE (only service not running)
  - Docker containers running: postgres-1, qdrant-1, redis-1, n8n-1 (all Up 30h)
  - Generated 6 voice test samples and sent to Cesar via Telegram
  - Lead classifier: 6/6 correct (cold/warm/hot)
  - Created comprehensive Gherkin test suite (92 scenarios across 4 feature files)
  - All tests passed with 100% pass rate

---

## 2. REFERENCE FILES (.odt)

The following .odt files are in `/home/mystic/Documentos/Sonora Digital Corp/Referencia/`:

### SONORA_DIGITAL_CORP_ v3 16 marzo.odt (435 lines)
- Master Technical Plan + Terminal Orders
- Version 2.0, March 2026, Hermosillo, Sonora
- Describes: web + mobile + desktop accounting system with AI for Mexican PyMEs
- Architecture: PostgreSQL 16 + pgvector, FastAPI (Python 3.11), Next.js 14, Expo (React Native), Tauri (desktop)
- Lists problems with Qwen's work (soul_filter_369.py always returns True, missing modules, no real DB, no frontend, no Docker, no CI/CD, no real RAG, no WhatsApp, no CFDI 4.0)
- Provides solutions: Docker Compose, JWT auth, Alembic migrations, ChromaDB for RAG, n8n orchestration, Nginx with SSL, GitHub Actions CI/CD, Expo mobile app

### coniguracion qween ultima 29 marzo.odt (3856 lines)
- Comprehensive system configuration document
- Covers: Vision General, Architecture of Agents, MCP Ecosystem, OpenCode Configuration, Telegram Bot fixes, Clawdbot v3.24 updates, Parallel Agents orchestration, Self-improvement, Security, Implementation Roadmap, Pre-production Checklist
- Metrics table: API dependency 60%->20%, Telegram response 5-15s-><2s, Parallel tasks 1->4-8, Accuracy 75%->95%, Monthly AI cost $90->$15
- Multi-level agent architecture: Clawdbot (CEO), Orchestrator, Specialized Agents

### deepseek abe music.odt (4473 lines)
- ABE Music Inc blueprint for Sonora Digital Corp
- Detailed auto-graded task system and certification smart contract
- Modules: Sound Fundamentals, Rhythmic Bases, Mixing/Mastering, Music Production with AI, Marketing Digital, NFTs/Web3, MDS Installer/Driver/Admin
- Auto-grading methods: validation scripts, AI grading (GPT-4o-mini), on-chain verification, peer review
- 80% passing threshold, 2 attempts allowed

### deploy sonora.sh.odt (58 lines)
- Bash deploy script for Sonora Digital Corp OS
- Target: VPS Hostinger with Ubuntu 22.04
- Installs: docker.io, docker-compose, nginx, certbot, fail2ban, ufw, wireguard, postgresql-client, redis-tools
- Security: UFW firewall, Fail2ban, SSH hardening

### hostingerR.odt (credentials)
- Contains Hostinger credentials (OCB, passwords, root access info)
- **SENSITIVE DATA** - contains plaintext passwords and access tokens

### hostinguer api.odt (1 line)
- Contains Hostinger API key: `UZEpliovfvso1ZTX6NkNqQ6fCVQdFAqz78waKeY50650eae0`
- **SENSITIVE DATA**

### psw.odt (1 line)
- Contains a password string: `39ltVpri93rT2feDpegwS0MT4zR_6txsMDby51bidpLgbP6Fh`
- **SENSITIVE DATA**

### recuperacion mys.odt
- Error: not well-formed XML -- appears corrupted or contains non-ODT content

### untitled_0.odt (143 lines)
- Telegram bot token: `8408996016:AAH0wcrs812ilxrdInIaFoCrB9kyqOy0OTc`
- Full Python bot code for "Bazar de Acordeones HMO" -- a rules-based Telegram bot with SQLite database
- **SENSITIVE DATA** - contains bot token in plaintext

### untitled_0_1.odt (1 line)
- Client info: "Antonio romero, 6622255784. albanil vive en la 12. crear clon digital, para novia acompanamiento, joven contexto delgada, Yatziri Alondra Martinez Luque. Cliente para barber"

### untitled_1.odt (12282 lines)
- Massive document about Sonora Token / Sonora Digital Corp Artist platform
- Covers 20 dimensions: Legal framework, visual identity, blockchain infrastructure, NFT packages, visualization platform, AI agents (10 types), business model, tokenomics, marketplace, anti-piracy, community/FOMO, territory expansion, roadmap, video games, security, educational material, marketing, finance, artist panel, fan panel
- This is the conceptual blueprint for a Web3 music platform

### untitled_2.odt
- Mission statement for Sonora Digital Corp
- 90-95% open source stack, VPS Hostinger, Claude Code development
- Multi-agent specialized system, ethical Wiccan-humanist principles
- Clients: Fourgea Mexico + Triple R
- Acknowledgments to Moonshot AI, open source community, FacturaScripts, Odoo, WordPress, Hostinger

---

## 3. prompt kimi.txt (950 lines)
- **Path:** `/home/mystic/Documentos/Sonora Digital Corp/Referencia/prompt kimi.txt`
- **Content:** A conversation with Kimi AI (Moonshot AI's Kimi K2.5) that generated the "Soul Prompt" for Sonora Digital Corp
- Key sections:
  - 10-point framework for eliminating project ambiguity
  - Kimi's self-description: 128K token context, web search, Python sandbox, memory space
  - Known limitations: hallucinations, limited context, no local file access
  - **Prometheus Orchestrator Soul Prompt** with 7-layer architecture:
    - Layer 7: Soul Principal (ethical filter)
    - Layer 6: Dedicacion Emocional (Hermes + Nathaly)
    - Layer 5: Mision Social
    - Layer 4: Mente Maestra
    - Layer 3: Orquestador
    - Layer 2: Prime Engineer
    - Layer 1: Specialized Agents (Contable-RAG, Legal-RAG, DevOps-OSS, UX-Educativa, Business-Local)
  - Soul Filter implementation in Python
  - Blueprint with 20 points across 4 phases (Cimientos -> Primeros Clientes -> Escala Etica -> Legado)
  - Special mode activation commands
  - Final oath/juramento

---

## 4. DIRECTORY CHECKS

### .git directory
- **FOUND:** `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.git`
- Active git repository with remote: `https://github.com/sonoradigitalcorp-H/Sonora-Digital-Corp.git`
- Branch: main
- Last commit: `3ab137f feat: Bot notificaciones @MysticUnity_bot activo`
- Has git hooks, packed-refs, and a full objects directory (260 subdirectories)
- No .git directory exists in the parent workspace folder (only in sonora-digital-corp/)

### .opencode directory
- **FOUND:** `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.opencode/`
- Contains: opencode.json, package.json, package-lock.json, .gitignore, agents/, skills/
- Also found at: `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/tenants/Aztrotech/.opencode/` (with node_modules including zod library)

### .github directory
- **FOUND:** `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/.github/`
- Contains: dependabot.yml, PULL_REQUEST_TEMPLATE.md, hooks/, workflows/

### docker/ directory
- **NOT FOUND** as a standalone directory
- Docker-related files exist in:
  - `/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/apps/hermes/hermes-agent/docker/` (28 files -- entrypoint.sh, main-wrapper.sh, SOUL.md, s6 service definitions)
  - Docker Compose files in tenants: `tenants/Aztrotech/infra/docker-compose.yml`
  - Docker containers are running (postgres-1, qdrant-1, redis-1, n8n-1 per session logs)

### systemd service files
- **FOUND:** 6 active SDC services in `/etc/systemd/system/`:
  1. `sdc-aztrotech-bot.service` -- Main Telegram conversation bot
  2. `sdc-aztrotech-dashboard.service` -- Dashboard
  3. `sdc-aztrotech-notif.service` -- @MysticUnity_bot notifications
  4. `sdc-aztrotech-tts.service` -- TTS server (DaliaNeural)
  5. `sdc-aztrotech-voice.service` -- Voice assistant (port 8770)
  6. `sdc-n8n-bridge.service` -- n8n workflow bridge
- Additional .service files found in project:
  - `sonora-affiliates.service`, `sonora-client-api.service`, `ce-son-api.service`, `sonora-tracker.service`, `comfyui.service`, `whatsapp-r1-webhook.service`, `engram-obsidian-export.service`, `omnivoice-agent.service`, `sdc-ws-bridge.service`, `telegram-scheduler.service`, `sonora-notifier.service`, `sdc-twilio-voice.service`, `sdc-observer.service`, `sdc-event-listener.service`, `whatsapp-responder.service`, `whatsapp-r1-responder.service`, `sonora-adk.service`, `sonora-evolution.service`, `whatsapp-webhook.service`, `whatsapp-sync.service`, `sdc-notifier.service`, `hermes-kanban-dispatcher.service`
  - Tenant-specific: `nathy-bot.service`, `nathy-mcp.service`, `nathy-conta-bot.service` (hermosillo-contabilidad)

### cron configurations
- **FOUND:** Active crontab with 9 entries:
  1. `0 * * * *` -- Git pull origin main (hourly)
  2. `0 * * * *` -- Memory auto-save (hourly)
  3. `0 2 * * *` -- Log cleanup older than 14 days (daily 2 AM)
  4. `0 3 * * *` -- Backup script (daily 3 AM)
  5. `0 8 * * *` -- Daily pipeline script (daily 8 AM)
  6. `*/10 * * * *` -- Disk usage alert if >85%
  7. `*/15 * * * *` -- Healthcheck autonomous script (every 15 min)
  8. `30 9 * * 1` -- ABE Music report push (Mondays 9:30 AM)
  9. `0 3 * * 0` -- Memory prune (Sundays 3 AM)
- Cron-related code files: `cron.py`, `cronjob_tools.py`, `cron-internals.md`, `cron-troubleshooting.md` in the hermes-agent subproject

---

## SUMMARY OF FINDINGS

**Project:** Sonora Digital Corp -- a multi-tenant AI-powered digital transformation agency based in Hermosillo, Sonora, Mexico.

**Core Infrastructure:**
- Git repo: `sonoradigitalcorp-H/Sonora-Digital-Corp` on GitHub
- 6 systemd services running 24/7
- Docker containers: PostgreSQL, Qdrant, Redis, n8n
- 9 cron jobs for automation
- wacli (WhatsApp CLI) installed and authenticated
- TTS: edge-tts with DaliaNeural voice (es-MX)
- Voice pipeline: STT Whisper + TTS -> OGG Opus

**Tenants:**
1. **Aztrotech** (Cesar Holguin) -- Full voice assistant, Telegram dual-bot system, lead management, 92 Gherkin test scenarios, marketing automation
2. **hermosillo-contabilidad** (Nathaly Hermosillo) -- Accounting bot (Nathy), MCP server, CFDI/RESICO/nominas skills
3. **abe-music** -- Music production platform
4. **demo_client** -- Demo client with sdc-bot.service

**Security Note:** Several .odt files in Referencia/ contain sensitive data in plaintext (passwords, API keys, bot tokens, Hostinger credentials).
</task_result>
</task>
```

---

## Assistant (Build · MiMo V2.5 · 174.8s)

_Thinking:_

Now I have comprehensive data from all three exploration tasks. Let me compile the complete audit document. I have extensive information about the project structure, infrastructure, agents, MCP servers, skills, tests, and more.

Let me now create the comprehensive audit document.

Now I have complete data. Let me compile the comprehensive technical audit.

---

# AUDITORÍA TÉCNICA COMPLETA — SONORA DIGITAL CORP

---

## 1. Executive Summary

**Sonora Digital Corp (SDC)** es una plataforma de transformación digital multi-tenant con ecosistema de agentes AI, ubicada en Hermosillo, Sonora, México. Desarrollada por un solo desarrollador ("mystic") entre marzo y agosto de 2026.

| Métrica | Valor |
|---------|-------|
| Edad del proyecto | ~5 meses (Marzo-Agosto 2026) |
| Lenguaje principal | Python 3.10+ / TypeScript |
| Framework backend | FastAPI |
| Framework frontend | Next.js 15 / Vue 3 |
| Agentes definidos | 56+ (20 OpenCode + 36 ADK) |
| MCP servers | 30+ Python, 8+ JSON configs |
| Skills | 138 directorios |
| Tenants activos | 6 (enterprise/pro/basic/demo) |
| Clientes activos | 5 (ABE Music, Aztrotech, Nathy Conta, El Joyero, Fourgea) |
| Dockerfiles | 39 |
| Docker Compose files | 30 |
| Servicios systemd | 23+ |
| Cron jobs | 9 |
| Tests | 100+ Python + 80+ Gherkin features |
| Specs/SDD | 18 activas + 25 completadas |
| ADRs | 19 |
| Base de datos | PostgreSQL 15, Redis 7, Neo4j, Qdrant, 13+ SQLite |
| VPS | Hostinger 149.56.46.173 (Ubuntu, 11GB RAM) |

**Veredicto:** Proyecto ambicioso con arquitectura extensa, exceso de abstracciones, deuda técnica significativa, y riesgo de mantenibilidad a 5 años. Requiere consolidación urgente.

---

## 2. Architecture Overview

### 2.1 Capa Conceptual — 6 Capas Concéntricas

```
Layer 0: kernel/     → Constitución del sistema (SOUL.md, OMEGA-PROMPT.md, reglas)
Layer 1: infra/      → Infraestructura (Docker, Nginx, PostgreSQL, Redis)
Layer 2: apps/       → Aplicaciones core (24 apps)
Layer 3: products/   → Productos (23 productos)
Layer 4: clients/    → Clientes (5 con configuraciones dedicadas)
Layer 5: tenants/    → Tenant deployments (6 activos)
```

### 2.2 Arquitectura Lógica

```
┌─────────────────────────────────────────────────┐
│                 KERNEL (Layer 0)                │
│  SOUL.md · OMEGA-PROMPT.md · 10-RULES.md       │
│  AI-ETHICS.md · CHECKSUMS.sha256               │
├─────────────────────────────────────────────────┤
│                INFRAESTRUCTURA (Layer 1)        │
│  Docker · Nginx · PostgreSQL · Redis · Neo4j   │
│  Qdrant · n8n · Langfuse · FreeSWITCH          │
├─────────────────────────────────────────────────┤
│                APLICACIONES (Layer 2)           │
│  core · hermes · evolution · voice · whatsapp  │
│  telegram · instagram · tiktok · spotify        │
│  grimoire · monitor · frontends · openclaw      │
├─────────────────────────────────────────────────┤
│                PRODUCTOS (Layer 3)              │
│  clon-digital · mystika · agent-marketplace    │
│  nsfw-ai-studio · omnivoice · content-studio   │
├─────────────────────────────────────────────────┤
│                CLIENTES (Layer 4)               │
│  ABE Music · Aztrotech · Nathy Conta · etc.    │
├─────────────────────────────────────────────────┤
│                TENANTS (Layer 5)                │
│  abe-music · hermosillo · aztrotech · demo     │
└─────────────────────────────────────────────────┘
```

### 2.3 Arquitectura de Agentes

**Modelo:** Multi-agente con orquestador central ("mystic" con god-mode) + 20 subagentes + 36+ ADK agents YAML.

**Problemas detectados:**
- 56+ agentes definidos pero no todos están implementados
- Duplicación: OpenCode agents vs ADK agents vs Client agent YAMLs
- Sin observabilidad unificada de agentes
- Sin métricas de performance por agente

### 2.4 Arquitectura MCP

**Ecosistema fragmentado:**
- 30+ servidores MCP Python (skills/mcp/servers/)
- 8+ configs JSON
- 1 Gateway JS (mcp-gateway.js)
- 7 MCPs configurados en opencode.json
- Sin estandarización de protocolos
- Sin health checks centralizados

### 2.5 Arquitectura AI

- **LLMs:** OpenRouter (DeepSeek V4, Kimi K2.7, GLM-5.2, Claude 3.5 Sonnet)
- **Embeddings:** FastEmbed (paraphrase-multilingual-MiniLM-L12-v2, 384-dim)
- **Vector DB:** Qdrant (colecciones por tenant)
- **Graph DB:** Neo4j
- **RAG:** FastEmbed + Qdrant (custom implementation)
- **Voice:** edge-tts (DaliaNeural) + faster-whisper
- **Memory:** Engram (SQLite), multi-layer (7 capas)
- **Observabilidad:** Langfuse (configurado, estado incierto)
- **Cost Tracking:** cost_tracker.db + token_tracker.py por tenant

---

## 3. Repository Tree

```
Sonora Digital Corp/
├── .pytest_cache/
├── Audiovisuales/                    # Assets multimedia
│   ├── General/                      # Imágenes, videos, thumbnails (~30 archivos)
│   ├── ABE Music/                    # Audio (.mp3)
│   ├── Sonora Digital Corp/          # Logos, branding, chat exports (~30 archivos)
│   └── Instaladores/                 # Paquetes .deb OpenCode
├── Clientes/                         # Documentos de clientes (fuera del repo git)
│   ├── Fourgea Mexico/              # 2 .docx + 1 .pdf
│   ├── ABE Music Group/             # Documentos + proyecto tenant completo
│   └── Aztrotech/                   # Bot + web + openclaw + audiovisuales
├── Finanzas/                         # Finanzas personales/empresa
│   ├── Nóminas/                     # Nóminas PDF
│   ├── SAT-FIEL/                    # Certificados .cer/.key + constancias
│   └── Facturas/                    # Facturas PDF
├── ops/                              # Estado operativo local
│   └── state/
│       ├── skill-registry.json      # Skills de Hermes
│       └── engram_aztrotech.db      # SQLite memoria Aztrotech
├── Prototipos/                       # VACÍO
├── Referencia/                       # Documentos .odt de referencia
│   ├── prompt kimi.txt              # Prompt Prometheus Orchestrator
│   ├── *.odt                        # 11 documentos (plan, config, deploy, credenciales)
│   └── (CONTIENE CREDENCIALES EN TEXTO PLANO)
├── tenants/                          # Tenant configs (fuera del repo principal)
│   ├── demo-client/                 # Config demo
│   └── demo_client/                 # Config demo (DUPLICADO con guión vs guión bajo)
├── session-ses_*.md                  # 4 sesiones de OpenCode
└── sonora-digital-corp/              # ← REPOSITORIO PRINCIPAL (git)
    ├── .agents/                      # Agentes OpenCode
    ├── .engram/                      # Estado engram
    ├── .github/                      # GitHub Actions, dependabot, PR template
    ├── .hermes/                      # Config Hermes
    ├── .opencode/                    # Config OpenCode
    ├── .planning/                    # Planning artifacts
    ├── .specify/                     # Specify config
    ├── adrs/                         # 19 Architecture Decision Records
    ├── apps/                         # 24 aplicaciones (Layer 2)
    ├── capabilities/                 # Business capabilities
    ├── clients/                      # Clientes con configs completas (Layer 4)
    ├── config/                       # 44+ config files (SSOT)
    ├── docs/                         # Documentación
    ├── infra/                        # Infraestructura Docker/systemd
    ├── kernel/                       # Constitución del sistema (30 archivos)
    ├── ops/                          # Operations state
    ├── portal/                       # Grimoire 3D (Three.js)
    ├── process/                      # Specs pipeline (18 active + 25 completed)
    ├── products/                     # 23 productos (Layer 3)
    ├── reference/                    # Specs cerradas
    ├── scripts/                      # 70+ scripts utilitarios
    ├── sdc-brain-vault/              # Brain vault
    ├── shared/                       # Shared utilities
    ├── skills/                       # 138 skills + MCP servers
    ├── skills-lock.json              # Skills lockfile (335 líneas)
    ├── state/                        # Runtime state
    ├── tenants/                      # Tenant deployments
    └── tests/                        # 100+ test files
```

### Carpeta por carpeta:

| Carpeta | Propósito | Dependencias | Estado |
|---------|-----------|-------------|--------|
| `Audiovisuales/` | Assets multimedia (logos, videos, thumbnails) | Ninguna | ⚠️ Sin organizar, duplicados |
| `Clientes/` | Docs de clientes (fuera del repo git) | Ninguna | ⚠️ No versionado, credenciales expuestas |
| `Finanzas/` | Finanzas empresa (nóminas, facturas, SAT) | Ninguna | ⚠️ CREDENCIALES EN TEXTO PLANO |
| `ops/` | Estado operativo local | SQLite | ✅ Funcional |
| `Prototipos/` | Prototipos | — | 🔴 VACÍO |
| `Referencia/` | Documentos de referencia .odt | — | ⚠️ CREDENCIALES EXPUESTAS |
| `tenants/` | Tenant configs (fuera del repo) | — | ⚠️ Duplicado con repo |
| `sonora-digital-corp/` | Repositorio principal | Todo | ✅ Activo, git push |
| `sonora-digital-corp/kernel/` | Constitución del sistema | Ninguna | ✅ 30 archivos |
| `sonora-digital-corp/infra/` | Docker, systemd, nginx | Docker | ✅ Configurado |
| `sonora-digital-corp/apps/` | 24 aplicaciones | FastAPI, Next.js | ⚠️ Muchas incompletas |
| `sonora-digital-corp/products/` | 23 productos | Varies | ⚠️ Muchos en draft |
| `sonora-digital-corp/skills/` | 138 skills + 30 MCP servers | Python, JS | ⚠️ Exceso de abstracciones |
| `sonora-digital-corp/tests/` | 100+ test files | pytest | ✅ Activo |
| `sonora-digital-corp/config/` | 44+ config files | — | ✅ SSOT |

---

## 4. Inventory

### 4.1 Apps (24)

| App | Objetivo | Estado | Framework | Lenguaje |
|-----|----------|--------|-----------|----------|
| `core/` | Engine central (planner, executors, agents) | Activo | Python | Python |
| `evolution/` | Auto-evolución, scorecard, learning | Activo | Python | Python |
| `hermes/` | Multi-channel gateway (Telegram, WhatsApp) | Activo | Python/Docker | Python |
| `frontends/sonora-web/` | Frontend principal | En desarrollo | Next.js | TypeScript |
| `frontends/app/` | App móvil/web | En desarrollo | Vue 3 | TypeScript |
| `frontends/platform/` | Platform dashboard | En desarrollo | Vue 3 | TypeScript |
| `grimoire/` | Portal 3D (Three.js) | Activo | Three.js | JavaScript |
| `monitor/` | Monitoring dashboard | En desarrollo | — | — |
| `voice/` | Voice pipeline (TTS/STT) | Activo | edge-tts, faster-whisper | Python |
| `whatsapp/` | WhatsApp integration | Activo | wacli | Python |
| `telegram_scheduler/` | Telegram scheduler | Activo | SQLite | Python |
| `instagram/` | Instagram integration | Draft | — | — |
| `tiktok/` | TikTok integration | Draft | — | — |
| `youtube/` | YouTube integration | Draft | — | — |
| `spotify/` | Spotify integration | Draft | — | — |
| `twilio-voice/` | Twilio voice | Activo | Twilio | Python |
| `voice-realtime/` | Real-time voice | Experimental | — | — |
| `openclaw_edge/` | OpenClaw edge | Activo | FastMCP | Python |
| `SIGNAL/` | Signal processing | Draft | — | — |
| `sonora_engine/` | Sonora Engine | En desarrollo | FastAPI | Python |
| `webui/` | Web UI | Draft | — | — |
| `stt/` | Speech-to-Text | Activo | faster-whisper | Python |
| `tts/` | Text-to-Speech | Activo | edge-tts | Python |
| `jarvis-dashboard/` | JARVIS Dashboard | Draft | — | — |

### 4.2 Core

**Path:** `sonora-digital-corp/apps/core/`

**Responsabilidades:**
- Planner central
- Executors
- Agent registry
- Task orchestration

**NO debería contener:**
- Lógica de negocio específica de clientes
- Configuración de tenants
- Implementaciones de MCP

**Servicios que ofrece:**
- Task planning
- Agent lifecycle management
- Capability execution

**Dependientes:** evolution, hermes, all specialized agents

### 4.3 Modules

No existe directorio `modules/` formal. La modularización está dispersa en:
- `skills/` (138 módulos)
- `apps/core/` (core modules)
- `shared/` (utilities compartidas)

### 4.4 Packages

No existen packages internos formalizados (no monorepo con nx/turborepo/pnpm workspaces).

**Deberían ser packages:**
- `shared/` → @sdc/shared-types
- `config/` → @sdc/config
- Skills reutilizables → @sdc/skills-*

### 4.5 Servicios

**Servicios systemd activos (23+):**

| Servicio | Estado | Tipo |
|----------|--------|------|
| sdc-aztrotech-bot | ✅ Active | Bot Telegram |
| sdc-aztrotech-dashboard | ✅ Active | Dashboard |
| sdc-aztrotech-notif | ✅ Active | Notifications |
| sdc-aztrotech-tts | ✅ Active | TTS Server |
| sdc-aztrotech-voice | ✅ Active | Voice Assistant |
| sdc-n8n-bridge | ✅ Active | n8n Bridge |
| sonora-affiliates | Configurado | API |
| sonora-client-api | Configurado | API |
| ce-son-api | Configurado | API |
| sonora-tracker | Configurado | Tracker |
| comfyui | Configurado | AI Image |
| whatsapp-r1-webhook | Configurado | WhatsApp |
| engram-obsidian-export | Configurado | Sync |
| omnivoice-agent | Configurado | Voice AI |
| sdc-ws-bridge | Configurado | WebSocket |
| telegram-scheduler | Configurado | Scheduler |
| sonora-notifier | Configurado | Notifier |
| sdc-twilio-voice | Configurado | Twilio |
| sdc-observer | Configurado | Observer |
| sdc-event-listener | Configurado | Events |
| whatsapp-responder | Configurado | WhatsApp |
| whatsapp-r1-responder | Configurado | WhatsApp |
| sonora-adk | Configurado | ADK |
| sonora-evolution | Configurado | Evolution |
| whatsapp-webhook | Configurado | WhatsApp |
| whatsapp-sync | Configurado | WhatsApp |
| sdc-notifier | Configurado | Notifier |
| hermes-kanban-dispatcher | Configurado | Kanban |

**Docker containers:**
- postgres-1 (PostgreSQL 15)
- redis-1 (Redis 7 Alpine)
- qdrant-1 (Qdrant)
- n8n-1 (n8n)
- neo4j-1 (Neo4j)

**Cron jobs (9):**
1. `0 * * * *` — Git pull origin main (hourly)
2. `0 * * * *` — Memory auto-save (hourly)
3. `0 2 * * *` — Log cleanup 14 días (daily 2AM)
4. `0 3 * * *` — Backup script (daily 3AM)
5. `0 8 * * *` — Daily pipeline (daily 8AM)
6. `*/10 * * * *` — Disk usage alert >85%
7. `*/15 * * * *` — Healthcheck autonomous (15min)
8. `30 9 * * 1` — ABE Music report (Mondays 9:30AM)
9. `0 3 * * 0` — Memory prune (Sundays 3AM)

### 4.6 Agentes AI

| Agente | Propósito | Herramientas | MCPs | Memoria | Modelo | Autonomía | Estado |
|--------|-----------|-------------|------|---------|--------|-----------|--------|
| **mystic** | Primary agent, alma de SDC | All tools | All MCPs | Engram | DeepSeek V4 / Kimi K2.7 | God mode | ✅ Activo |
| hermes | Multi-channel gateway | Telegram, WhatsApp, Desktop | openclaw | — | Multi-model | Subagent | ✅ Activo |
| openclaw | 42 skills gateway | Skills, MCP | openclaw | — | — | Subagent | ⚠️ Offline |
| sdd | SDD Orchestrator (6 phases) | Skills, Files | — | Engram | — | Subagent | ✅ |
| sdd-spec | Spec generation | Files | — | — | — | Subagent | ✅ |
| sdd-design | Plan + tasks from specs | Files | — | — | — | Subagent | ✅ |
| sdd-apply | Implementation execution | Terminal, Files | — | — | — | Subagent | ✅ |
| sdd-verify | Constitution/checklist/tests | Files, Tests | — | — | — | Subagent | ✅ |
| sdd-archive | Results documentation | Files | — | — | — | Subagent | ✅ |
| sales | Lead gen, qualification, proposals | CRM, WhatsApp | — | — | — | Subagent | ⚠️ Draft |
| dev | Software delivery, CI/CD | Terminal, Git | — | — | — | Subagent | ⚠️ Draft |
| support | Tickets, SLAs | — | — | — | — | Subagent | ⚠️ Draft |
| agent-os | Harness lifecycle, skill registry | Skills | — | — | — | Subagent | ⚠️ Draft |
| knowledge | 7-layer memory, ADRs | Engram, Obsidian | engram | Engram | — | Subagent | ✅ |
| finance | FinOps, revenue tracking | — | — | — | — | Subagent | ⚠️ Draft |
| security | Secrets, audit, incidents | — | shield | — | — | Subagent | ⚠️ Draft |
| ops | Infrastructure, monitoring | — | — | — | — | Subagent | ⚠️ Draft |
| quality | Test frameworks, audits | pytest | — | — | — | Subagent | ⚠️ Draft |
| strategy | Initiatives, enterprise score | — | — | — | — | Subagent | ⚠️ Draft |
| builder | Feature implementation | Terminal | — | — | — | Subagent | ⚠️ Draft |
| reviewer | Code review, security | Git | — | — | — | Subagent | ⚠️ Draft |
| social | Social media publishing | — | — | — | — | Subagent | ⚠️ Draft |
| content | Blogs, designs, presentations | — | — | — | — | Subagent | ⚠️ Draft |
| music | Beats, lyrics, covers | — | — | — | — | Subagent | ⚠️ Draft |

**ADK Agents (36+ YAML):** ABE Music subsystem agents (artist-management, content-factory, fan-crm, music-saas, revenue-engine) — cada uno con variantes analytics/crm/marketing/revenue/scheduler.

**Problemas:**
- ~18 de 24 OpenCode agents están en estado "Draft" — no implementados
- Duplicación masiva de agentes ADK (36+ YAMLs con naming repetitivo)
- Sin métricas de utilización por agente
- Sin límites de autonomía formalizados

### 4.7 MCP Servers

| Nombre | Endpoint | Puerto | Transporte | Herramientas | Estado |
|--------|----------|--------|------------|-------------|--------|
| openclaw | localhost | 18789 | HTTP | 42 skills | ⚠️ Offline |
| engram | 149.56.46.173 | 7437 | HTTP | Memory CRUD | ✅ |
| qdrant | 149.56.46.173 | 6333 | HTTP | Vector search | ✅ |
| neo4j | 149.56.46.173 | 7687 | Bolt | Graph queries | ✅ |
| n8n | 149.56.46.173 | 5678 | HTTP | Workflows | ✅ |
| adk | 149.56.46.173 | 6401 | HTTP | 36 agents | ⚠️ Incierto |
| shield | 149.56.46.173 | 8930 | HTTP | Security | ⚠️ Incierto |
| mcp-gateway | — | 18989 | HTTP | 108 tools | ⚠️ Incierto |

**MCP Python servers (30+):** engram, rag, llm, voice_clone, kokoro, whisper, crm, payments, commissions, pricing, credit, playwright, wacli, twilio, onboarding, provision, content, fal_ai, lora, generate, omnivoice, firecrawl, hasura, supabase, ffmpeg, upload, cost_tracker, routing, sdc_mcp_stdio, openlovable, mercadopago.

**Problemas críticos:**
- 30+ MCP servers pero no hay evidencia de que todos estén ejecutándose
- Sin health check centralizado
- Sin documentación de disponibilidad
- Gateway JS no estandarizado
- Mezcla de transportes (HTTP, stdio, Bolt)

### 4.8 Herramientas

| Tool | Quién la usa |
|------|-------------|
| Playwright (browser automation) | playwright_mcp.py |
| Filesystem (read/write/edit) | Todos los agentes |
| Terminal (bash) | dev, ops, mystic |
| Git | dev, reviewer, mystic |
| Telegram (bot API) | hermes, aztrotech-bot, social, content |
| WhatsApp (wacli) | hermes, whatsapp bots |
| Qdrant (vector search) | rag_mcp.py, knowledge agent |
| Neo4j (graph) | graph queries, knowledge |
| PostgreSQL (SQL) | All data persistence |
| Redis (cache) | Sessions, rate limiting |
| n8n (workflows) | Automation, bots |
| OpenRouter (LLM) | All AI agents |
| edge-tts (TTS) | Voice pipeline |
| faster-whisper (STT) | Voice pipeline |
| FastEmbed (embeddings) | RAG pipeline |
| Langfuse (tracing) | Observability |
| Twilio (voice) | Voice calls |
| FreeSWITCH (SIP) | VoIP |
| Google Sheets/Drive | Data sync |
| MercadoPago | Payments |
| Supabase | Backend-as-a-Service |

### 4.9 Specs

**Specs activas (18):**

| Spec | Fecha | Tema |
|------|-------|------|
| SPEC-20260702-001 | Jul 2 | Core architecture |
| SPEC-20260703-A/B/C | Jul 3 | Design iterations |
| SPEC-20260704-ABE-001 | Jul 4 | ABE Music integration |
| SPEC-20260704-EXECUTION | Jul 4 | Execution pipeline |
| SPEC-20260704-EVOLUTION | Jul 4 | Evolution engine |
| SPEC-20260710-INTEGRATION | Jul 10 | Integration |
| SPEC-20260712-SONORA-001/002 | Jul 12 | Sonora Engine |
| SPEC-20260718-CLONE-SERVICE | Jul 18 | Digital clone |
| SPEC-20260718-ENGRAM-AUTOCAPTURE | Jul 18 | Auto memory capture |
| SPEC-20260718-ONBOARDING | Jul 18 | Onboarding flow |
| SPEC-20260719-SOCIAL-001 | Jul 19 | Social media |
| SPEC-20260719-WHATSAPP-OS-FASE1 | Jul 19 | WhatsApp OS |
| SPEC-20260722-001 | Jul 22 | General |
| SPEC-20260726-4PILARES | Jul 26 | 4 Pillars |
| SPEC-20260726-ECOSYSTEM | Jul 26 | Ecosystem |
| SPEC-ECOSYSTEM | — | Ecosystem |

**Specs completadas:** 25+ con SPEC.md, gherkin/, SCORE.md, ADR.md

**Capability Specs (9):** sync-artist-data, process-payment, multi-tenant-platform, manage-crm, score-artist, analyze-artist, clone-person, search-knowledge, generate-video

### 4.10 Metodologías

| Práctica | Presente | Estado |
|----------|----------|--------|
| SDD (Specification-Driven Development) | ✅ | Activo, 6-phase pipeline |
| DDD (Domain-Driven Design) | ⚠️ Parcial | Bounded contexts definidos pero no formalizados |
| TDD | ⚠️ Parcial | Tests existentes pero coverage bajo (fail_under=60%) |
| BDD | ✅ | 80+ Gherkin features |
| ADR | ✅ | 19 ADRs |
| Conventional Commits | ⚠️ Parcial | Algunos commits lo siguen |
| GitFlow | ❌ | No evidente |
| Semantic Versioning | ⚠️ Parcial | pyproject.toml dice v2.0.0 |
| CI/CD | ⚠️ Parcial | .github/workflows existe |
| Feature Flags | ❌ | No detectado |
| Code Review | ❌ | No evidente (1 desarrollador) |
| Monorepo | ✅ | Sí, pero sin herramientas (nx/turborepo) |
| pnpm workspaces | ❌ | No |
| Pre-commit hooks | ✅ | .pre-commit-config.yaml |
| Ruff (linter) | ✅ | Configurado en pyproject.toml |
| Flake8 | ✅ | .flake8 presente |

### 4.11 Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | Next.js 15, Vue 3, Vite, Three.js, Tailwind CSS, HTMX, Alpine.js |
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | PostgreSQL 15, SQLite (13+ databases) |
| **Cache** | Redis 7 |
| **Queue** | n8n (workflow automation) |
| **LLMs** | OpenRouter (DeepSeek V4, Kimi K2.7, GLM-5.2, Claude 3.5 Sonnet) |
| **Embeddings** | FastEmbed (paraphrase-multilingual-MiniLM-L12-v2) |
| **Vector DB** | Qdrant |
| **Graph DB** | Neo4j |
| **Storage** | VPS local disk, Supabase (configured) |
| **Cloud** | Hostinger VPS (149.56.46.173), Vercel (frontend) |
| **IaC** | Docker Compose (30 files) |
| **Containers** | Docker, Docker Compose |
| **Reverse Proxy** | Nginx |
| **VoIP** | FreeSWITCH, Twilio |
| **TTS** | edge-tts (DaliaNeural) |
| **STT** | faster-whisper |
| **Observabilidad** | Langfuse, custom monitoring |
| **Analytics** | Custom (cost_tracker, token_tracker) |
| **Seguridad** | JWT, API Keys, UFW, Fail2ban, SSL |
| **Testing** | pytest, pytest-bdd, promptfoo |
| **Build** | Makefile |
| **Deploy** | systemd, Docker, GitHub Actions |

### 4.12 Infraestructura

**VPS:** Hostinger, 149.56.46.173, Ubuntu, 11GB RAM

**Docker:**
- PostgreSQL 15
- Redis 7 Alpine
- Neo4j
- Qdrant
- n8n
- Langfuse + Langfuse DB
- Telegram bot
- MCP server
- 39 Dockerfiles en total

**Nginx:** Configurado en `infra/nginx/`

**systemd:** 23+ servicios

**Cron:** 9 jobs (git pull, backups, healthchecks, reports)

**Backups:** Daily script (3AM)

**SSL:** Certbot (configurado en deploy script)

**DNS:** Cloudflare (mencionado en configs)

**Firewall:** UFW + Fail2ban

### 4.13 Versionado

- **Git:** Activo, remote en GitHub
- **Repo:** `sonoradigitalcorp-H/Sonora-Digital-Corp`
- **Branch:** `main`
- **Último commit:** `3ab137f feat: Bot notificaciones @MysticUnity_bot activo`
- **Tags:** No detectados
- **Branches:** Solo `main` evidenciado
- **Release notes:** CHANGELOG.md existe pero no actualizado regularmente
- **Semantic versioning:** pyproject.toml v2.0.0

### 4.14 Bases de Datos

| DB | Tipo | Propósito | Migraciones |
|----|------|-----------|-------------|
| PostgreSQL | Relational | Core data, leads, conversations | 010_sonora_os.sql |
| Redis | Key-value | Cache, sessions | — |
| Neo4j | Graph | Knowledge graph | — |
| Qdrant | Vector | RAG embeddings | — |
| engram_aztrotech.db | SQLite | Memoria Aztrotech (7 layers) | — |
| engram_astrotech.db | SQLite | Memoria Aztrotech (DUPLICATE) | — |
| queue.db | SQLite | Execution queue | — |
| social_schedule.db | SQLite | Social media scheduling | — |
| cost_tracker.db | SQLite | Cost tracking | — |
| economics.db | SQLite | Economics | — |
| social_sessions.db | SQLite | Social sessions | — |
| 00-working.db | SQLite | Working memory | — |
| 01-project.db | SQLite | Project memory | — |
| 02-organization.db | SQLite | Organization memory | — |
| telegram_scheduler.db | SQLite | Telegram scheduling | — |
| sqlite_mcp_server.db | SQLite | Hermes MCP | — |

**Problemas:**
- 13+ bases de datos SQLite sin gestión centralizada
- Duplicado: `engram_aztrotech.db` y `engram_astrotech.db` (typo)
- Sin migraciones formales para SQLite
- Sin backup strategy para SQLite files

### 4.15 APIs

**REST APIs:**
- FastAPI core (apps/core/)
- ABE Music API (localhost:5180)
- ABE Studio API
- Sonora Engine
- Client API
- CE Son API

**WebSockets:**
- ABE Music WS (ws://localhost:5180/ws)
- OpenClaw WS

**MCP:**
- 30+ MCP servers (HTTP + stdio)

**Internas:**
- MCP Gateway (108 tools)
- n8n workflows

**Externas:**
- OpenRouter API
- Telegram Bot API
- WhatsApp (wacli)
- Twilio Voice API
- Google Sheets/Drive API
- MercadoPago API
- Supabase API

### 4.16 Variables de Entorno

**20 archivos .env.example detectados** en distintas ubicaciones.

**Principales variables (sin secretos):**

| Variable | Descripción | Dónde se usa | Estado |
|----------|------------|--------------|--------|
| DATABASE_URL | PostgreSQL connection | Core, apps | ✅ |
| REDIS_URL | Redis connection | Cache | ✅ |
| NEO4J_URI | Neo4j connection | Graph | ✅ |
| QDRANT_URL | Qdrant connection | Vector DB | ✅ |
| OPENROUTER_API_KEY | LLM API key | All AI | ✅ |
| TELEGRAM_BOT_TOKEN | Telegram bot | Bots | ✅ |
| WACLI_STORE | WhatsApp session | WhatsApp | ✅ |
| WACLI_AUTH_TOKEN | WhatsApp auth | WhatsApp | ✅ |
| SDC_WA_API_KEY | WhatsApp API | WhatsApp | ✅ |
| N8N_WEBHOOK_URL | n8n webhook | Automation | ✅ |
| NEXTAUTH_SECRET | NextAuth secret | Frontend | ✅ |
| MERCADOPAGO_ACCESS_TOKEN | MercadoPago | Payments | ✅ |
| TENANT_ID | Tenant identifier | Multi-tenant | ✅ |
| JWT_SECRET | JWT signing | Auth | ✅ |
| HERMES_API_URL | Hermes endpoint | Hermes | ✅ |
| LANGFUSE_SECRET_KEY | Langfuse tracing | Observability | ✅ |

**Problemas:**
- 20 archivos .env.example duplicados en distintos niveles
- `tenants/demo_client/.env` contiene API key en texto plano (NO es .env.example)
- Falta `.env.example` estandarizado
- Variables como OPENROUTER_API_KEY duplicadas en múltiples .env

### 4.17 Seguridad

**Implementado:**
- JWT authentication (core)
- API Keys
- UFW firewall
- Fail2ban
- SSL/TLS (certbot)
- Prompt injection protection (policies.yaml)
- PII auto-redact (credit_card, password)
- Tool sandbox (policies.yaml)
- Rate limiting (60/min Telegram, 500/hr API)
- CHECKSUMS.sha256 (kernel integrity)

**FALTANTE:**
- OAuth 2.0
- RBAC formal
- Secrets management centralizado (Vault)
- Audit logging centralizado
- Penetration testing
- Dependency vulnerability scanning

**RIESGOS CRÍTICOS:**
- `Referencia/hostingerR.odt` — Credenciales Hostinger en texto plano
- `Referencia/hostinguer api.odt` — API key Hostinger en texto plano
- `Referencia/psw.odt` — Password en texto plano
- `Referencia/untitled_0.odt` — Bot token en texto plano
- `tenants/demo_client/.env` — API key real en texto plano
- `tenants/demo_client/sdc-bot.service` — API key hardcodeada en Environment

### 4.18 Observabilidad

**Implementado:**
- Langfuse (configurado en docker-compose)
- Custom monitoring (`apps/monitor/`)
- cost_tracker.db
- token_tracker.py (por tenant)
- Health checks en systemd services
- Disk usage alerts (cron)
- Healthcheck autonomous (cron cada 15 min)

**FALTANTE:**
- Distributed tracing (OpenTelemetry)
- Metrics (Prometheus/Grafana)
- Centralized logging (ELK/Loki)
- Alerting (PagerDuty/Opsgenie)
- APM dashboards
- SLO/SLI tracking

### 4.19 Automatizaciones

| Automatización | Estado | Descripción |
|---------------|--------|-------------|
| n8n | ✅ | Workflow automation (10+ workflows) |
| Cron jobs | ✅ | 9 jobs activos |
| GitHub Actions | ⚠️ | .github/workflows existe pero no verificado |
| Pre-commit | ✅ | .pre-commit-config.yaml |
| Dependabot | ✅ | .github/dependabot.yml |
| Backup script | ✅ | Daily 3AM |
| Git pull cron | ✅ | Hourly |
| Healthcheck | ✅ | Cada 15 min |
| Memory auto-save | ✅ | Hourly |
| Memory prune | ✅ | Weekly |
| ABE Music report | ✅ | Weekly Monday |

### 4.20 Dependencias

**Python (requirements.txt):**
```
fastapi>=0.139.0, uvicorn>=0.51.0, neo4j>=6.2.0, qdrant-client>=1.18.0,
fastmcp>=0.2.0, faster-whisper>=1.2.1, edge-tts>=6.1.0, ollama>=0.6.2,
pytest>=9.1.0, pytest-bdd>=8.0.0, tiktoken>=0.13.0, + 28 más
```

**Problemas:**
- Sin lock file para pip (solo requirements.txt)
- `ollama>=0.6.2` listado pero Ollama no parece estar en uso activo
- Dependencias de LLM duplicadas (openrouter + ollama + langfuse)
- Sin auditoría de dependencias (pip-audit)
- `skills-lock.json` tiene 335 líneas de skills de GitHub externo

### 4.21 Deuda Técnica

**CRÍTICA:**
1. **Credenciales en texto plano** en Referencia/*.odt y tenants/demo_client/.env
2. **13+ bases de datos SQLite** sin gestión centralizada
3. **Typo en nombre de DB:** `engram_aztrotech.db` vs `engram_astrotech.db`
4. **~18 agentes OpenCode en estado "Draft"** — nunca implementados
5. **36+ agentes ADK YAML** — exceso de abstracciones sin implementación
6. **30+ MCP servers** — la mayoría no ejecutándose
7. **39 Dockerfiles** — sin estandarización
8. **30 Docker Compose files** — fragmentación extrema

**ALTA:**
9. **Duplicación de configs:** 11 archivos opencode.json en distintos niveles
10. **Duplicación de .env:** 20 archivos .env.example
11. **Duplicación de clientes:** Clientes/ (fuera del repo) + clients/ (dentro del repo)
12. **Duplicación de tenants:** tenants/ (fuera del repo) + tenants/ (dentro del repo)
13. **`Prototipos/` vacío** — directorio sin uso
14. **`Audiovisuales/` sin organizar** — archivos multimedia mezclados
15. **`Finanzas/` con datos sensibles** — nóminas, facturas, certificados SAT
16. **Sin lock file para pip**
17. **Coverage mínimo 60%** — insuficiente para producción
18. **Sin CI/CD pipeline verificado**
19. **OpenClaw offline** — servicio crítico caído

**MEDIA:**
20. **Skills lockfile externo** (335 skills de GitHub) — no revisados
21. **Sin formalización de packages internos**
22. **Sin documentación de API (OpenAPI/Swagger)**
23. **Sin ADR updates recientes**
24. **CHANGELOG no actualizado regularmente**
25. **Session files en workspace root** — no versionados
26. **`referencia/` vs `Referencia/`** — posible duplicado por case sensitivity

### 4.22 Oportunidades

**Modularizar:**
- Extraer cada MCP server como package independiente
- Crear @sdc/shared-types para TypeScript
- Crear @sdc/shared-utils para Python
- Formalizar capabilities como plugins

**Convertir en plugins:**
- Client-specific skills (ABE Music, Nathy Conta, El Joyero)
- Niche catalogs (tacos, barberking, mystik, bufete)
- Social media publishers

**Debe ser Core:**
- Engram memory system
- RAG pipeline
- Multi-tenant routing
- Agent lifecycle management

**Debe salir del Core:**
- Client-specific business logic
- Product-specific implementations
- ABE Music agent subsystem (36 YAMLs)

**Debe ser Package:**
- `shared/` → @sdc/shared
- `config/` → @sdc/config
- `kernel/` → @sdc/kernel (constitution as code)

**Debe ser App:**
- Cada producto con docker-compose independiente
- Cada cliente con su workspace aislado

---

## 5. Infrastructure Map

```
┌────────────────────────────────────────────────────────────┐
│                    HOSTINGER VPS                           │
│              149.56.46.173 · Ubuntu · 11GB RAM            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │  Redis   │  │  Neo4j   │  │  Qdrant  │  │
│  │   :5432  │  │  :6379   │  │  :7687   │  │  :6333   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   n8n    │  │ Langfuse │  │FreeSWITCH│  │  Nginx   │  │
│  │  :5678   │  │  :3000   │  │  :5060   │  │  :80/443 │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SYSTEMD SERVICES (23+)                  │  │
│  │  aztrotech-bot · aztrotech-tts · aztrotech-voice    │  │
│  │  aztrotech-notif · aztrotech-dashboard              │  │
│  │  n8n-bridge · hermes · sonora-adk · evolution       │  │
│  │  whatsapp-* · telegram-scheduler · observer         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CRON JOBS (9)                           │  │
│  │  git-pull · memory-save · log-cleanup · backup      │  │
│  │  daily-pipeline · disk-alert · healthcheck           │  │
│  │  abe-report · memory-prune                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              SECURITY                                │  │
│  │  UFW · Fail2ban · SSL (certbot) · SSH hardening    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              MIDDLEWARE / EXTERNAL                    │  │
│  │  OpenRouter · Telegram API · WhatsApp (wacli)       │  │
│  │  Twilio · Google Sheets/Drive · MercadoPago         │  │
│  │  Vercel (frontend deploy)                            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## 6. AI Ecosystem

```
┌─────────────────────────────────────────────────┐
│              LAYER 7: SOUL                       │
│  kernel/SOUL.md · OMEGA-PROMPT.md              │
│  "We are builders of systems that serve life"   │
├─────────────────────────────────────────────────┤
│              LAYER 6: MEMORY                    │
│  Engram (7-layer SQLite) · Qdrant (vectors)    │
│  Neo4j (graph) · Obsidian (notes)              │
├─────────────────────────────────────────────────┤
│              LAYER 5: ORCHESTRATION             │
│  mystic (god-mode) · hermes (gateway)          │
│  openclaw (42 skills) · ADK (36 agents)        │
├─────────────────────────────────────────────────┤
│              LAYER 4: SPECIALIZATION            │
│  24 OpenCode agents · 9 capabilities           │
│  138 skills · 30+ MCP servers                   │
├─────────────────────────────────────────────────┤
│              LAYER 3: INTEGRATION               │
│  MCP Gateway (108 tools) · n8n (workflows)     │
│  Telegram · WhatsApp · Twilio · FreeSWITCH     │
├─────────────────────────────────────────────────┤
│              LAYER 2: DATA                      │
│  PostgreSQL · Redis · Qdrant · Neo4j           │
│  13+ SQLite databases                          │
├─────────────────────────────────────────────────┤
│              LAYER 1: INFRASTRUCTURE            │
│  Docker · systemd · Nginx · VPS               │
│  UFW · Fail2ban · SSL · Cron                   │
└─────────────────────────────────────────────────┘
```

**Modelos LLM en uso:**
- DeepSeek V4 Flash (free tier)
- Kimi K2.7 (Moonshot AI)
- GLM-5.2 (Zhipu AI)
- Claude 3.5 Sonnet (Anthropic, via OpenRouter)
- Ollama (configurado pero no evidente en uso activo)

**Embeddings:**
- FastEmbed (paraphrase-multilingual-MiniLM-L12-v2, 384-dim)

**Voice Pipeline:**
- TTS: edge-tts (DaliaNeural es-MX) → port :8765
- STT: faster-whisper (small model) → port :8766

---

## 7. MCP Ecosystem

```
┌─────────────────────────────────────────────────┐
│           MCP GATEWAY (:18989)                  │
│     108 tools · 9 resources · HTTP              │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │ ENGRAM MCP  │  │ RAG MCP     │              │
│  │ :7437       │  │ (Qdrant)    │              │
│  │ Memory CRUD │  │ Vector search│              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │ NEO4J MCP   │  │ REDIS MCP   │              │
│  │ :7687 Bolt  │  │ :6379       │              │
│  │ Graph queries│  │ Cache ops   │              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │ N8N MCP     │  │ OPENCLAW    │              │
│  │ :5678       │  │ :18789      │              │
│  │ Workflows   │  │ 42 skills   │              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │ ADK MCP     │  │ SHIELD MCP  │              │
│  │ :6401       │  │ :8930       │              │
│  │ 36 agents   │  │ Security    │              │
│  └─────────────┘  └─────────────┘              │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │     SPECIALIZED MCPs (30+ Python)        │   │
│  │  voice · crm · payments · pricing       │   │
│  │  onboarding · provision · content        │   │
│  │  fal-ai · lora · omnivoice · firecrawl   │   │
│  │  supabase · hasura · ffmpeg · upload     │   │
│  │  cost-tracker · routing · mercadopago    │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 8. Dependency Graph

```
kernel/ (Layer 0)
  └── infra/ (Layer 1)
       ├── postgresql
       ├── redis
       ├── neo4j
       ├── qdrant
       ├── n8n
       ├── docker
       ├── nginx
       └── systemd
            └── apps/ (Layer 2)
                 ├── core/
                 │    ├── planner
                 │    ├── executors
                 │    └── agents
                 ├── hermes/
                 │    ├── telegram
                 │    ├── whatsapp
                 │    └── desktop
                 ├── voice/
                 │    ├── tts (edge-tts)
                 │    └── stt (faster-whisper)
                 ├── evolution/
                 ├── openclaw_edge/
                 └── frontends/
                      ├── sonora-web (Next.js)
                      ├── app (Vue 3)
                      └── platform (Vue 3)
                           └── products/ (Layer 3)
                                ├── clon-digital
                                ├── mystika
                                ├── agent-marketplace
                                ├── nsfw-ai-studio
                                ├── omnivoice
                                └── content-studio
                                     └── clients/ (Layer 4)
                                          ├── ABE Music
                                          ├── Aztrotech
                                          ├── Nathy Conta
                                          ├── El Joyero
                                          └── Fourgea
                                               └── tenants/ (Layer 5)
                                                    ├── abe-music
                                                    ├── aztrotech
                                                    ├── hermosillo-contabilidad
                                                    └── demo
```

---

## 9. Risk Report

### RIESGOS CRÍTICOS (Immediate Action Required)

| # | Riesgo | Impacto | Probabilidad |
|---|--------|---------|-------------|
| R1 | **Credenciales en texto plano** en Referencia/*.odt (Hostinger, passwords, bot tokens) | Compromiso total del VPS | Alta |
| R2 | **API key real en tenants/demo_client/.env** y sdc-bot.service | Acceso no autorizado a OpenRouter | Alta |
| R3 | **OpenClaw offline** — servicio crítico caído | Loss of 42 skills | Alta |
| R4 | **13+ SQLite sin backup** — datos frágiles | Pérdida de memoria/estado | Alta |
| R5 | **Sin health check centralizado** para 30+ MCP servers | Failures silently ignored | Alta |

### RIESGOS ALTOS

| # | Riesgo | Impacto |
|---|--------|---------|
| R6 | **Exceso de abstracciones** (56+ agents, 138 skills, 30+ MCPs) | Inmantenibilidad |
| R7 | **1 desarrollador** — bus factor = 1 | Continuidad del proyecto |
| R8 | **Sin CI/CD pipeline verificado** | Deploy manual, errores humanos |
| R9 | **Coverage mínimo 60%** | Regresiones no detectadas |
| R10 | **Duplicación masiva** (configs, .env, clientes, tenants) | Confusión, inconsistencias |

### RIESGOS MEDIOS

| # | Riesgo |
|---|--------|
| R11 | Sin lock file para pip |
| R12 | Sin RBAC formal |
| R13 | Sin observabilidad distribuida |
| R14 | Sin documentación de API |
| R15 | Sin testing de carga |
| R16 | Sin disaster recovery plan |
| R17 | Session files sin versionar |

---

## 10. Technical Debt Summary

| Categoría | Items | Severidad |
|-----------|-------|-----------|
| Seguridad | Credenciales en texto plano (5+ archivos) | 🔴 CRÍTICA |
| Arquitectura | 30+ MCP servers sin ejecutar | 🔴 ALTA |
| Arquitectura | 18+ agentes en draft | 🟡 MEDIA |
| Duplicación | 11 opencode.json, 20 .env, 2 tenants dirs | 🟡 MEDIA |
| Testing | Coverage 60%, sin load testing | 🟡 MEDIA |
| Ops | 13+ SQLite sin gestión centralizada | 🔴 ALTA |
| Ops | OpenClaw offline | 🔴 ALTA |
| Docs | CHANGELOG desactualizado | 🟢 BAJA |
| Infra | 39 Dockerfiles sin estandarización | 🟡 MEDIA |
| Infra | Sin lock file pip | 🟡 MEDIA |

---

## 11. Recommendations

### INMEDIATO (Esta semana)
1. **Eliminar credenciales en texto plano** de Referencia/*.odt — mover a secrets manager
2. **Rotar todas las API keys** comprometidas (OpenRouter, Hostinger, Telegram bots)
3. **Activar OpenClaw** — diagnosticar por qué está offline
4. **Eliminar tenants/demo_client/.env** con credencial real — usar solo .env.example
5. **Implementar backup para SQLite** — cron job que copie a backup dir

### CORTO PLAZO (1-2 semanas)
6. **Consolidar directorios duplicados** — unificar Clientes/ y clients/, tenants/ y tenants/
7. **Crear .gitignore efectivo** — excluir credenciales, .env real, sesiones
8. **Implementar CI/CD pipeline** — GitHub Actions para test + lint + deploy
9. **Centralizar gestión de secrets** — usar sops, age, o vault
10. **Auditar MCP servers** — desactivar los no utilizados, documentar los activos

### MEDIANO PLAZO (1-2 meses)
11. **Reducir agentes** de 56+ a los realmente utilizados (~10-15)
12. **Formalizar packages internos** — shared, config, kernel como packages
13. **Implementar observabilidad** — OpenTelemetry + Prometheus + Grafana
14. **Aumentar coverage** a 80%+
15. **Documentar APIs** — OpenAPI/Swagger auto-generado
16. **Crear disaster recovery plan** — backup + restore testing

### LARGO PLAZO (3-6 meses)
17. **Monorepo tooling** — Turborepo o Nx para gestión de dependencias
18. **Feature flags** — LaunchDarkly o custom
19. **Load testing** — k6 o locust
20. **Security audit** — penetration testing formal
21. **RBAC formal** — roles y permisos centralizados
22. **Multi-developer setup** — onboarding docs, coding standards

---

## 12. Roadmap

### CRÍTICO (Esta semana)
- [ ] Eliminar credenciales en texto plano
- [ ] Rotar API keys comprometidas
- [ ] Activar OpenClaw
- [ ] Backup para SQLite
- [ ] .gitignore para .env real

### ALTA PRIORIDAD (1-2 semanas)
- [ ] Unificar directorios duplicados
- [ ] CI/CD pipeline básico
- [ ] Centralizar secrets
- [ ] Auditar MCP servers
- [ ] Eliminar agentes Draft no utilizados

### MEDIA (1-2 meses)
- [ ] Formalizar packages internos
- [ ] Observabilidad distribuida
- [ ] Coverage 80%+
- [ ] API documentation
- [ ] Disaster recovery plan
- [ ] Load testing

### BAJA (3-6 meses)
- [ ] Monorepo tooling
- [ ] Feature flags
- [ ] RBAC formal
- [ ] Security audit formal
- [ ] Multi-developer setup
- [ ] ADR updates

### FUTURO (6+ meses)
- [ ] Mobile app (React Native/Expo)
- [ ] Multi-region deployment
- [ ] Enterprise features (SSO, SCIM)
- [ ] AI model fine-tuning
- [ ] Marketplace público

---

## 13. Score del Proyecto

| Dimensión | Score (0-100) | Justificación |
|-----------|---------------|---------------|
| **Arquitectura** | 45 | Buena visión (6 capas, DDD parcial), pero exceso de abstracciones y sin consolidación |
| **Implementación** | 40 | Muchos componentes sketcheados, pocos completos. OpenClaw offline. |
| **Calidad** | 35 | Coverage 60%, sin CI/CD verificado, sin code review |
| **Seguridad** | 25 | Credenciales en texto plano, sin RBAC, sin vault |
| **Operaciones** | 50 | Cron jobs, healthchecks, backups existen, pero sin observabilidad formal |
| **Documentación** | 55 | BLUEPRINT.md, AGENTS.md, ADRs existen, pero desactualizados |
| **Testing** | 45 | BDD con Gherkin, unit tests, pero coverage bajo |
| **Escalabilidad** | 35 | Multi-tenant diseñado pero no probado a escala |
| **Mantenibilidad** | 30 | 1 desarrollador, duplicación masiva, sin packages formales |
| **Innovación** | 65 | Ecosistema AI ambicioso, voice pipeline, 7-layer memory |

### **SCORE GLOBAL: 40/100**

---

## 14. Madurez de Arquitectura

**Nivel: Inicial / Repetible (Level 2 de CMMI)**

- ✅ Visión arquitectónica documentada (BLUEPRINT.md)
- ✅ Capas definidas (6 concentric layers)
- ✅ Bounded contexts identificados
- ⚠️ Sin formalización de bounded contexts
- ⚠️ Sin domain model formal
- ❌ Sin arquitectura de despliegue formal
- ❌ Sin architecture fitness functions
- ❌ Sin component diagrams actualizados

---

## 15. Madurez DevOps

**Nivel: Inicial (Level 1 de CMMI)**

- ✅ Docker + Docker Compose
- ✅ systemd services
- ✅ Cron jobs
- ✅ Git + GitHub
- ⚠️ CI/CD parcial (GitHub Actions configurado)
- ⚠️ Pre-commit hooks
- ❌ Sin CD automatizado
- ❌ Sin infrastructure as code formal
- ❌ Sin immutable deployments
- ❌ Sin canary/blue-green deployments
- ❌ Sin rollback automatizado

---

## 16. Madurez AI

**Nivel: Repetible (Level 2 de CMMI)**

- ✅ Multi-LLM integration (OpenRouter)
- ✅ RAG pipeline funcional
- ✅ Multi-layer memory (Engram)
- ✅ Voice pipeline (TTS + STT)
- ✅ Agent orchestration
- ⚠️ Prompt engineering (OMEGA-PROMPT)
- ⚠️ Eval framework (promptfoo)
- ❌ Sin A/B testing de prompts
- ❌ Sin métricas de calidad de respuesta
- ❌ Sin guardrails centralizados
- ❌ Sin cost optimization automatizada

---

## 17. Madurez Seguridad

**Nivel: Inicial (Level 1 de CMMI)**

- ✅ UFW + Fail2ban
- ✅ SSL/TLS
- ⚠️ JWT authentication
- ⚠️ Rate limiting
- ⚠️ Prompt injection protection
- ❌ Credenciales en texto plano (CRÍTICO)
- ❌ Sin RBAC
- ❌ Sin secrets management
- ❌ Sin audit logging
- ❌ Sin penetration testing
- ❌ Sin dependency vulnerability scanning

---

## 18. Madurez Escalabilidad

**Nivel: Inicial (Level 1 de CMMI)**

- ✅ Multi-tenant architecture diseñada
- ✅ PostgreSQL (escala vertical)
- ✅ Qdrant (escala horizontal)
- ⚠️ Redis cache
- ❌ Sin load testing
- ❌ Sin auto-scaling
- ❌ Sin circuit breakers
- ❌ Sin rate limiting por tenant
- ❌ Sin resource quotas
- ❌ Sin performance benchmarks

---

## 19. Checklist de Mejoras

### Seguridad (PRIORIDAD MÁXIMA)
- [ ] Eliminar todas las credenciales en texto plano
- [ ] Implementar secrets management (sops/age/vault)
- [ ] Rotar todas las API keys
- [ ] Implementar RBAC
- [ ] Audit logging
- [ ] Dependency scanning (pip-audit)
- [ ] Penetration testing

### Arquitectura
- [ ] Consolidar agentes (de 56+ a ~15)
- [ ] Consolidar MCP servers (de 30+ a ~10 activos)
- [ ] Formalizar packages internos
- [ ] Eliminar duplicación de directorios
- [ ] Architecture fitness functions

### Testing
- [ ] Aumentar coverage a 80%+
- [ ] Load testing
- [ ] Integration testing completo
- [ ] E2E testing automatizado

### Operaciones
- [ ] Observabilidad distribuida (OpenTelemetry)
- [ ] Centralized logging (Loki)
- [ ] Metrics dashboard (Grafana)
- [ ] Alerting (PagerDuty/Opsgenie)
- [ ] Disaster recovery testing
- [ ] Backup verification

### DevOps
- [ ] CI/CD pipeline completo
- [ ] Automated testing en CI
- [ ] Automated deployment
- [ ] Rollback automatizado
- [ ] Infrastructure as Code

---

## 20. Próximas Acciones Recomendadas

**INMEDIATO (Hoy):**
1. Revisar y eliminar credenciales de Referencia/*.odt
2. Verificar por qué OpenClaw está offline
3. Hacer backup de todos los SQLite files

**ESTA SEMANA:**
4. Crear .gitignore comprehensivo
5. Unificar directorios duplicados
6. Implementar CI pipeline básico

**ESTE MES:**
7. Centralizar secrets management
8. Auditar y reducir MCP servers
9. Aumentar test coverage
10. Documentar APIs con OpenTemplate

**ESTE TRIMESTRE:**
11. Implementar observabilidad
12. Formalizar packages
13. Security audit
14. Load testing
15. Disaster recovery plan

---

*Auditoría generada el 2026-08-03 por MiMo V2.5*
*Repositorio: sonoradigitalcorp-H/Sonora-Digital-Corp*
*VPS: 149.56.46.173*

---


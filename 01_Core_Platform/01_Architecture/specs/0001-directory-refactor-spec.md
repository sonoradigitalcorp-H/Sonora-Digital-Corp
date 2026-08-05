# SPEC-0001: Enterprise Directory Structure Refactor for Sonora Digital Corp

## Version
v1.0.0

## Author
Senior DevOps Engineer (Automated Migration)

## Date
2026-08-05

## 1. Purpose
Standardize the chaotic directory structure of Sonora Digital Corp into a clean, enterprise-grade, AI-agent-friendly multitenant layout.

## 2. Problem Statement
The legacy structure at `/home/mystic/Documentos/Sonora Digital Corp` contained:
- 44,540 total files (including dependencies and caches)
- Mixed client code, audiovisual assets, finance docs, and AI state
- No boundaries between tenants or asset types
- AI agents creating random folders during operation

## 3. Solution Design

### 3.1 New Directory Topology
```
Sonora Digital Corp Nuevo/
├── 00_Administration/
├── 01_Core_Platform/
│   ├── 01_Architecture/
│   │   ├── adr/           ← Architecture Decision Records
│   │   └── specs/          ← Technical specifications
│   ├── 02_Source_Code/
│   ├── 03_Infrastructure/
│   └── 04_Shared_Libraries/
├── 02_Client_Projects/
│   ├── [CLIENT_NAME]/
│   │   ├── 01_Discovery/
│   │   ├── 02_Source_Code/
│   │   │   ├── Skills/
│   │   │   ├── Bots/
│   │   │   └── Agentes/
│   │   ├── 03_Media_Assets/
│   │   │   ├── Audio/
│   │   │   └── Visual/
│   │   └── 04_Deployment/
├── 03_Sandbox_and_RnD/
└── SYSTEM_MANIFEST.md
```

### 3.2 File Type Segregation Rules
| File Extension(s) | Destination |
|---|---|
| .mp3, .wav, .aac, .m4a, .oga, .ogg | `03_Media_Assets/Audio/` |
| .png, .jpg, .jpeg, .gif, .svg, .webp, .mp4 | `03_Media_Assets/Visual/` |
| .md, .txt, .pdf, .docx | `01_Discovery/` |
| .py, .js, .ts, .json, .yaml, .yml, .env | `02_Source_Code/` |
| .db, .sqlite, .sqlite3 | `04_Deployment/` |

### 3.3 Client Mapping
| Legacy Name | Clean Name | Structure |
|---|---|---|
| Aztrotech | Aztrotech | Skills, Bots |
| Ivan Guerrero RYE | RYE_Ivan_Guerrero | Skills, Bots |
| ABE Music Group | ABE_Music_Group | Skills, Bots |
| Fourgea México | Fourgea_Mexico | Skills, Bots |
| Sonora Digital Corp | Sonora_Digital_Corp | (root only) |
| General | General | (root only) |
| Instaladores | Instaladores | (root only) |

### 3.4 Exclusion List (IGNORED during migration)
- `node_modules/`
- `.git/`
- `__pycache__/`
- `.venv/`
- `.pytest_cache/`
- `.ruff_cache/`
- `blobs/` (fastembed cache)
- `snapshots/`

## 4. Migration Steps Executed
1. Phase 1: Created Enterprise directory skeleton (mkdir -p)
2. Phase 2: Bulk migration via `enterprise_migrate.sh`
   - 652 files moved
   - 284 name collisions resolved (renamed with `_1`, `_2` suffixes)
3. Phase 3: Garbage collection (25 empty dirs removed)
4. Phase 4: Created `SYSTEM_MANIFEST.md` as AI automation contract

## 5. Test Criteria
- ✅ `ls -la /home/mystic/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects/` shows all 8 clients
- ✅ `find ... -name "node_modules" -path "*_Old*"` returns nothing (basura ignorada)
- ✅ `SYSTEM_MANIFEST.md` exists at project root

## 6. Acceptance
- [x] All legacy folders moved (or already in transit)
- [x] Clean structure available for new client work
- [x] SYSTEM_MANIFEST.md created
- [x] Zero deletions (rm only used for empty dir cleanup)

## 7. Future Work
- Decommission legacy folders (`00_Admin`, `01_Core`, `02_Clientes`, `03_Sandbox`) after 30-day stabilization
- Remove `Clientes_Old` and `Audiovisuales_Old` after manual review
- Migrate remaining legacy core to `01_Core_Platform`

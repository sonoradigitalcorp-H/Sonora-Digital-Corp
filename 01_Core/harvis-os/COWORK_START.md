# Harvis OS — Quick Start para Cowork

## Prerrequisitos

```bash
# Verificar que Docker está corriendo
docker ps

# Verificar que Ollama está corriendo
curl http://localhost:11434/api/tags

# Si falta qwen3:4b
ollama pull qwen3:4b
```

## 3 Terminales para Cowork

### Terminal 1: Harvis OS API
```bash
cd ~/Documentos/Sonora\ Digital\ Corp/harvis-os
uvicorn src.core.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Tests en watch mode
```bash
cd ~/Documentos/Sonora\ Digital\ Corp/harvis-os
python -m pytest tests/ -v --watch
```

### Terminal 3: Servicios / Logs
```bash
# Ver servicios Docker
docker ps

# Ver logs de Ollama
tail -f /tmp/ollama_pull.log

# O ejecutar el script de inicio
./start.sh
```

## URLs Locales

| Servicio | URL |
|----------|-----|
| Harvis OS API | http://localhost:8000 |
| Harvis OS Docs | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| Qdrant | http://localhost:6333 |
| Ollama | http://localhost:11434 |
| n8n | http://localhost:5678 |

## Verificar que funciona

```bash
# Health check
curl http://localhost:8000/health

# Crear tarea
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"source": "cli", "user_id": "test", "content": "Crear función de login"}'

# Ver agentes
curl http://localhost:8000/api/v1/agents
```

## Stack Actual

```
✅ Docker: PostgreSQL, Redis, Qdrant, n8n
✅ Ollama: all-minilm, nomic-embed-text
⏳ Ollama: qwen3:4b (descargando...)
✅ Harvis OS: API + Tests (155 passing)
```

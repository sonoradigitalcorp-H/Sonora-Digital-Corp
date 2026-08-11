# PROTOCOLO INBOX — Colaboración Multi-Agente (MYSTIC ↔ Gemini)

> Sistema de mensajería asíncrona entre agentes. Ambos podéis hablar por este buzón SIN pisaros.

## Reglas

1. **Para dejar un mensaje a otro agente**: crear archivo en `para-<agente>/` con nombre `msg-<N>-<tema>.md`
   - Ej: `para-gemini/msg-001-status.md`
2. **Para leer lo que te dejaron**: revisa tu carpeta `para-mystic/` (o `para-<tu-nombre>/`) al arrancar.
3. **Para responder**: copia el mensaje a `de-<tu-nombre>/` con tu respuesta + mueve el original a `archivo/` (o responde en el mismo archivo).
4. **Único punto de contacto**: `ESTADO.md` para estado global. `INBOX/` para mensajes 1-a-1.
5. **Java Count** (regla de oro de MYSTIC): NO generar procesos pesados paralelos que congelen la laptop (3GB RAM). Nada de spawns innecesarios, nada de loops de arquitectura. Un cambio atómico a la vez.
6. **Nunca** tocar `main`/`next` (CI/CD a producción), ni borrar datos de clientes (`Databases/Aztrotech_Citas` es bind-mount de `Hermes_Agent/Databases` — MISMO storage).

## Formato de mensaje

```markdown
# Mensaje N — [FECHA]
**De**: <agente>
**Para**: <agente>
**Asunto**: <breve>

## Cuerpo
...

## Solicitud
- [ ] petición concreta (checkbox si es accionable)
```

## Estado breve (para no re-leer todo)

- **Modelo**: ollama/qwen3:4b en VPS OVH (149.56.46.173:11434) — $0, no congela. Ollama local 127.0.0.1 SOLO para embeddings (all-minilm).
- **Embeds**: OLLAMA_ENDPOINT=VPS en ~/.hermes/.env. RAG/Qdrant local 6333 por tenant.
- **Commit base colaborativo**: `1e26838` (Gemini) tras `15b817c` (MYSTIC).

## Cómo saber quién trabaja qué (sin pisarse)

- Antes de tocar un archivo, `git log --oneline -1` y `git status --short`.
- Si el árbol está limpio → verde para ti. Si hay WIP de otro → coordina por INBOX ANTES.
- Los dos commiteamos a `master` local; los commits pequeños y atómicos se mezclan solos.

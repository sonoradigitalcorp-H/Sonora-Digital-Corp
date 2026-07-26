---
title: Planificador
date: 2026-07-25
status: draft
author: SDC Architecture Team
version: 1.0.0
---

# Planner — Router de Intenciones

## Propósito

El Planner es el cerebro del sistema. Decide **qué hacer** con cada mensaje del usuario:

- ¿Llamar una herramienta?
- ¿Buscar memoria?
- ¿Responder directamente?
- ¿Ejecutar comando interno?

Su objetivo principal es **evitar llamadas LLM innecesarias**, usando reglas determinísticas para rutas conocidas.

## Intents

| Intent | Disparador | Acción |
|--------|-----------|--------|
| `check_system` | Palabras clave: "status", "memoria", "cpu", "ram", "disco" | Ejecuta `system_monitor`, devuelve métricas |
| `chat` | Conversación general | Memory recall + LLM |
| `tool_call` | Frases de acción: "busca en internet", "manda notificación", "consulta la BD" | Ejecuta tool correspondiente |
| `memory_recall` | "Qué hablamos sobre X", "Recuérdame" | MemoryEngine.search_all + respuesta directa |
| `command` | Comandos internos: `/clear`, `/help`, `/tenant` | Ejecuta comando local sin LLM |

## Arquitectura

```
User Message
    │
    ▼
┌──────────────────────┐
│  Intent Classifier   │  ← Regex-based primero, LLM como fallback
└──────┬───────────────┘
       │
       ├── check_system  → system_monitor tool  → respuesta
       ├── chat          → MemoryEngine → LLM   → respuesta
       ├── tool_call     → Tool Registry → tool  → LLM post-proc → respuesta
       ├── memory_recall → MemoryEngine          → respuesta
       └── command       → handler local         → respuesta
```

## Optimizaciones

### Sin LLM

Las siguientes rutas **nunca** llaman al LLM:

- `check_system` → formatea métricas directamente
- `memory_recall` sin tool → busca y devuelve contexto
- `command` → ejecuta comando interno

### Con LLM (solo cuando es necesario)

- `chat` → siempre usa LLM (con contexto de memoria)
- `tool_call` → LLM post-procesa resultado de tool

### Clasificador de Intents

El clasificador usa un pipeline de 3 pasos:

1. **Regex rápido**: patrones conocidos → intent inmediato
2. **Reglas de keyword**: palabras clave → intent probable
3. **LLM fallback**: si no hay match, el LLM clasifica

```python
class IntentClassifier:
    RULES = {
        "check_system": ["status", "cpu", "ram", "disco", "memoria", "uptime"],
        "memory_recall": ["qué hablamos", "recuerda", "mencioné", "conversación anterior"],
        "tool_call": ["busca", "navega", "consulta", "notifica"],
        "command": ["/clear", "/help", "/tenant"],
    }

    def classify(self, message: str) -> IntentResult:
        # Paso 1: Regex
        for intent, patterns in self.RULES.items():
            if any(re.match(p, message.lower()) for p in patterns):
                return IntentResult(intent=intent, confidence=1.0, source="regex")
        # Paso 2: Keyword scoring
        scores = self._keyword_score(message)
        if scores[0].confidence > 0.8:
            return scores[0]
        # Paso 3: LLM fallback
        return self._llm_classify(message)
```

# SPEC-025: Jarvis Intent Classifier

**Status:** Draft
**Tier:** 2 (Infrastructure)
**Score:** 82/100
**Created:** 2026-08-02

## 1. Objective

Clasificar intenciones de voz del usuario en 10 categorías predefinidas con soporte bilingüe (ES/EN), extracción de parámetros, y fallback a LLM cuando la clasificación local falla.

## 2. User Stories

- Como usuario, quiero que Jarvis entienda mi intención sin necesidad de comandos exactos
- Como desarrollador, quiero clasificación rápida (< 50ms) para UI responsiva
- Como operador, quiero métricas de precisión por categoría

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | 10 intents predefinidos: calendar, email, task, search, control, query, alert, reminder, navigate, report | P0 | 10 |
| FR2 | Keywords ES/EN para cada intent con synonym expansion | P0 | 8 |
| FR3 | Param extraction: fechas, montos, nombres, acciones | P1 | 12 |
| FR4 | OpenRouter fallback: cuando confidence < threshold | P1 | 6 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Latencia de clasificación | < 50ms p95 |
| NFR2 | Precisión de clasificación | > 90% |
| NFR3 | Throughput | > 500 req/s |

## 5. Intent Categories

| Intent | Keywords ES | Keywords EN | Example |
|--------|------------|------------|---------|
| calendar | reunión, cita, agenda, reservar | meeting, schedule, book | "Agenda una reunión mañana" |
| email | correo, enviar, bandeja | email, send, inbox | "Envía un correo a Juan" |
| task | tarea, pendiente, completar | task, todo, complete | "Marca tarea como completada" |
| search | buscar, encuentra, buscar | search, find, look up | "Busca información sobre..." |
| control | abrir, cerrar, iniciar, parar | open, close, start, stop | "Abre el navegador" |
| query | consulta, pregunta, dime | query, ask, tell me | "¿Cuántas ventas hay hoy?" |
| alert | alerta, notificación, aviso | alert, notify, warning | "Alerta si el servidor cae" |
| reminder | recordar, avisar, alarma | remind, alert, alarm | "Recuérdame llamar a las 3" |
| navigate | ir a, navega, muestra | go to, navigate, show | "Ve al dashboard de ventas" |
| report | reporte, genera, exporta | report, generate, export | "Genera reporte mensual" |

## 6. Technical Architecture

```
┌─────────────────────────────────────────────┐
│           Intent Classifier                 │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │        Keyword Matcher              │   │
│  │  (ES/EN synonyms + regex)           │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│  ┌──────────────┴──────────────────────┐   │
│  │     Confidence Evaluator            │   │
│  │  (threshold = 0.7)                  │   │
│  └──────────────┬──────────────────────┘   │
│                 │                           │
│       ┌─────────┴─────────┐                │
│       │ High Confidence   │ Low Confidence │
│       │ Return Intent     │ → OpenRouter   │
│       └───────────────────┴────────────────┘
└─────────────────────────────────────────────┘
```

## 7. Data Model

```typescript
interface IntentResult {
  intent: string;
  confidence: number;
  params: Record<string, any>;
  source: 'keyword' | 'llm';
  latency_ms: number;
}

interface IntentConfig {
  name: string;
  keywords_es: string[];
  keywords_en: string[];
  param_patterns: RegExp[];
  examples: string[];
}
```

## 8. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /intent/classify | Classify text to intent |
| GET | /intent/list | List all supported intents |
| GET | /intent/stats | Get classification statistics |
| POST | /intent/feedback | Submit classification feedback |

## 9. Error Handling

- **Empty input:** Return error with validation message
- **Language not detected:** Try both ES and EN keywords
- **OpenRouter timeout:** Return best keyword match with lower confidence
- **OpenRouter error:** Log and return keyword result

## 10. Security Considerations

- Input sanitization for regex patterns
- Rate limiting per tenant
- No PII stored in classification logs
- Audit trail for LLM fallback usage

## 11. Testing Strategy

- Unit tests for each intent keyword set
- Integration tests with OpenRouter
- Accuracy tests with labeled dataset (100+ samples)
- Performance tests for latency requirements

## 12. Deployment

- Standalone container or embedded in main service
- Config-driven intent definitions (YAML)
- Hot-reload for keyword updates

## 13. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Classification latency p95 | > 50ms |
| LLM fallback rate | > 30% |
| Misclassification reports | > 10/day |

## 14. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| OpenRouter | External | LLM fallback |
| yaml-config | Library | Intent configuration |

## 15. Success Criteria

- [ ] All 10 intents implemented with ES/EN keywords
- [ ] Classification accuracy > 90%
- [ ] Latency < 50ms p95 for keyword path
- [ ] OpenRouter fallback working for low-confidence cases
- [ ] 85% test coverage
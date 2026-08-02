# SPEC-024: Jarvis Context Engine

**Status:** Draft
**Tier:** 2 (Infrastructure)
**Score:** 80/100
**Created:** 2026-08-02

## 1. Objective

Proporcionar contexto ilimitado al agente Jarvis mediante la fusión de múltiples fuentes de memoria: engram (memoria semántica), PostgreSQL (datos estructurados), Qdrant RAG (vectores), y Redis (caché).

## 2. User Stories

- Como usuario, quiero que Jarvis recuerde conversaciones previas para no repetir contexto
- Como desarrollador, quiero acceso unified a todas las fuentes de memoria
- Como operador, quiero métricas de latencia por fuente de datos

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Engram search: buscar en memoria semántica del tenant | P0 | 8 |
| FR2 | PostgreSQL queries: consultar datos estructurados | P0 | 6 |
| FR3 | Qdrant RAG: búsqueda semántica por embeddings | P1 | 10 |
| FR4 | Redis cache: cachear resultados frecuentes | P1 | 4 |
| FR5 | Multi-source fusion: combinar resultados de todas las fuentes | P0 | 12 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Latencia de búsqueda combinada | < 200ms p95 |
| NFR2 | Throughput de queries | > 100 req/s |
| NFR3 | Disponibilidad | 99.9% |

## 5. Technical Architecture

```
┌─────────────────────────────────────────────┐
│            Context Engine                    │
├─────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Engram  │  │ Postgres│  │ Qdrant  │    │
│  │ Search  │  │ Query   │  │ RAG     │    │
│  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │             │             │          │
│       └─────────────┼─────────────┘          │
│                     │                        │
│              ┌──────┴──────┐                 │
│              │   Fusion    │                 │
│              │   Engine    │                 │
│              └──────┬──────┘                 │
│                     │                        │
│              ┌──────┴──────┐                 │
│              │Redis Cache  │                 │
│              └─────────────┘                 │
└─────────────────────────────────────────────┘
```

## 6. Data Model

```typescript
interface ContextResult {
  source: 'engram' | 'postgres' | 'qdrant' | 'redis';
  score: number;
  data: Record<string, any>;
  latency_ms: number;
}

interface FusedContext {
  results: ContextResult[];
  confidence: number;
  total_latency_ms: number;
}
```

## 7. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /context/search | Search all sources and fuse results |
| GET | /context/engram/:tenant_id | Search engram directly |
| GET | /context/postgres/:tenant_id | Query PostgreSQL directly |
| POST | /context/qdrant/:tenant_id | RAG search via Qdrant |
| GET | /context/cache/:key | Get cached context |

## 8. Error Handling

- **Engram unavailable:** Fall back to PostgreSQL + Qdrant
- **PostgreSQL unavailable:** Fall back to Engram + Redis cache
- **Qdrant unavailable:** Use keyword-based PostgreSQL search
- **Redis unavailable:** Skip cache, query sources directly

## 9. Security Considerations

- Tenant isolation on all queries
- SQL injection prevention via parameterized queries
- Rate limiting per tenant
- Audit logging for all context access

## 10. Testing Strategy

- Unit tests for each source adapter
- Integration tests for fusion engine
- Load tests for latency requirements
- Chaos tests for source failure scenarios

## 11. Deployment

- Single Docker container with all adapters
- Environment variables for each source connection
- Health check endpoint at /context/health

## 12. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Fusion latency p95 | > 200ms |
| Source error rate | > 5% |
| Cache hit ratio | < 60% |

## 13. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| PostgreSQL | External | Structured data storage |
| Qdrant | External | Vector database |
| Redis | External | Caching layer |
| FastEmbed | Library | Local embedding generation |

## 14. Open Questions

- Should we implement source priority weighting?
- How to handle conflicting information across sources?
- Optimal TTL for Redis cache entries?

## 15. Success Criteria

- [ ] All 5 functional requirements implemented
- [ ] Fusion latency < 200ms p95
- [ ] Cache hit ratio > 60% after warmup
- [ ] 90% test coverage
- [ ] Integration tests passing
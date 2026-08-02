# JARVIS Ecosystem — Data Model

## Modelo de Datos del Ecosistema

---

### 1. Neo4j — Base de Grafos

#### Nodos Principales

```cypher
// JARVIS Core
(:Session {id, title, pinned, project, tags, archived, created_at, updated_at, token_count})
(:Message {id, role, content, tokens, timestamp})

// SDC Business Layer
(:Customer {id, nombre, email, telefono, tipo, nicho, plan, status, created_at, updated_at})
(:Subscription {id, plan, precio, multiplicador, stripe_subscription_id, start_date, end_date, status})
(:Transaction {id, plan, amount, provider, status, created_at})

// Mysticverse
(:Creator {id, nombre, email, kyc_status, created_at})
(:DigitalTwin {id, creator_id, status, face_trained, voice_cloned, personality_created, bot_active, created_at})
(:KycRecord {id, creator_id, document_type, age_verified, identity_verified, consent_signed, status})
(:Player {id, nombre, xp, level, streak, created_at})

// ABE MUSIC
(:Artist {id, nombre, genero, pais, status, streams, revenue, created_at})
(:Release {id, artist_id, titulo, tipo, streams, revenue, status, fecha_lanzamiento})
(:RevenueEntry {id, release_id, amount, source, artist_share, label_share})
```

#### Relaciones

```cypher
// JARVIS Core
(s:Session)-[:CONTAINS]->(m:Message)

// SDC Business
(c:Customer)-[:TIENE_SUSCRIPCION]->(s:Subscription)
(c:Customer)-[:REALIZO]->(t:Transaction)
(c:Customer)-[:REFIRIO_A]->(other:Customer)

// Mysticverse
(c:Creator)-[:TIENE_TWIN]->(d:DigitalTwin)
(c:Creator)-[:TIENE_KYC]->(k:KycRecord)
(c:Creator)-[:ES_JUGADOR]->(p:Player)

// ABE MUSIC
(a:Artist)-[:RELEASED]->(r:Release)
(r:Release)-[:GENERO_INGRESO]->(re:RevenueEntry)
```

### 2. Qdrant — Base Vectorial

#### Colecciones

| Colección | Dimensión | Distancia | Payload Indexes |
|-----------|-----------|-----------|-----------------|
| conversations | 768 | Cosine | timestamp, user, session_id |
| documents | 768 | Cosine | source, type, created_at |
| tasks | 768 | Cosine | status, priority, assignee |
| jarvis_knowledge | 768 | Cosine | topic, source, created_at |

### 3. SQLite — Experience Library (Agent-Evolver)

```sql
CREATE TABLE experiences (
  id TEXT PRIMARY KEY,
  error_pattern TEXT,
  solution TEXT,
  confidence REAL,
  source_agent TEXT,
  created_at TIMESTAMP,
  success_rate REAL,
  times_used INTEGER DEFAULT 1
);

CREATE INDEX idx_experiences_pattern ON experiences(error_pattern);
```

### 4. Hermes State (SQLite)

```sql
-- sessions.db
CREATE TABLE sessions (id TEXT, platform TEXT, user_id TEXT, state TEXT, created_at TIMESTAMP);
CREATE TABLE messages (id TEXT, session_id TEXT, role TEXT, content TEXT, timestamp TIMESTAMP);
CREATE TABLE memories (id TEXT, user_id TEXT, key TEXT, value TEXT, timestamp TIMESTAMP);
```

### 5. Stripe/Mercado Pago (External)

```json
// Productos en Mercado Pago
{
  "explorador": { "price": 0, "type": "free" },
  "conquistador": { "price_mxn": 390, "price_adult": 780, "type": "subscription" },
  "agente_ia": { "price_mxn": 690, "price_adult": 1380, "type": "subscription" },
  "imperio": { "price_mxn": 1490, "price_adult": 2980, "type": "subscription" }
}
```

### 6. Gamification Engine (In-Memory)

```python
Player = {
    "id": str,
    "name": str,
    "xp": int,
    "level": int (1-8),
    "badges": List[str],
    "streak": int,
    "last_login": timestamp,
}

Levels = [
    {"level": 1, "name": "Novato", "xp_required": 0},
    {"level": 2, "name": "Aprendiz", "xp_required": 100},
    {"level": 3, "name": "Explorador", "xp_required": 300},
    {"level": 4, "name": "Conquistador", "xp_required": 700},
    {"level": 5, "name": "Estratega", "xp_required": 1500},
    {"level": 6, "name": "Visionario", "xp_required": 3000},
    {"level": 7, "name": "Magnate", "xp_required": 6000},
    {"level": 8, "name": "Leyenda", "xp_required": 12000},
]

Badges = {
    "primer_mensaje": {"name": "Primer Paso", "xp": 10},
    "streak_7": {"name": "Constante", "xp": 100},
    "primer_venta": {"name": "Primer Ingreso", "xp": 200},
    "referir_amigo": {"name": "Conector", "xp": 150},
    "subir_nivel_8": {"name": "Leyenda Viva", "xp": 1000},
}
```

### 7. Revenue Split Model (ABE MUSIC)

| Fuente | Artista | Sello | Distribución |
|--------|---------|-------|-------------|
| Streaming | 70% | 20% | 10% |
| Merch | 60% | 30% | 10% |
| Sync License | 50% | 40% | 10% |

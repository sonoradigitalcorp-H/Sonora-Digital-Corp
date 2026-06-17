# Internal Module Contracts: JARVIS Core Agent Platform

**Feature**: `001-jarvis-core`

## `Orchestrator`

```python
def route_message(message: Message, agents: AgentRegistry) -> OrchestratorResult
def get_agent_for_intent(intent: str, registry: AgentRegistry) -> Agent
def chain_agents(intents: list[str], message: Message) -> list[AgentResult]
```

- Deterministic routing based on intent classification rules
- Returns `AgentResult` with status, response, and trace
- Cannot find agent → returns default agent with logged miss

## `Neo4jStore`

```python
def store_entity(entity: Entity) -> str         # returns node ID
def get_entity(entity_id: str) -> Entity | None
def query_relationships(entity_id: str) -> list[Relationship]
def store_session(session: Session) -> None
def get_session(session_id: str) -> Session | None
```

- Connection pool with retry (3 attempts, exponential backoff)
- Falls back to in-memory dict when Neo4j unavailable
- Concurrent writes use locking

## `QdrantStore`

```python
def upsert(collection: str, points: list[Point]) -> None
def search(collection: str, vector: list[float], limit: int = 10) -> list[ScoredPoint]
def create_collection(collection: str, vector_size: int) -> None
```

- Auto-creates collection on first write if missing
- Vector size configured in startup config

## `Engram`

```python
def store(engram: Engram) -> None
def recall(query: str, limit: int = 5) -> list[Engram]
def promote(engram_id: str) -> Engram | None
def decay_all() -> int  # returns number of decayed engrams
```

- Importance threshold for short→long-term promotion (configurable)
- Max 3 promotion levels (guard against infinite promotion)

## `LLMClient`

```python
async def generate(prompt: str, system: str, stream: bool = True) -> AsyncGenerator[str]
def generate_sync(prompt: str, system: str, timeout: int = 30) -> str
```

- Supports streaming and non-streaming modes
- Configurable endpoint (opencode-go default, OpenRouter optional)
- Timeout handling with graceful cancellation

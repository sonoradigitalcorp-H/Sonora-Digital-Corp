# SDC Architecture Skill

## Overview

Architecture patterns and best practices for Sonora Digital Corp.

## 6-Layer Architecture

```
kernel/        ← Capa 0: identidad, reglas, constitución
infra/         ← Capa 1: infraestructura SSOT
apps/          ← Capa 2: servicios core del sistema
products/      ← Capa 3: lo que SDC vende
clients/       ← Capa 4: clientes externos
portal/        ← Capa visual: Grimoire 3D
ops/           ← Capa transversal: playbooks
state/         ← Capa transversal: estado vivo
reference/     ← Capa transversal: specs cerradas
```

## Golden Rule

**El core NO se mezcla con clientes.**

- Lo que está en kernel/, infra/, apps/ pertenece a SDC
- Productos y clientes importan del core
- Nunca al revés

## Component Design

### Apps Organization (7 Cognitive Levels)

```
apps/
├── act/           # Agentes que ejecutan
├── control/       # Monitoreo y control
├── decide/        # Toma de decisiones
├── learn/         # Aprendizaje y evolución
├── measure/       # Métricas y guardian
├── observe/       # Observabilidad
└── understand/    # Comprensión del contexto
```

### Agent Design

```python
# Pattern: Wrapper
class AgentWrapper:
    def __init__(self, agent):
        self.agent = agent
    
    def execute(self, task):
        # Add pre-processing
        result = self.agent.run(task)
        # Add post-processing
        return result

# Pattern: Dispatcher
class Dispatcher:
    def route(self, request):
        agent = self.registry.get(request.type)
        return agent.execute(request)
```

### Event-Driven Communication

```python
# Publisher
class EventPublisher:
    def publish(self, event):
        self.redis.xadd('events', event)

# Consumer
class EventConsumer:
    def consume(self):
        while True:
            events = self.redis.xread('events', count=10)
            for event in events:
                self.process(event)
```

## Data Storage

### PostgreSQL
- Structured data
- Transactions
- Complex queries

### Redis
- Cache
- Sessions
- Event streams
- Rate limiting

### Qdrant
- Vector storage
- Semantic search
- RAG embeddings

### Neo4j
- Relationships
- Graph queries
- Knowledge graphs

## API Design

### REST API

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/tasks")
async def create_task(task: Task):
    # Validate
    # Process
    # Return
    pass
```

### WebSocket API

```python
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

## Security Patterns

### Authentication

```python
# JWT RS256
from jose import jwt

def create_token(data: dict):
    return jwt.encode(data, private_key, algorithm="RS256")

def verify_token(token: str):
    return jwt.decode(token, public_key, algorithms=["RS256"])
```

### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data():
    pass
```

### Secrets Management

```python
import os

# Never hardcode
API_KEY = os.getenv("API_KEY")

# Use .env files
from dotenv import load_dotenv
load_dotenv()
```

## Testing Patterns

### Unit Tests

```python
def test_feature():
    # Arrange
    input_data = "test"
    
    # Act
    result = feature(input_data)
    
    # Assert
    assert result == "expected"
```

### Integration Tests

```python
@pytest.mark.integration
async def test_with_real_service():
    # This test uses real services
    # Only run in integration environment
    result = await call_service()
    assert result.success
```

### Mock Tests

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('module.external_service') as mock:
        mock.return_value = "mocked"
        result = function_using_service()
        assert result == "mocked"
```

## Deployment Patterns

### Docker

```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
    depends_on:
      - postgres
      - redis
```

### Systemd

```ini
# /etc/systemd/system/app.service
[Unit]
Description=My App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/app
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Checks

```python
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime": time.time() - start_time
    }
```

### Metrics

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('requests', 'Total requests')
REQUEST_LATENCY = Histogram('request_latency', 'Request latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response
```

### Logging

```python
import structlog

logger = structlog.get_logger()

@app.get("/api/data")
async def get_data():
    logger.info("Fetching data", user_id=user_id)
    try:
        data = await fetch_data()
        logger.info("Data fetched", count=len(data))
        return data
    except Exception as e:
        logger.error("Failed to fetch data", error=str(e))
        raise
```

## Documentation

### ADR (Architecture Decision Record)

```markdown
# ADR-001: Use Redis for Caching

## Status
Accepted

## Context
Need fast caching for frequently accessed data.

## Decision
Use Redis as primary cache.

## Consequences
+ Fast reads
+ Simple setup
- Additional dependency
- Memory usage
```

### Spec

```markdown
# SPEC-001: Feature Name

## Overview
What this feature does.

## Inputs
- data: string

## Outputs
- result: object

## Contract
POST /api/feature
{
  "data": "string"
}
Response:
{
  "result": "object"
}
```

# MODEL MAP — Task-to-Model Assignment
## Sonora Digital Corp — AI Model Routing Matrix

---

## Principle
- **Local first**: All inference runs on VPS via Ollama (CPU, no GPU)
- **Fallback**: OpenCode Go API (deepseek-v4-flash) when local is insufficient or too slow
- **Autonomy**: System must function 100% offline if internet is unavailable
- **Latency target**: <3s for embeddings, <10s for chat inference

---

## Model Registry

| ID | Model | Params | RAM (Q4) | Dims | Context | Purpose |
|----|-------|--------|----------|------|---------|---------|
| `embed-local` | nomic-embed-text | 137M | 274MB | 768 | 8K | Embeddings (Qdrant) |
| `chat-local` | qwen2.5:1.5b | 1.5B | ~1.1GB | — | 32K | Chat general |
| `chat-fallback` | deepseek-v4-flash | — | remoto | — | 128K | OpenCode Go API |

---

## Task-to-Model Mapping

### 1. Embeddings & Vector Search
**Model**: `embed-local` (nomic-embed-text)
**Why**: 
- 768-dim vectors → compatible with existing Qdrant `jarvis_knowledge` collection (Cosine, 768d)
- 274MB → fits in RAM alongside full docker stack
- No GPU needed, runs ~50ms per text on CPU
- No internet dependency

**Used by**: 
- JARVIS RAG pipeline (when deployed)
- Hermes memory search
- Semantic search in ABE Music
- All Qdrant vector operations

**When NOT to use**: 
- If we switch to multilingual (100+ languages), swap to `bge-m3` (~1.2GB, 1024-dim)
- If we need higher MTEB score, swap to `gte-Qwen3-8B` (~4.7GB, 4096-dim) — requires more RAM

### 2. Local Chat / Text Generation
**Model**: `chat-local` (qwen2.5:1.5b)
**Why**:
- 1.5B params → ~1.1GB in Q4_K_M → fits in ~11GB VPS alongside Docker containers
- Strong Spanish performance (trained on multilingual data including Spanish)
- Apache 2.0 license — no commercial restrictions
- 32K context window — sufficient for most tasks
- ~3-5s per response on CPU (11GB RAM, 4 cores)

**Used by**:
- Hermes local inference (when OpenCode Go is unavailable)
- n8n AI nodes (brain IA, content generation)
- Ollama API for any local LLM call
- Offline fallback

**When to use fallback**:
- When response time exceeds 5s
- When task requires complex reasoning
- When coding tasks exceed model capability
- When internet is available and speed matters

### 3. Fallback / Primary Cloud
**Model**: `chat-fallback` (deepseek-v4-flash via OpenCode Go)
**Why**:
- Free tier available via OpenCode Go API
- 128K context window
- State-of-the-art reasoning
- No local RAM consumption
- Fast (cloud GPU)

**Used by**:
- OpenClaw primary inference
- Hermes primary inference (when online)
- Complex coding tasks
- Tasks requiring large context (>32K)
- HTML comparison page generation

**When NOT to use**:
- When offline
- When privacy is critical (data leaves VPS)
- During internet outages

### 4. Quantum Class / Creative Text
**Model**: `chat-local` (qwen2.5:1.5b)
**Why**:
- Creative text generation does NOT need the latest model
- 1.5B is sufficient for poetic/philosophical content
- Spanish fluidity is adequate
- Zero latency concern for pre-generated content

**When to use fallback**:
- When generating complex HTML/visual content
- When structured output is required

### 5. System Operations (Healthchecks, Monitoring)
**Model**: `embed-local` (nomic-embed-text) + rule-based (NO LLM needed)
**Why**:
- Health checks don't need an LLM — simple HTTP status codes suffice
- Only use embeddings for semantic log comparison
- Rule-based watchdog scripts use zero model inference
- Saves RAM for production tasks

---

## RAM Budget (VPS: 11GB total)

| Service | RAM | Notes |
|---------|-----|-------|
| OS (Ubuntu 26.04) | ~1.6GB | Base system |
| Docker containers (5) | ~2.5GB | Neo4j, Qdrant, PG, Redis, n8n |
| Ollama (loaded: 1 model at a time) | ~1.4GB | nomic-embed + qwen2.5 swap |
| nginx + system services | ~300MB | |
| **Subtotal** | **~5.8GB** | |
| **Available** | **~5.2GB** | Headroom for spikes |

## Quantization Strategy

- `qwen2.5:1.5b` → Q4_K_M (~1.1GB, best quality/size ratio)
- `nomic-embed-text` → f16 (native format, no quantization needed)
- Future: `phi4-mini:3.8b` → Q4_K_M (~2.5GB) if more reasoning power needed
- Never run two chat models simultaneously — swap as needed

---

## Future Migrations

| When | Current → Target | Reason |
|------|-----------------|--------|
| RAM upgrade >16GB | qwen2.5:1.5b → phi4-mini:3.8b | Better reasoning |
| GPU added | phi4-mini → Qwen2.5-7B | Speed + quality |
| Multilingual need | nomic → bge-m3 | 100+ language support |
| 1024-dim needed | nomic → mxbai-embed-large | Higher precision |

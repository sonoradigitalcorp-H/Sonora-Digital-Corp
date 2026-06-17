# JARVIS Ecosystem — Research Document

## Investigación Técnica del Ecosistema

---

### 1. Stack Tecnológico Investigado y Seleccionado

| Componente | Opciones Evaluadas | Seleccionado | Razón |
|-----------|-------------------|-------------|-------|
| Orquestador | LangChain, LlamaIndex, CrewAI, JARVIS propio | **JARVIS AgentOrchestrator** | Control total, 10 agentes, routing por keywords, sin dependencias externas |
| Base de grafos | Neo4j, ArangoDB, Amazon Neptune | **Neo4j 5.19** | Comunidad, APOC, GraphRAG, maturity |
| Vector store | Qdrant, Pinecone, Weaviate, Milvus, Chroma | **Qdrant** | Open source, Dockerizado, rendimiento, payload indexing |
| Embeddings | OpenAI, Ollama nomic, sentence-transformers | **Ollama nomic-embed-text** | Local, gratis, 768d, sin API key |
| LLM | OpenAI, Anthropic, Gemini, DeepSeek, OpenRouter | **DeepSeek V4 Flash (vía OpenCode)** | Mejor costo/calidad, streaming, razonamiento |
| STT | Whisper, Deepgram, Google Speech | **faster-whisper (base, int8)** | Local, gratis, VAD, CPU eficiente |
| TTS | edge-tts, gTTS, espeak, ElevenLabs | **edge-tts → gTTS → espeak** | Cascada, gratis, sin API key |
| Workflow | n8n, Zapier, Make, Temporal | **n8n** | Open source, 400+ integraciones, self-hosted |
| Skills engine | OpenClaw, custom, Plugin system | **OpenClaw Gateway** | 5,000+ skills comunitarias, SKILL.md estándar |
| Mensajería | Hermes, Telegram API, WhatsApp API | **Hermes Agent** | Multi-canal, gateway, 86 tools, memoria |
| Web UI | React, Next.js, Svelte, FastAPI + Jinja2 | **FastAPI + HTML/CSS/JS** | Sin build step, directo, PWA-ready |
| Desktop control | browser-use, Playwright, Selenium, pyautogui | **browser-use + linux-desktop** | Skills OpenClaw, MCP, xdotool |
| Pagos México | Stripe, Mercado Pago, Bitso, SPEI | **Mercado Pago + Bitso + SPEI** | Multi-proveedor, LatAm optimizado |

### 2. Decisiones Arquitectónicas Clave

#### 2.1 Por qué AgentOrchestrator propio (no LangChain)
- LangChain añade complejidad innecesaria para routing determinista
- Nuestros agentes son ligeros (1 clase = 1 agente)
- Sin dependencia externa = sin breaking changes upstream
- 330 tests aseguran estabilidad

#### 2.2 Por qué OpenClaw como gateway de skills (no plugins custom)
- 5,000+ skills comunitarias ya resuelven 90% de necesidades
- SKILL.md es un estándar portable (OpenClaw, Claude Code, Cursor)
- Skills instaladas vía CLI sin tocar código JARVIS
- Gateway en puerto separado (:18789) = aislamiento

#### 2.3 Por qué Hermes como multi-canal (no bots individuales)
- Una sola API para Telegram, WhatsApp, Discord, Slack
- Gateway unificado con cola de mensajes
- 86 tools compartidas entre canales
- Sesiones persistentes entre canales

### 3. Limitaciones Identificadas

| Limitación | Impacto | Mitigación |
|-----------|---------|------------|
| Whisper base accuracy | ~85% en español | VAD filter + fallback a Google STT |
| JARVIS mono-usuario | Sin aislamiento multi-cliente | Sesiones en Neo4j, perfiles por nicho |
| OpenClaw gateway local | No accesible desde internet | Tunnel ngrok cuando sea necesario |
| Sin Redis | Cache limitado a in-memory | Redis planificado para v4 |
| Sin autenticación multi-factor | Seguridad básica | JWT + Google OAuth implementado |

### 4. Benchmarks Realizados

| Operación | Tiempo | Objetivo | Cumple |
|-----------|--------|----------|--------|
| Chat streaming (primer token) | <500ms | <2s | ✅ |
| Búsqueda semántica Qdrant | <50ms | <100ms | ✅ |
| Consulta Neo4j grafo | <100ms | <200ms | ✅ |
| Generación imagen fal.ai | ~3s | <10s | ✅ |
| Transcripción Whisper (10s audio) | ~2s | <5s | ✅ |
| TTS edge-tts (100 chars) | ~1s | <3s | ✅ |
| Onboarding Mystic completo | <2s | <5s | ✅ |

# Mystik AI API

Asistente de ventas inteligente. Mobile-first PWA con voz + texto.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/products` | Catálogo de productos SDC |
| POST | `/api/chat` | Chat con Mystik (texto → respuesta AI) |
| POST | `/api/leads` | Crear lead en Twenty CRM |
| GET | `/api/leads` | Listar leads (filtrable por tenant) |
| POST | `/api/leads/{id}/qualify` | Calificar lead (BANT) |
| POST | `/api/knowledge` | Buscar en knowledge base (RAG) |
| GET | `/api/tenant/{id}/config` | Configuración por tenant |
| POST | `/api/voice/transcribe` | Whisper STT (audio → texto) |
| POST | `/api/voice/speak` | OpenVoice TTS (texto → audio) |
| WS | `/api/voice/stream` | LiveKit WebRTC signaling |

## Ejemplo: Chat

```bash
curl -X POST http://localhost:5200/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "qué es omnivoice?", "tenant": "sonora"}'
```

## Ejemplo: Crear lead

```bash
curl -X POST http://localhost:5200/api/leads \
  -H "Content-Type: application/json" \
  -d '{"name": "Cliente", "email": "c@example.com", "company": "Empresa SA"}'
```

## Stack

| Componente | Puerto | Tecnología |
|-----------|--------|------------|
| Mystik API | :5200 | FastAPI |
| Lobe Chat UI | :3210 | React/Next.js |
| Twenty CRM | :3000 | GraphQL |
| ChromaDB | :8001 | Vector store |
| LiveKit | :7880 | WebRTC voz |
| PostgreSQL | :5433 | Base de datos |

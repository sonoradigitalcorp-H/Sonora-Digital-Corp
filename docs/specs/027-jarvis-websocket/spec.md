# SPEC-027: Jarvis WebSocket Bridge

**Status:** Draft
**Tier:** 2 (Infrastructure)
**Score:** 78/100
**Created:** 2026-08-02

## 1. Objective

Implementar un puente WebSocket para comunicación en tiempo real entre el navegador del usuario y el backend de Jarvis, soportando entrada de voz, streaming de respuestas, y relay de screenshots.

## 2. User Stories

- Como usuario, quiero que Jarvis responda en tiempo real mientras hablo
- Como desarrollador, quiero un protocolo WebSocket limpio y extensible
- Como operador, quiero métricas de conexión y latencia

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | WS server: WebSocket server con manejo de conexiones | P0 | 8 |
| FR2 | voice_input handling: procesar audio chunks entrantes | P0 | 10 |
| FR3 | response streaming: enviar respuestas chunk por chunk | P1 | 8 |
| FR4 | screenshot relay: enviar screenshots al browser | P1 | 4 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Connection latency | < 50ms |
| NFR2 | Concurrent connections | > 100 |
| NFR3 | Message throughput | > 1000 msg/s |
| NFR4 | Reconnection time | < 2s |

## 5. Protocol Design

```typescript
// Client → Server
interface WSClientMessage {
  type: 'voice_chunk' | 'voice_end' | 'text_input' | 'action_confirm' | 'ping';
  payload: any;
  timestamp: number;
}

// Server → Client
interface WSServerMessage {
  type: 'response_chunk' | 'response_end' | 'screenshot' | 'action_request' | 'error' | 'pong';
  payload: any;
  timestamp: number;
}
```

## 6. Message Flow

```
┌─────────┐                              ┌─────────┐
│ Browser │                              │ Backend │
└────┬────┘                              └────┬────┘
     │  ┌─────────────────────────────┐      │
     │  │ WebSocket Connection        │      │
     │  └─────────────────────────────┘      │
     │                                        │
     │──── voice_chunk (audio data) ────────>│
     │──── voice_chunk ─────────────────────>│
     │──── voice_end ───────────────────────>│
     │                                        │
     │<──── response_chunk (text) ───────────│
     │<──── response_chunk ─────────────────│
     │<──── response_end ───────────────────│
     │                                        │
     │<──── screenshot (base64) ────────────│
     │                                        │
     │──── action_confirm ──────────────────>│
```

## 7. Data Model

```typescript
interface WSConnection {
  id: string;
  tenant_id: string;
  user_id: string;
  connected_at: Date;
  last_message: Date;
  message_count: number;
}

interface VoiceSession {
  connection_id: string;
  chunks: Buffer[];
  started_at: Date;
  language?: string;
}
```

## 8. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| WS | /ws | Main WebSocket endpoint |
| GET | /ws/health | WebSocket server health |
| GET | /ws/stats | Connection statistics |

## 9. Error Handling

- **Connection drop:** Auto-reconnect with exponential backoff
- **Message parse error:** Send error response, continue connection
- **Voice processing timeout:** Send timeout error after 30s
- **Backend overload:** Send backpressure signal to client

## 10. Security Considerations

- JWT authentication on connection handshake
- Tenant isolation per connection
- Message size limits (1MB max)
- Rate limiting per connection
- WSS (TLS) required in production

## 11. Testing Strategy

- Unit tests for message handlers
- Integration tests with mock browser
- Load tests for concurrent connections
- Latency tests for message delivery

## 12. Deployment

- Runs on same port as HTTP server (upgrade)
- Connection pooling for backend services
- Sticky sessions for load balancers

## 13. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Connection failure rate | > 5% |
| Average message latency | > 100ms |
| Memory per connection | > 10MB |
| Dropped connections/min | > 10 |

## 14. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| ws | Library | WebSocket server |
| JWT | Library | Authentication |

## 15. Success Criteria

- [ ] All 4 functional requirements implemented
- [ ] WebSocket connection stable for 1+ hour
- [ ] Voice chunk processing working end-to-end
- [ ] Screenshot relay functional
- [ ] 75% test coverage
- [ ] Reconnection working after network drop
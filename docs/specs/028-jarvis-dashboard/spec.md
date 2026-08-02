# SPEC-028: Jarvis Dashboard UI

**Status:** Draft
**Tier:** 2 (Infrastructure)
**Score:** 80/100
**Created:** 2026-08-02

## 1. Objective

Dashboard 3D interactivo con micrófono continuo para entrada de voz, screenshots inline en tiempo real, feed de acciones, y visualización de mundos de clientes.

## 2. User Stories

- Como usuario, quiero ver a Jarvis "vivo" en un entorno 3D inmersivo
- Como desarrollador, quiero componentes React reutilizables para el dashboard
- Como operador, quiero monitorear actividad de todos los clientes en una vista

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Three.js 3D: escena 3D con avatar de Jarvis | P1 | 16 |
| FR2 | Continuous mic: micrófono siempre activo con visualización | P0 | 10 |
| FR3 | Inline screenshots: mostrar screenshots capturados en feed | P1 | 8 |
| FR4 | Action feed: lista en tiempo real de acciones ejecutadas | P0 | 6 |
| FR5 | Client worlds: vista de múltiples clientes/tenants | P2 | 12 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Initial load time | < 3s |
| NFR2 | 3D render FPS | > 30fps |
| NFR3 | UI responsiveness | < 100ms interaction |
| NFR4 | Memory usage | < 500MB |

## 5. Component Architecture

```
┌─────────────────────────────────────────────────┐
│              Jarvis Dashboard                    │
├─────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐   │
│  │           3D Scene (Three.js)            │   │
│  │  ┌──────────┐  ┌──────────────────┐    │   │
│  │  │  Avatar  │  │  Particle Effects │    │   │
│  │  │  Jarvis  │  │  (voice activity) │    │   │
│  │  └──────────┘  └──────────────────┘    │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────┐    │
│  │  Voice Panel │  │  Action Feed          │    │
│  │  (mic + wave)│  │  (real-time list)     │    │
│  └──────────────┘  └──────────────────────┘    │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Screenshot Gallery (inline preview)     │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Client Worlds (multi-tenant overview)   │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## 6. Data Model

```typescript
interface DashboardState {
  connection: 'connected' | 'disconnected' | 'reconnecting';
  voice: VoiceState;
  actions: ActionItem[];
  screenshots: ScreenshotItem[];
  clients: ClientWorld[];
}

interface VoiceState {
  active: boolean;
  level: number; // 0-1
  language: string;
  transcript?: string;
}

interface ActionItem {
  id: string;
  type: string;
  description: string;
  status: 'running' | 'completed' | 'failed';
  timestamp: Date;
}

interface ScreenshotItem {
  id: string;
  url: string;
  thumbnail: string;
  action_id: string;
  timestamp: Date;
}

interface ClientWorld {
  tenant_id: string;
  name: string;
  status: 'active' | 'idle' | 'offline';
  last_action: Date;
  action_count: number;
}
```

## 7. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /dashboard/config | Get dashboard configuration |
| GET | /dashboard/state | Get current dashboard state |
| WS | /dashboard/ws | WebSocket for real-time updates |

## 8. Error Handling

- **WebSocket disconnect:** Show reconnection indicator
- **3D render failure:** Fall back to 2D mode
- **Screenshot load failure:** Show placeholder
- **High memory usage:** Reduce particle effects

## 9. Security Considerations

- JWT authentication
- Tenant-scoped data only
- No sensitive data in 3D scene
- CSP headers for script security

## 10. Testing Strategy

- Component tests for each React component
- Visual regression tests for 3D scene
- Performance tests for FPS and memory
- E2E tests for voice interaction flow

## 11. Deployment

- Static build served via CDN
- Environment config for API endpoints
- Feature flags for 3D vs 2D mode
- Lazy loading for non-critical components

## 12. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Initial load time | > 5s |
| FPS drop | < 24fps |
| Memory leak | > 800MB |
| Component error rate | > 1% |

## 13. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| Three.js | Library | 3D rendering |
| React | Library | UI framework |
| WebSocket | Protocol | Real-time communication |

## 14. Open Questions

- Should we support WebXR for VR/AR?
- How to handle very large number of client worlds (100+)?
- Optimal screenshot thumbnail size for performance?

## 15. Success Criteria

- [ ] All 5 functional requirements implemented
- [ ] 3D scene rendering at 30+ fps
- [ ] Voice visualization responding to audio
- [ ] Screenshots displaying inline
- [ ] 70% test coverage
- [ ] Load time < 3s on 3G connection
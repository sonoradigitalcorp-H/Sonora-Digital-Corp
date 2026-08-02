# SPEC-026: Jarvis Action Router

**Status:** Draft
**Tier:** 3 (Core)
**Score:** 85/100
**Created:** 2026-08-02

## 1. Objective

Ejecutar acciones reales en el sistema del usuario: automatización de navegador (Playwright), consultas a base de datos, captura de screenshots, síntesis de voz (TTS), con sistema de confirmación para acciones destructivas y navegador persistente.

## 2. User Stories

- Como usuario, quiero que Jarvis abra websites y complete formularios por mí
- Como desarrollador, quiero un sistema de acciones extensible y seguro
- Como operador, quiero logs de cada acción ejecutada con screenshots de auditoría

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | Playwright browser: navegación, click, fill, screenshot | P0 | 16 |
| FR2 | DB queries: SELECT, INSERT, UPDATE con parameterización | P0 | 10 |
| FR3 | Screenshots: capture and store with metadata | P1 | 6 |
| FR4 | TTS direct: text-to-speech via configured provider | P1 | 4 |
| FR5 | Confirmation: confirm before destructive actions | P0 | 8 |
| FR6 | Persistent browser: session reuse across actions | P1 | 8 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Action execution latency | < 5s average |
| NFR2 | Browser startup time | < 3s cold, < 500ms warm |
| NFR3 | Screenshot generation time | < 2s |
| NFR4 | Concurrent action support | > 10 parallel actions |

## 5. Action Types

| Type | Description | Destructive | Confirmation Required |
|------|-------------|-------------|----------------------|
| browser.navigate | Go to URL | No | No |
| browser.click | Click element | No | No |
| browser.fill | Fill form field | No | No |
| browser.screenshot | Capture page | No | No |
| db.select | Read query | No | No |
| db.insert | Insert data | No | No |
| db.update | Update data | Yes | Yes |
| db.delete | Delete data | Yes | Yes |
| tts.speak | Text to speech | No | No |
| system.execute | Run command | Yes | Yes |

## 6. Technical Architecture

```
┌─────────────────────────────────────────────────┐
│              Action Router                       │
├─────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐              │
│  │  Action     │  │  Action     │              │
│  │  Queue      │  │  Executor   │              │
│  └──────┬──────┘  └──────┬──────┘              │
│         │                │                       │
│  ┌──────┴────────────────┴──────┐              │
│  │         Handler Registry     │              │
│  ├──────────────────────────────┤              │
│  │  ┌──────────┐ ┌──────────┐  │              │
│  │  │Playwright│ │ DB       │  │              │
│  │  │ Handler  │ │ Handler  │  │              │
│  │  └──────────┘ └──────────┘  │              │
│  │  ┌──────────┐ ┌──────────┐  │              │
│  │  │Screenshot│ │ TTS      │  │              │
│  │  │ Handler  │ │ Handler  │  │              │
│  │  └──────────┘ └──────────┘  │              │
│  └──────────────────────────────┘              │
│                                                  │
│  ┌──────────────────────────────┐              │
│  │     Confirmation Layer       │              │
│  │  (for destructive actions)   │              │
│  └──────────────────────────────┘              │
└─────────────────────────────────────────────────┘
```

## 7. Data Model

```typescript
interface Action {
  id: string;
  type: string;
  params: Record<string, any>;
  destructive: boolean;
  status: 'pending' | 'confirming' | 'running' | 'completed' | 'failed';
  result?: ActionResult;
  created_at: Date;
  completed_at?: Date;
}

interface ActionResult {
  success: boolean;
  data?: any;
  screenshot_path?: string;
  error?: string;
  duration_ms: number;
}

interface BrowserSession {
  id: string;
  browser: Browser;
  page: Page;
  created_at: Date;
  last_used: Date;
}
```

## 8. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /actions/execute | Execute an action |
| POST | /actions/confirm/:id | Confirm destructive action |
| GET | /actions/:id | Get action status/result |
| GET | /actions/history | Get action history |
| DELETE | /actions/browser/:session_id | Close browser session |

## 9. Error Handling

- **Browser crash:** Auto-restart and retry action
- **DB connection lost:** Queue action and retry with backoff
- **Confirmation timeout:** Cancel action after 30s
- **Screenshot failure:** Log warning, continue action
- **TTS provider down:** Queue for later delivery

## 10. Security Considerations

- Parameterized queries only (no SQL injection)
- Browser runs in sandboxed mode
- Screenshots stored with tenant-scoped paths
- Action history retained for audit (configurable TTL)
- No credentials stored in action params

## 11. Testing Strategy

- Unit tests for each handler
- Integration tests with Playwright test browser
- DB handler tests with test database
- E2E tests for confirmation flow
- Load tests for concurrent actions

## 12. Deployment

- Container with Playwright + browser binaries
- Persistent volume for browser cache
- Environment variables for DB/TTS config
- Resource limits: 2GB RAM, 2 CPU cores

## 13. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Action failure rate | > 10% |
| Browser memory usage | > 1.5GB |
| Average execution time | > 10s |
| Confirmation timeout rate | > 20% |

## 14. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| Playwright | Library | Browser automation |
| PostgreSQL | External | Database queries |
| TTS Provider | External | Text-to-speech |

## 15. Success Criteria

- [ ] All 6 functional requirements implemented
- [ ] Browser session reuse working (warm start < 500ms)
- [ ] Confirmation flow for destructive actions
- [ ] Screenshot capture and storage working
- [ ] 80% test coverage
- [ ] Load test passing: 10 concurrent actions
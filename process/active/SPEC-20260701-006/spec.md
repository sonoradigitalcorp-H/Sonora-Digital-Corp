# SPEC — CI Completo + Mock Tests + Sin Puntos Ciegos

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-006` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Eliminar el punto ciego del CI. Hoy CI prueba planner (70 tests) + ABE Service (9 tests) pero NO los scrapers/collectors. Si un collector se rompe, CI sigue verde. Este spec agrega mock tests para TODOS los collectors, asegurando que cualquier regression sea detectada automaticamente.

---

## 2. Value Driver

reliability, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Mock tests para Deezer collector (httpx mock) |
| FR2 | Mock tests para Apple Music collector |
| FR3 | Mock tests para YouTube collector |
| FR4 | Mock tests para TikTok collector |
| FR5 | Mock tests para Spotify collector |
| FR6 | Mock tests para Wikipedia collector |
| FR7 | Mock tests para sync.py (integration-level) |
| FR8 | Tests de health check con cache |
| FR9 | CI workflow actualizado para correr los nuevos tests |
| FR10 | No menos de 90 tests totales en CI |

---

## 4. Success Criteria

- [ ] 90+ tests pasando en CI
- [ ] Cada collector tiene ≥1 test con mock HTTP
- [ ] sync.py tiene test que verifica fallback chain
- [ ] health cache tiene test que verifica set_health()
- [ ] CI workflow incluye `tests/collectors/` y pasa verde
- [ ] Score ≥60

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260701-006.feature`

---

## 6. Edge Cases

- [EC1] Collector HTTP timeout → debe retornar None, no exception
- [EC2] Mock API devuelve 500 → collector debe fallback graceful
- [EC3] Playwright no disponible → browser collector fallback a mensaje claro
- [EC4] sync.py corre sin internet → datos en cache deben servir

---

## 7. Technical Approach

```
tests/collectors/
├── test_deezer.py        # mock httpx, test search + detail + top_tracks
├── test_apple_music.py    # mock httpx, test search
├── test_youtube.py        # mock subprocess, test yt-dlp output
├── test_tiktok.py         # mock playwright, test HTML parse
├── test_spotify.py        # mock playwright, test raw text parse
├── test_wikipedia.py      # mock httpx, test API response
├── test_sync.py           # mock execute_capability, test fallback chain
└── test_health.py         # test set_health + get_provider_health + is_healthy
```

Herramientas:
- `unittest.mock` / `pytest-mock` para mocks
- `responses` library para mock HTTP (alternativa a httpx mock)
- `pytest-asyncio` para tests async

---

## 8. Dependencies

- pytest-mock (pip install)
- responses (pip install, opcional)
- planner/ package funcional
- scrapers/collectors/*.py existentes

---

## 9. Events to Emit

| Evento | Cuándo |
|--------|--------|
| `collector_test_added` | Nuevo test de collector agregado |
| `ci_test_count_updated` | Total de tests en CI cambia |

---

## 10. Kill Criteria

Si despues de 2 sesiones no se alcanzan 90 tests en CI, pausar y priorizar otra cosa.

---

## 11. Scale Criteria

- Tests de estres para sync.py (100+ artists, verificar timeout)
- Property-based testing para parseo de HTML
- Integration tests con Docker containers reales

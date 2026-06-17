# test-patterns — Cómo Escribir Tests: Unit, Integ, E2E
## CODE · AGENCY OS v1

## IDENTITY
Eres un ingeniero de testing. Sabes exactamente qué testear, cómo, y cuándo cada tipo de test es apropiado.

## MISSION
Cobertura >80% en código determinista. Tests que corren en <30s. Sin falsos positivos.

## TEST PYRAMID

### UNIT (70% de tests) — <10ms cada uno
**QUÉ**: Una función, un método. Aislado de todo.
**CÓMO**:
```python
from unittest.mock import Mock, patch

def test_calculate_revenue_split():
    # Datos de entrada controlados
    streams = 100000
    rate = 0.004  # $0.004 por stream
    expected = 400.0
    
    result = calculate_revenue(streams, rate)
    assert result == expected
    assert isinstance(result, float)
```
**MOCK**: Todo lo externo (LLM, Neo4j, Qdrant, HTTP requests)
**DÓNDE**: `tests/unit/test_[module].py`

### INTEGRATION (20% de tests) — <500ms cada uno
**QUÉ**: Dos o más componentes juntos. Flujo real sin LLM.
**CÓMO**:
```python
def test_api_dashboard_returns_kpis():
    client = TestClient(app)
    response = client.get("/api/abe/dashboard/ceo")
    assert response.status_code == 200
    data = response.json()
    assert "total_streams" in data
    assert data["total_artists"] == 3
```
**MOCK**: Solo el LLM. Neo4j y Qdrant pueden ser reales o test containers.
**DÓNDE**: `tests/integration/test_[feature].py`

### E2E (10% de tests) — <10s cada uno
**QUÉ**: El sistema completo. Playwright en HDMI. Usuario real simulado.
**CÓMO**:
```python
async def test_user_sees_dashboard():
    page = await browser.new_page()
    await page.goto("http://localhost:5174/static/dashboard-abe.html")
    await page.wait_for_selector(".metric")
    text = await page.text_content("h1")
    assert "ABE MUSIC" in text
```
**REAL**: Sin mocks. Sistema completo funcionando.
**DÓNDE**: `tests/e2e/test_[flow].spec.js` o `tests/e2e/test_[flow].py`

## NAMING CONVENTION
```
tests/
├── unit/
│   ├── test_abe_music.py      # Tests ABE Music
│   ├── test_payments.py        # Tests pagos
│   └── test_orchestrator.py    # Tests orquestador
├── integration/
│   ├── test_api_dashboard.py   # API dashboard
│   └── test_api_artists.py     # API artistas
└── e2e/
    ├── test_dashboard_loads.py # Dashboard carga
    └── test_user_login.py      # Login flow
```

## REGLAS
1. Cada función pública tiene al menos 1 test
2. Cada edge case tiene su propio test (input vacío, error, timeout)
3. Tests unitarios NO tocan la red (mocks)
4. Tests de integración NO llaman al LLM (mocks)
5. Tests E2E corren en HDMI (monitor real)
6. `pytest -x` → para en el primer fallo
7. `pytest -q` → output silencioso

# AI Ethics Framework — Native Agent OS

## Core Principles

### 1. Transparency
Every AI action must be traceable. Events are logged. Decisions are explainable.
- `events.jsonl` registra cada acción
- Enterprise Score mide impacto
- Dashboard muestra estado en vivo

### 2. Human Control
Agents propose. Humans decide. Always.
- Toda tool requiere auth JWT
- Humanos pueden kill agents en cualquier momento
- Approvals necesarios para acciones críticas

### 3. Privacy
No datos personales sin consentimiento. KYC obligatorio para contenido sensible.
- Secrets en archivos separados (`.secrets/`)
- No logs con datos de clientes
- KYC pipeline en Mysticverse

### 4. Fairness
Modelos locales (0$/call) y cloud (pago por uso) coexisten. Sin vendor lock-in.
- 3 providers: ollama, opencode-go, openrouter
- Fallback automático si un provider falla
- Cost tracking transparente en FinOps

### 5. Accountability
Cada agente tiene un capability owner. Cada tool tiene un responsable.
- CapabilityRegistry mapea capabilities a owners
- Events registran producer de cada acción
- ADR documenta cada decisión

## Prohibited Actions

| Action | Reason | Enforcement |
|--------|--------|-------------|
| Expose secrets | Security | .secrets/ en .gitignore |
| Delete data without confirmation | Safety | Approvals system |
| Run untrusted code | Security | Docker sandbox |
| Share PII without consent | Privacy | KYC pipeline |
| Bypass rate limits | Fairness | Redis token bucket |

## Content Policy

- No generar contenido NSFW sin KYC verificado
- No impersonar personas reales
- No generar desinformación
- Todo contenido generado debe tener watermark

## Enforcement

```bash
# Review: correr auditoría de seguridad
sdc audit run

# Check: ver qué agents están corriendo
sdc agent list

# Monitor: revisar eventos recientes
sdc event tail
```

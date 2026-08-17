# ADR-0007: Un core, N tenants
Estado: ACEPTADO 2026-08-17
Contexto: Instalar Hermes paralelos (Hermes Millonario), procesos duplicados
(409 Telegram) y edits manuales a config.yaml causaron el desmadre diario.
Decisión:
1. Un solo core Hermes (gateway, config.yaml, .env, VPS) = intocable.
2. Persona/proyecto/empresa nueva = tenant: registro en tenants.json +
   agents/<id>/ (agent.yaml + persona.md) + .env TELEGRAM_<TENANT>_TOKEN +
   Engram space tenant:<id>. NUNCA instalación nueva.
3. config.yaml SOLO lo escribe telegram-tenant-router (--sync).
4. Secrets: .env local = master; VPS = espejo unidireccional. Prohibido
   Environment= en systemd y .bashrc.
5. Deploy unidireccional repo → script → VPS. Nunca se edita en VPS.
Consecuencias: tenant nuevo = checklist 5 min. Cambio al core = ADR + OK del jefe.
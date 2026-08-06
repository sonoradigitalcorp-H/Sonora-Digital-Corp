---
name: analisis-personas
description: Analiza el ecosistema completo de personas: contactos en Postgres, interacciones en Engram, media en carpetas tenant.
---
# Analisis de personas
1. Postgres: SELECT * FROM contacts WHERE name ILIKE
2. Engram: engram search "contacto-<persona>"
3. Interacciones: SELECT * FROM interactions WHERE tenant_id

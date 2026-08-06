---
description: Estado completo del sistema COSUDE: Engram, Postgres, Qdrant, bots, servicios, pendientes
---
1. engram stats
2. PGPASSWORD=sdc_local_dev psql -h localhost -U sdc -d sdc -c "SELECT count(*),tenant_id FROM contacts GROUP BY tenant_id"
3. curl -s localhost:6333/collections | python3 -c "import sys,json;print([c['name'] for c in json.load(sys.stdin).get('collections',[])])"
4. cat ESTADO.md | head -15

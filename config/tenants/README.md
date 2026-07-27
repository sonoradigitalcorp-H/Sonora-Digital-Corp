# Tenants

Cada subdirectorio representa un cliente aislado con su propia configuración, memoria, herramientas y políticas.

## Estructura

```
tenants/
├── _template/          # Plantilla para nuevos tenants (copiar y reemplazar variables)
├── astrotech/          # AstroTech (César Holguín)
├── sonora-digital/     # Sonora Digital Corp (tenant interno)
└── abe-music/          # ABE Music Group (Abraham Ortega)
```

## Estructura por tenant

```
tenants/<id>/
├── prompt.md           # System prompt del agente (personalidad + reglas)
├── branding/           # Colores, logo, tono de voz
├── knowledge/          # Documentos, PDFs, FAQs para RAG
├── memory/             # (Lógico) Namespace para Qdrant/Neo4j
├── skills/             # Skills markdown exclusivas del tenant
├── tools.yaml          # Tools globales permitidas/bloqueadas
├── mcp.yaml            # Servidores MCP específicos del tenant
├── policies.yaml       # Reglas de seguridad y rate limiting
├── workflows/          # Flujos n8n o scripts exclusivos
└── config.yaml         # Configuración general (modelo, idioma, etc.)
```

## Principios

- El Core nunca sabe quién es el tenant. Solo carga su contexto.
- Skills de un tenant no son accesibles desde otro.
- Qdrant colección: `tenant_{id}_memory`
- Neo4j database: `{id}`
- Postgres RLS: filtro por `tenant_id`

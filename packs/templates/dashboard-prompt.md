# Template: Dashboard Prompt for Open Lovable
# Variables: {{pack_name}}, {{industry}}, {{colors}}, {{deploy_target}}, {{pages}}

Crea un dashboard para {{pack_name}} ({{industry}}) usando Next.js 14 (App Router),
shadcn/ui, Tailwind CSS, y Hasura GraphQL como backend.

## Branding
- Colores primarios: {{colors}}
- Tipografía: Inter
- Idioma: Español
- Tono: Profesional y amigable

## Páginas

{{#pages}}
### {{name}}
{{description}}

Componentes:
{{#components}}
- {{.}}
{{/components}}
{{/pages}}

## Integraciones
- Hasura GraphQL en /v1/graphql
- WebSocket para actualizaciones en tiempo real
- WhatsApp para notificaciones
- Exportar reportes a PDF/CSV

## Deploy
- Destino: {{deploy_target}}
- Variables de entorno: NEXT_PUBLIC_HASURA_URL, NEXT_PUBLIC_TENANT_ID

## Requisitos técnicos
- Responsive (mobile-first)
- SSR para SEO en landing pages
- PWA-ready
- Tiempo de carga < 3s
- Lighthouse score > 85

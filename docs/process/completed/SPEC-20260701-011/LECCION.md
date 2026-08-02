# Lecciones — SPEC-20260701-011

## Lo que funciono bien
1. Los collectors ya manejan errores gracefulmente (Instagram, Wikipedia, TikTok)
2. Git MCP y Memory MCP se integraron a HermesClient sin problemas

## Lo que no funciono
1. Instagram, Wikipedia y TikTok son problemas de infraestructura, no de codigo
2. No hay fix de codigo posible para login wall de Instagram o 403 de Wikipedia

## Proxima vez
1. Documentar bloqueos de infraestructura en ARQUITECTURA.md, no ignorarlos
2. Evaluar si Instagram deberia removerse del sync permanentemente

# Research: ABE MUSIC
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| ArtistCRM en Neo4j | Grafos de relaciones, recomendaciones | Overhead de setup | ✅ CRM en grafos |
| Dashboard propio | Control total, KPIs específicos | Desarrollo interno | ✅ Dashboard CEO |
| Revenue Split 70/20/10 | Estándar industria musical | Sin integración con distribuidoras | ✅ Modelo propio |
## Decisión Arquitectónica
- **Selección**: CRM en Neo4j + Dashboard propio + Revenue Split en SQLite
- **Motivo**: White label de SDC para industria musical
## Limitaciones
1. Sin integración con distribuidoras digitales (DistroKid, TuneCore)
2. Revenue tracking es manual — no hay API de Spotify/Apple Music

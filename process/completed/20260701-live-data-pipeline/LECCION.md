# Lección — Live Data Pipeline

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260701-003` |
| **Tier** | 2 |
| **Fecha** | 2026-07-01 |

---

## ¿Qué pasó?

Se construyó un pipeline de datos vivos usando la API pública de Deezer (sin API key) para mantener actualizados los datos de artistas ABE Music y alimentar el pipeline de revenue con eventos reales.

## ¿Qué salió bien?

- [x] TDD funcionó: 12 tests escritos antes del código, 12/12 verdes
- [x] SPEC + Score + Gherkin completados en <30 min total
- [x] Deezer API resultó ser completamente funcional sin auth
- [x] Arquitectura con fallback chain (crw → Python → search) lista para producción
- [x] Zero nuevas API keys en el sistema

## ¿Qué salió mal?

- [x] El test de fallback inicial falló porque el mock no coincidía con el formato real de Deezer search API — se corrigió rápido
- [x] crw no se pudo probar porque requiere compilación Rust (binario prebuilt no disponible)

## ¿Qué haríamos diferente?

- Verificar el schema exacto de Deezer search API antes de escribir el test de fallback
- Considerar usar `responses` library en vez de `mock` para HTTP mocking más realista
- Probar sync real contra Deezer API (no solo mocks) antes del deploy a VPS

## Enriquecimiento Web — Fase 2 (2026-07-01)

Se realizó una segunda ronda de investigación web para enriquecer los datos con fuentes reales:

### Hallazgos Clave

| Dato | Fuente | Detalle |
|------|--------|---------|
| **Fundador** | Corporation Wiki | Abraham Ortega es Presidente de ABE Music Inc (fundada 19 Ene 2018, Compton CA) |
| **Oplaai connection** | Apple Music | "Se Volvieron Locos (En Vivo)" distribuido bajo licencia exclusiva a Oplaai, LLC |
| **Hector Rubio real** | MusicMetricsVault | ~961K monthly listeners, 45,862 Spotify followers, originario de Angostura, Sinaloa |
| **Hector latest** | Apple Music | "Malicia (En Vivo)" - Single lanzado 18 Jul 2025 |
| **Jesus Urquijo streams** | Chartex | 4,635,222 total Spotify streams, 3,341,069 YouTube views |
| **Jesus Urquijo label** | Chartex | "El Abe" distribuido por ABE Music / Colonize Media (538.1K streams) |
| **Javier Arvayo** | Spotify | 981 monthly listeners, album "Abe Music Presenta (2020)" |
| **ABE Music Group IG** | Instagram | @abemusicgroup, 16K followers, 980 posts |
| **Oplaai** | LinkedIn/Billboard | Fundada 2017 en Maricopa, AZ; distribuidora independiente, 3 empleados, 30K IG followers |

### Campos Agregados
- `metadata.label_info` — datos legales del sello (fundador, jurisdicción, revenue estimado)
- `metadata.social` — cuentas oficiales de ABE Music Group
- `metadata.distribution` — conexión Oplaai / Colonize Media
- `artists[].apple_music_url` — enlace directo a Apple Music
- `artists[].distribution` — distribuidor de cada artista
- `artists[].latest_release` — última publicación
- `artists[].youtube_views` — vistas totales en YouTube
- `artists[].shazams` — conteo de Shazams

### Artistas identificados para onboarding futuro
- Roberto Amaya (aparece en "Abe Music Presenta" con Javier Arvayo)
- Christian Ortega (mismo álbum)
- La Séptima Banda (colaboró con Hector Rubio en "Se Volvieron Locos")
- Decreto Norte (misma colaboración)

## Engram Tags

live-data-pipeline, deezer, collector, tdd, spec-003, revenue, abe-music, enrichment, web-research, abraham-ortega, oplaai

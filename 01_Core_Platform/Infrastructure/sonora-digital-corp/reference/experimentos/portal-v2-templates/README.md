# Experimento: Portal v2 — Sistema de Templates

## Fecha
2026-07-22

## Descripción
Segunda versión del portal con arquitectura modular y sistema de templates intercambiables.
El sistema se conoce a sí mismo — genera system.json desde datos reales del sistema.

## Stack
- Three.js (CDN r160) con OrbitControls y CSS2DRenderer
- ImportMap para módulos ES
- HTML/CSS/JS modular autónomo
- Python script para auto-generación de datos

## Archivos
- `portal/index.html` — portal principal (24KB, autónomo)
- `portal/data/system.json` — datos del sistema (auto-generado por scripts/generate-system-json.py)
- `portal/data/templates.json` — configuraciones de escena (5 templates)
- `scripts/generate-system-json.py` — genera system.json desde fleet.yml + constitution/ + products/ + clients/

## Templates disponibles

| Template | ID | Estilo | Partículas | Velocidad | Gamma |
|----------|----|--------|------------|-----------|-------|
| Grimorio Cósmico | cosmic | Espacio profundo | 3000 estrellas | 0.5 | 40 Hz |
| Portal Místico | mystical | Brumas violeta-doradas | 2000 runas | 0.3 | 40 Hz |
| Neón Digital | cyber | Grid futurista | 1500 neón | 0.7 | 40 Hz |
| Raíces Naturales | nature | Verde orgánico | 1000 hojas | 0.2 | 40 Hz |
| Minimal Transparente | minimal | Blanco/gris tenue | 500 puntos | 0.3 | 0 Hz |

## Autoconocimiento
El script `generate-system-json.py` escanea:
- `constitution/` → nodos del kernel
- `fleet.yml` → nodos de infraestructura
- `clients/` → nodos de clientes
- `products/` → nodos de productos
- Datos conocidos de bases de datos

Para regenerar: `python3 scripts/generate-system-json.py`

## Para probar
```bash
cd portal && python3 -m http.server 8080
# Abrir http://localhost:8080
# Click en los botones de template (arriba derecha)
```

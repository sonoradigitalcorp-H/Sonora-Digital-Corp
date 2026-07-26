# Experimento: Brain v1

## Fecha
2026-07-22

## Descripción
Primera versión del Mystic Grimoire servida desde el VPS en `/brain/`.
Portal de creación con ciclo diurno/nocturno, gráfico de fuerza D3.js, y elementos místicos.

## Stack
- Canvas 2D (background particles, smoke, waves, element animations)
- D3.js v7 (force-directed graph overlay)
- CSS puro (glass-morphism panels)
- Tiempo virtual en ciclo de 4 minutos (24h → 4min)
- 4 elementos: Fuego, Aire, Tierra, Agua
- Sigilos: triquetra, pentagrama, flor de la vida, runa de abundancia
- Servido por nginx en el VPS

## Archivo guardado
`reference/experimentos/brain-v1/index.html`

## URL original
http://149.56.46.173/brain/

## Captura
- 39,402 bytes
- 1 archivo HTML autónomo
- Sin dependencias externas excepto D3.js v7 (CDN) y Google Fonts

## Aprendizajes
- El ciclo de tiempo crea una experiencia orgánica que conecta con el usuario
- Los sigilos dan identidad mística que refuerza la marca SDC
- D3.js force-graph funciona bien pero es 2D — limitado para visión de galaxia
- El portal se siente más como dashboard que como universo navegable

---
name: analyze-revenue
description: >
  Genera reportes de regalías de streaming para artistas de ABE Music.
  Consulta datos en ABE Service, calcula splits 70/20/10,
  y produce un resumen ejecutivo.
license: MIT
compatibility: opencode
metadata:
  domain: music
  capabilities: revenue, streaming, crm
---

## Qué hace

Toma el ID de un artista (o "todos") y un período (mes/año),
consulta el revenue real desde ABE Service, aplica el split del contrato,
y devuelve un resumen con:
- Total de streams
- Revenue bruto
- Split: artista / sello / reserva
- Comparativa contra mes anterior
- Top plataformas

## Cuándo usarlo

- Cuando Abraham pregunte "cómo van las regalías?"
- Cuando Luis Daniel pida /revenue
- En reportes automáticos de fin de mes

## Pasos

1. **Identificar el artista**
   - Si es "todos", usa abe-service_abe_list_artists para obtener la lista
   - Si es un nombre, busca el ID exacto

2. **Obtener revenue del período**
   - Usa abe-service_abe_get_artist_revenue con artist_id, month, year
   - El resultado incluye: total_streams, revenue_bruto, revenue_por_plataforma

3. **Obtener contrato**
   - Usa abe-service_abe_get_contract para el split del artista
   - Split por defecto: 70% artista / 20% sello / 10% reserva

4. **Calcular splits**
   - Artista = revenue_bruto * 0.70
   - Sello   = revenue_bruto * 0.20
   - Reserva = revenue_bruto * 0.10

5. **Generar resumen**
   - Texto claro: "Héctor generó $8,000 este mes (2M streams)"
   - Tabla si son varios artistas
   - Destacar cambios vs mes anterior

6. **Si el agente tiene acceso a Telegram**
   - Envía el reporte al chat de Abraham

## Ejemplo de output

```
📊 Reporte de Regalías — Julio 2026

Héctor Rubio
  Streams: 2,150,000
  Revenue bruto: $8,600
  Split (70/20/10):
    -> Artista: $6,020
    -> Sello: $1,720
    -> Reserva: $860

Jesús Urquijo
  Streams: 380,000
  Revenue bruto: $1,520
  Split (70/20/10):
    -> Artista: $1,064
    -> Sello: $304
    -> Reserva: $152

Total sello (Julio): $2,024
```

## Referencias

- ABE Service API: src/abe/revenue.py
- Contratos: src/abe/contracts.py
- Datos de streaming: src/collectors/spotify.py

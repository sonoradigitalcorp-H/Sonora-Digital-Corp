# Mystic Shield — Skill de Diagnóstico

## Descripción
Diagnóstico automatizado de seguridad para empresas. Escanea red, analiza con IA, genera PDF profesional + audio resumen, y envía al CEO por WhatsApp y Email.

## Flujo
1. Recibe IP/subred + nombre empresa
2. Ejecuta escaneo (Naabu/ping sweep)
3. Analiza resultados con LLM (deepseek-v4-flash)
4. Genera PDF profesional (fpdf2) + Audio (edge-tts)
5. Envía WhatsApp al CEO + Email a empresa

## Tools MCP
- `shield_diagnose` — Ejecuta diagnóstico completo
- `shield_send_report` — Reenvía diagnóstico previo

## Endpoints HTTP
- `POST /diagnose` — Iniciar diagnóstico (JSON: target, company_name, ceo_phone, ceo_email, company_email)
- `GET /report/{id}` — Obtener reporte JSON
- `GET /health` — Health check

## Dependencias
- Python: fpdf2, edge-tts, httpx
- Sistema: wacli (WhatsApp), ffmpeg (audio)
- Red: ping, python socket

## ¿Por qué?
El CEO recibe un diagnóstico completo sin tener que interpretar datos técnicos. Mystic habla directamente con él.

# Score — SPEC-20260724-JARVIS-DESKTOP

| Métrica | Peso | Score (0-10) | Justificación |
|---------|------|--------------|---------------|
| Revenue Impact | 1x | 8 | Nuevo SKU comercializable: Jarvis Desktop como producto enterprise; canal directo a escritorio del cliente |
| Scalability | 1x | 8 | Multi-laptop desde diseño: misma codebase corre en N máquinas con identidad propia; plugin system permite extensión sin tocar core |
| Reusability | 1x | 9 | Acciones modulares en `actions/*.py` que son skills reutilizables vía MCP; voice/screen/monitor modules pueden ser invocados por otros agentes SDC |
| Automation Impact | 1x | 9 | Proactividad contextual elimina necesidad de comandos explícitos para monitoreo, recordatorios y alertas; always-on elimina fricción de abrir interfaz |
| Knowledge Impact | 1x | 8 | Cada interacción y contexto de escritorio alimenta Engram vía sync batch; patrones de uso del founder se vuelven datos estratégicos |
| Reliability | 1x | 7 | Modo offline con cola asegura operación sin VPS; SQLite local como respaldo; pero dependencia de wake word local y micrófono introduce puntos de falla |
| Founder Independence | 1x | 9 | Elimina dependencia del VPS como único canal de interacción; founder interactúa con SDC desde su herramienta principal (la laptop); proactividad reduce necesidad de pedir |
| Operational Simplicity | 1x | 7 | Arquitectura clara con layers y plugin system; pero requiere 22+ dependencias y binarios del sistema (tesseract, wmctrl, xdotool) que complican setup inicial |
| Customer Value | 1x | 9 | Asistente siempre presente sin abrir navegador: voz, control de escritorio, notificaciones nativas; la propuesta de valor es inmediatamente perceptible |
| FinOps Efficiency | 1x | 6 | Modo local (whisper.cpp, edge-tts) reduce costos de API comparado con depender 100% de VPS; pero Hermes API calls para agentes SDC remotos agregan costo por ejecución |

**Total: 80/100** → PASA (corte Tier 3: ≥75)

**Veredicto:** Aprobado
**Aprobado por:** score-sh (automático)

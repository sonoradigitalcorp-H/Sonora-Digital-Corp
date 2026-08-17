# Campaña: Nicho Dental (Hermosillo) — Sonora Digital Corp

**Objetivo**: captar 3-5 clínicas/consultorios dentales de Hermosillo como clientes potenciales (paquete low ticket) mandándoles un DM con una imagen de cómo se vería su consultorio con un agente IA.
**Costo máximo**: $0.10-0.15/semana (solo imágenes FAL; DM/follow $0 local).
**Fuente de leads**: `topsearch?query=dentista hermosillo` (verificado: Dra. Paola Ortiz, CLINICA DENTAL GOLDEN, Dra. Vanessa García, etc.)

## Estrategia de DM con imagen (el diferenciador)

1. Buscar 5-10 consultorios dentales de Hermosillo con `discover`.
2. Para cada uno, generar UNA imagen FAL ($0.05) que muestre cómo se vería SU consultorio con un agente IA: recepcionista digital con su logo/colores, "respondiendo WhatsApp 24/7".
3. DM (máx 10/día) con el mensaje + la imagen: "Hola, vi tu consultorio [nombre]. Esto es cómo se vería con un agente que responde tus pacientes 24/7. ¿Te interesa una demo? wa.me/5216623538272".
4. Seguir la cuenta antes del DM (perfil público).

## Guion del DM (plantilla)

```
Hola [nombre] 👋 Soy de Sonora Digital Corp. Vi tu consultorio [nombre].
Te mando una imagen de cómo se vería tu WhatsApp respondiendo a pacientes
24/7 con un agente IA. ¿Quieres ver la demo gratis? Te escribo por wa.me/5216623538272
```

## Pipeline (por prospecto, determinista)

1. `discover --query "dentista hermosillo"` → elegir 5 no privados con bio.
2. `gen_fal.py image "<prompt cinematográfico del consultorio con agente>" /tmp/dental_<user>.png` ($0.05).
3. `dm --execute` con la imagen como adjunto (Playwright: click mensaje → adjuntar → enviar).
4. Registrar contacto en `prospects.json` → `sdc-wacli` hace onboarding cuando respondan.

## Skills involucradas

`sdc-ig-autopilot`, `sdc-campaigns`, `sdc-ai-content-engine` (imagen), `sdc-instagram-composio` (follow-up posts), `sdc-scripts` (guion del DM), `sdc-wacli` (onboarding), `sdc-brand-mystic` (voz/tono).

## Costo realista

- 5 imágenes FAL: $0.25
- 5 DMs + 5 follows: $0 (Playwright)
- Total campaña dental: **~$0.25**

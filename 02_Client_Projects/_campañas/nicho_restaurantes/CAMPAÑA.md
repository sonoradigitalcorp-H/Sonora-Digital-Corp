# Campaña: Nicho Restaurantes (Sonora) — Sonora Digital Corp

**Objetivo**: captar restaurantes/marisquerías de Sonora (Hermosillo, Obregón, Guaymas) mandándoles un DM con imagen de "tu menú respondido 24/7 por IA".
**Costo máximo**: ~$0.25/semana (5 imágenes FAL).
**Fuente de leads**: `topsearch?query=restaurante sonora` (verificado: vivasonorarestaurante, restauranteymariscossonora, palominossonora, muysonora, etc.)

## Diferencial (imagen = demostración)

El DM incluye una imagen FAL del menú/negocio del restaurante atendido por un agente IA: "pide 2 tacos de cabeza" en WhatsApp → el agente confirma orden. Esas son las **imágenes listas de cómo se vería su empresa** que el usuario pidió.

## Guion del DM

```
Hola [nombre] 👋 Vi tu restaurante [nombre] en Instagram.
Así se vería tu WhatsApp tomando pedidos 24/7 con un agente IA
(no pierdes clientes fuera de horario). Demo gratis por wa.me/5216623538272
```

## Pipeline (por prospecto)

1. `discover --query "restaurante sonora"` → 5 no privados.
2. `gen_fal.py image` → imagen del menú con agente IA ($0.05).
3. `dm --execute` con imagen adjunta.
4. Onboarding con `sdc-wacli` cuando respondan.

## Skills

`sdc-ig-autopilot`, `sdc-campaigns`, `sdc-ai-content-engine`, `sdc-hybrid-video` (video corto del "antes/después" de tomar pedido), `sdc-scripts`, `sdc-wacli`.

## Costo realista

- 5 imágenes FAL: $0.25
- DMs + follows: $0
- Total: **~$0.25**

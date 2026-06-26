# YAMI (闇) — Salud Mental Preventiva

**Antes de que sea crisis, que sea conversación.**

Ecosistema preventivo de salud mental para México. Tres capas: MIRU (detección), KIKU (acompañamiento), TOMONI (comunidad).

## Stack

- **Frontend**: HTML + CSS + Vanilla JS (PWA)
- **Hosting**: Vercel (`yami-mx.vercel.app`)
- **Subdominio**: `yami.sonoradigitalcorp.com` (CNAME a Vercel)
- **Colaboración**: Mystic + Noel

## Proyecto en el Monorepo

Todo el código de Yami vive en `products/yami/`:
- `www/` — website (index, miru, kiku, tomoni + assets)
- `constitution/` — reglas y verdad absoluta del proyecto
- `docs/` — documentación y onboarding
- `specs/` — especificaciones SDD
- `memory/` — lecciones y patrones aprendidos
- `scripts/` — utilidades
- `templates/` — plantillas para specs

## Colaboración Mystic + Noel

| Persona | Rol |
|---------|-----|
| **Mystic** (Luis Daniel) | Visión, arquitectura, negocio |
| **Noel** | Desarrollo, implementación, co-creación |

Ver `AGENTS.md` para el protocolo completo.

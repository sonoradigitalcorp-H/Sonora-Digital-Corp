---
id: 009
title: Playwright Automation System
status: draft
type: infrastructure
---

# Spec 009 — Playwright Automation System

## Purpose
Replace broken linux-desktop (xdotool/Wayland) with Playwright for:
- Full browser automation on correct monitor (XWAYLAND1: 1360x768)
- E2E testing of SDC App, landings, payments
- Screenshot evidence for spec verification
- MCP-driven browser control

## Architecture

| Component | Role |
|-----------|------|
| **Playwright Test** | E2E test runner |
| **Playwright MCP** | Browser tool for agent orchestration |
| **Chromium** | Browser engine (Wayland-compatible) |

## Monitor Configuration
- Primary: XWAYLAND1 (1360x768) — HDMI — user workspace
- Secondary: XWAYLAND0 (1920x1080) — laptop
- Chrome launch: `--window-position=0,0 --window-size=1350,700`

## Test Plan

### US1 — App Registration Flow
**Given** un usuario nuevo
**When** completa el formulario de registro
**Then** recibe credenciales (password + api_key)

### US2 — Dashboard por Nicho
**Given** un usuario registrado
**When** inicia sesión
**Then** ve dashboard personalizado según su nicho

### US3 — Landing Pages
**Given** un visitante
**When** navega a /static/{landing}
**Then** recibe HTTP 200 con HTML completo

### US4 — Payments SPEI
**Given** un cliente
**When** consulta /api/payments/spei
**Then** recibe datos de cuenta NVIO

## Implementation
- Tests en `tests/playwright/`
- Config en `playwright.config.ts`
- Script helper en `scripts/playwright-run.sh`

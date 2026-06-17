# CLIENT OS V1 — Sonora Digital Corp

**Propósito**: Cada cliente tiene un sistema. No se pierde nada. No se olvida nada.

---

## CLIENT JOURNEY

```
Lead → Calificado → Propuesta → Cerrado → Onboarding → 
→ Delivery Semanal → Reporte Mensual → Review Trimestral → 
→ Upsell/Referral → (loop)
```

## CLIENT FILE STRUCTURE

Para cada cliente (crear carpeta en `clients/<cliente>/`):

```
clients/<cliente>/
├── profile.md              # Quién es, contacto, empresa, dolor
├── contract.md             # Contrato firmado
├── onboarding.md           # Checklist de onboarding
├── delivery/               # Entregables semanales
│   ├── week-2026-06-15.md
│   ├── week-2026-06-22.md
│   └── ...
├── reports/                # Reportes mensuales
│   ├── 2026-06.md
│   └── ...
├── notes.md                # Notas de llamadas, decisions
└── health.md               # Health score del cliente
```

## ONBOARDING CHECKLIST (para cada cliente nuevo)

- [ ] Contract firmado
- [ ] Primer pago recibido
- [ ] Cuentas/credenciales creadas
- [ ] Welcome pack enviado
- [ ] Primera llamada de setup (30 min)
- [ ] Primer entregable enviado (día 1-3)
- [ ] Check-in día 7: ¿vieron valor?
- [ ] Check-in día 14: feedback

## HEALTH SCORE

```
Score = (delivery_on_time * 0.3) + (support_response * 0.2) + 
        (nps * 0.3) + (usage_growth * 0.2)

> 8: Happy → pedir referral
5-8: Neutral → check-in
< 5: At Risk → intervención inmediata
```

## WEEKLY DELIVERY REPORT (template)

```markdown
# Weekly Delivery — [Cliente] — [Semana]

## Entregado esta semana
- [ ] [Entregable 1]
- [ ] [Entregable 2]

## Métricas
- [Métrica 1]: [valor]
- [Métrica 2]: [valor]

## Próxima semana
- [ ] [Entregable planeado 1]

## Notas
[Problemas, feedback, oportunidades]
```

## CLIENT SUCCESS PLAYBOOK

| Señal | Acción |
|-------|--------|
| Cliente pide algo fuera de plan | ¿Upsell? ¿Feature request? |
| Cliente no abre reportes 2 semanas | Check-in preventivo |
| Cliente menciona presupuesto | Prepárate para renewal con valor |
| Cliente dice "me encanta" | Pide testimonio + referral |
| Cliente se queja | Escalar a founder (tú). Respuesta < 2h. |

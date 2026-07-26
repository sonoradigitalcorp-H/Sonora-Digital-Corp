# Events — SDC Ecosystem

## Registro de Eventos

| Evento | Trigger | Datos | Destino |
|--------|---------|-------|---------|
| `call.inbound.started` | Llamada entrante conectada | `{call_sid, from, to, timestamp}` | cost_tracker, Engram |
| `call.inbound.completed` | Llamada entrante termina | `{call_sid, duration, cost, transcript}` | cost_tracker, Engram |
| `call.outbound.initiated` | Llamada saliente iniciada | `{call_sid, to, agent, lead_name}` | cost_tracker, CRM |
| `call.outbound.completed` | Llamada saliente termina | `{call_sid, duration, cost, result}` | cost_tracker, CRM |
| `token.charged` | Partner cobra a su cliente | `{partner_id, client_id, amount, action}` | cost_tracker |
| `commission.sdc` | SDC toma su comisión | `{partner_id, amount, commission_pct, sdc_earnings}` | cost_tracker (hidden) |
| `xp.awarded` | Usuario gana XP | `{user_id, amount, reason, total_xp}` | gamification_db |
| `level.up` | Usuario sube nivel | `{user_id, level, unlocked_feature}` | gamification_db |
| `referral.commission` | Comisión por referido | `{referrer_id, referee_id, amount, level}` | cost_tracker, multinivel |

# abe-music — ABE MUSIC Inc · Cliente Principal
## CLIENTS · AGENCY OS v1

## CLIENT DATA
- **Nombre**: ABE MUSIC Inc
- **CEO**: Abraham Ortega
- **Paga**: $750/semana ($25/h × 30h)
- **Contacto**: (323) 819-2000
- **Dirección**: 2405 W 153rd St, Compton CA 90220
- **Desde**: ~Mayo 2026 (1 mes sin entregas visibles)
- **Riesgo**: ~$3,000 facturados sin entregable tangible

## ARTISTAS
| Artista | Streams | Revenue | Género | Status |
|---------|---------|---------|--------|--------|
| Jesus Urquijo | 245,000 | $12,110 | Pop Latino | active |
| Hector Rubio | 193,000 | $9,660 | Regional Mexicano | active |
| Javier Arvayo | 101,000 | $5,110 | Urbano | signed |

## KPIS
- **Total streams**: 539,000
- **Total revenue**: $26,880
- **Label share**: $5,376 (20%)
- **API**: `http://localhost:5174/api/abe/dashboard/ceo`
- **Data**: `data/abe-music.json` (90 entradas, 3 reales)

## ENTREGABLES
| Entregable | Estado | URL |
|------------|--------|-----|
| Dashboard CEO | ✅ ENTREGADO | `/static/dashboard-abe.html` |
| API endpoints | ✅ 8 endpoints | `/api/abe/*` |
| Reporte Ejecutivo | ✅ GENERADO | `/static/abe-reporte-ejecutivo.html` |
| Delivery Gate | ✅ ACTIVO | `scripts/abe-delivery-gate.sh` |
| Report Push System | ✅ INSTALADO | `scripts/abe-report-push.sh` |
| Push Gateway | ✅ CONFIGURADO | `scripts/push-to-gateway.sh` |
| Telegram bot | ⏳ Script listo, necesita token | `scripts/abe-telegram-bot.py` |
| WhatsApp | 🔴 Pendiente de configuración | — |
| Hub landing | ✅ CREADO | `/static/abe-music.html` |

## PRÓXIMOS PASOS (ejecución inmediata)
1. ✅ DASHBOARD CREADO + REPORTE — solo falta que Abraham abra la URL
2. ⏳ Regenerar Telegram token (BotFather → /regeneratetoken)
3. ⏳ Desplegar bot: `scripts/abe-telegram-bot.py`
4. 🔴 Configurar WhatsApp business
5. 🔴 CRM de artistas completo con grafos

## REGLA DE ORO
Cada 48h, Abraham debe poder abrir una URL y ver su dinero. Si no, TODO lo demás espera.

## DELIVERY GATE (ejecutar antes de cada "done")
```bash
bash scripts/abe-delivery-gate.sh
```

## AUTO-REPORTE (generar y enviar)
```bash
bash scripts/abe-report-push.sh
```

## ENVIAR MENSAJE A ABRAHAM
```bash
bash scripts/push-to-gateway.sh "🎵 ABE MUSIC update: streams 539K, revenue $26,880"
```

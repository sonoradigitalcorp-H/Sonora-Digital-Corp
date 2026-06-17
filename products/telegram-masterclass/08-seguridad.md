# 8. Seguridad en Telegram

## Anti-Spam
- **Restrict new members:** No send links until N messages
- **Captcha bot:** `/captcha` para verificar humanos
- **Slow mode:** 30s entre mensajes
- **Word filter:** Bloquear palabras clave (spam, estafa)

## Privacidad
- Ocultar numero de telefono en grupo
- No compartir datos de clientes entre grupos
- Usar bots con BBDD separada para datos sensibles

## Backups
```
# Backup de grupos (mensajes)
tg-backup export --group @AzREC --format json

# Backup de bots (codigo + config)
cp -r /home/mystic/products/azrec/telegram/ /backups/
```

## Reglas para Admins
1. Nunca compartir tokens de bots
2. Usar 2FA en cuenta personal
3. Revocar acceso si alguien sale del equipo
4. Logs de acciones del bot (quien, cuando, que)

## Limites de Telegram
| Recurso | Limite |
|---------|--------|
| Miembros por grupo | 200,000 |
| Bots en un grupo | Ilimitado |
| Mensajes por dia por bot | ~1000 (anti-spam) |
| Archivos | 2GB max |

# 9. Configuracion Actual de Nuestros Bots

## Infraestructura
- **Servidor:** mysticpc (laptop, Ubuntu, local network)
- **Telegram Bot Service:** localhost:3003 (3 bots cargados)
- **n8n:** localhost:5678
- **Acceso publico:** ngrok (URL cambia sin dominio estatico)

## Bots Existentes

| Bot | Token | Puerto | Skills |
|-----|-------|--------|--------|
| **Hermes Default** | t.me/HermesSDCBot | 3003 | 97 skills |
| **Hermes Admin** | t.me/HermesAdminBot | 3003 | Admin |
| **Hermes Abraham** | t.me/HermesAbrahamBot | 3003 | Personal |

## Bots por Crear

### AzREC Bot
- **Username:** t.me/AzRECBot
- **Token:** Crear via @BotFather
- **Script:** /home/mystic/products/azrec/telegram/bot-azrec.py
- **Comandos:** start, catalogo, gorras, playeras, info, ayuda
- **Grupo:** t.me/AzREC (comunidad)

### Abe Music Bot
- **Username:** t.me/AbeMusicBot
- **Token:** Crear via @BotFather
- **Script:** basado en bot-azrec.py (adaptar)
- **Grupo:** t.me/AbeMusic (comunidad)

## Proximo Paso: Crear los Tokens
1. Abre @BotFather
2. `/newbot` → AzREC → AzRECBot
3. `/newbot` → Abe Music → AbeMusicBot
4. Copiar tokens a:
   ```
   /home/mystic/products/azrec/telegram/config.json
   ```
5. Ejecutar bot:
   ```bash
   export AZREC_TELEGRAM_TOKEN='token_aqui'
   python3 /home/mystic/products/azrec/telegram/bot-azrec.py
   ```

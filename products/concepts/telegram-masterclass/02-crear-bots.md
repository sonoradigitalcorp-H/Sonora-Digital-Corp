# 2. Crear Bots con @BotFather

## Paso a Paso
1. Abre Telegram, busca `@BotFather`
2. Envia: `/newbot`
3. Pon nombre: `AzREC`
4. Pon username: `AzRECBot` (termina en "bot")
5. Recibes un **token** como:
   ```
   1234567890:ABCdefGHIjklmNOPqrstUVwxyz-1234567
   ```

## Configurar Bot
Con @BotFather:
- `/setdescription` — Texto que aparece al iniciar
- `/setabouttext` — Info del bot
- `/setuserpic` — Foto de perfil (logo AzREC)
- `/setcommands` — Lista de comandos:
  ```
  start - Menu principal
  catalogo - Ver productos
  gorras - Coleccion gorras
  playeras - Playeras y hoodies
  info - Sobre AzREC
  ayuda - Comandos disponibles
  tienda - Ir a la tienda
  ```
- `/mybots` — Gestionar bots existentes

## Donde Hostear el Bot
Nuestra maquina (mysticpc):
```
/home/mystic/products/azrec/telegram/bot-azrec.py
```
Se ejecuta como servicio systemd o dentro del docker de telegram.

Si no tienes servidor 24/7:
- **PythonAnywhere** (gratis, limitado)
- **Railway.app** (gratis con limite)
- **Render.com** (gratis, duerme)

## Tokens de Nuestros Bots
| Bot | Token | Host |
|-----|-------|------|
| Hermes default | 8875376383:AAG4dDoxdUfHqR7oIqW0lC4ygLxfzfg1EMA | localhost:3003 |
| Hermes admin | 7654876543:AAFakeAdmin... | localhost:3003 |
| Hermes abraham | 7654876543:AAFakeAbraham... | localhost:3003 |
| AzREC | CREAR NUEVO | pendiente |
| Abe Music | CREAR NUEVO | pendiente |

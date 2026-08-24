# wacli Auth — Guía de Pairing para Roberto Lara
**Tu Bandera A.C. — Notificaciones WhatsApp**

> [!IMPORTANT]
> Esto solo necesita hacerse **una vez**. Después, `wacli-keepalive.service` mantiene la sesión 24/7.

---

## Prerequisito

Que Luis Daniel (Mystic) esté conectado al VPS vía SSH y que Roberto tenga su WhatsApp abierto en el celular.

---

## Pasos

### 1. Conectar al VPS
```bash
ssh ovh   # alias configurado en ~/.ssh/config
```

### 2. Detener el keepalive temporalmente
```bash
sudo systemctl stop wacli-keepalive
```

### 3. Limpiar sesión anterior (si existe sesión rota)
```bash
rm -rf ~/.wacli/whatsmeow.db ~/.wacli/*.json 2>/dev/null
```

### 4. Iniciar pairing
```bash
/home/mystic/wacli auth --store ~/.wacli
```

Verás en pantalla:
```
QR Code:
[QR code ASCII o código numérico]

Or link with pairing code: XXXX-XXXX
```

### 5. Roberto escanea / ingresa código

**Opción A — QR** (más fácil):
- Roberto abre WhatsApp → **Dispositivos vinculados** → **Vincular dispositivo** → Escanea el QR.

**Opción B — Código de 8 dígitos**:
- Roberto abre WhatsApp → **Dispositivos vinculados** → **Vincular con número de teléfono** → Ingresa el código `XXXX-XXXX`.

### 6. Verificar sesión
```bash
/home/mystic/wacli send text \
  --store ~/.wacli \
  --to 5216623645186@s.whatsapp.net \
  --message "✅ wacli autenticado correctamente en Tu Bandera VPS"
```

Roberto debe recibir el mensaje en su WhatsApp en segundos.

### 7. Reiniciar keepalive
```bash
sudo systemctl start wacli-keepalive
sudo systemctl status wacli-keepalive
```

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `QR expiró` | Correr `wacli auth` de nuevo |
| `Not authenticated` después de reinicio | Verificar que `wacli-keepalive.service` tiene `Environment=HOME=/home/mystic` y `ExecStart=/home/mystic/wacli ...` |
| `store lock` | `rm ~/.wacli/*.lock` y reintentar |
| QR no aparece, solo texto | La terminal no soporta Unicode; usar **Opción B** (código numérico) |

---

## Número de Roberto en el sistema

```
ROBERTO_WA = "5216623645186@s.whatsapp.net"
```

Configurado en:
- `/opt/hermes/tubandera/tubandera-bot.service` → `Environment=ROBERTO_WA=...`
- `02_Client_Projects/Tu_Bandera_Froy/05_FullStack/backend/.env` → `ROBERTO_WA=...`

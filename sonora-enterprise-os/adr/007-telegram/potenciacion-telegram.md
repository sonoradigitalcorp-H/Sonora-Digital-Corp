# Estrategia Telegram — Sonora Digital Corp (Junio 2026)

## Arquitectura 3 Bots

| Bot | Token | Propósito | Modo |
|-----|-------|-----------|------|
| **@sonora_digital_bot** | `8625694089:AAH2z0dnuW9UpqCtH_s_6lPJXh-wuwQVdS0` | Admin CEO — alertas, KPI, comisiones, monitoreo | **Secretary Mode** (conectado a tu cuenta) |
| **@mystic_sdc_bot** | `8626738281:AAFTEWpyEN2Ki59fyKXjxH9BN3V93i9RSTI` | Clientes — ventas, freemium, soporte, funnel | **Guest AI Bot** (mencionable en cualquier chat) |
| **@Gucci_ortega_bot** | `8665900402:AAEwlpCKyi2Hiy5WQrRui5atpOhmqL5msaM` | Abraham Ortega — notificaciones de su empresa | **Secretary Mode** (conectado a Abraham) |

## Telegram Secretary Mode (NUEVO — Mayo 2026)
Conecta un bot a tu cuenta personal. El bot **lee mensajes entrantes y responde en tu nombre** sin marca "enviado por bot". El destinatario cree que eres tú.

**Para @sonora_digital_bot:** 
1. Ve a @BotFather → /mybots → @sonora_digital_bot → Bot Settings → **Business Mode** → Enable
2. En Telegram: Settings → Chat Automation → Conectar @sonora_digital_bot
3. Configura: "Solo chats nuevos" (para no saturar)

## Guest Mode: @mystic_sdc_bot
Cualquier persona puede taguear @mystic_sdc_bot en cualquier chat y obtiene respuesta al instante, sin que el bot sea miembro del grupo.

**Para activar:**
1. @BotFather → /mybots → @mystic_sdc_bot → Bot Settings → **Guest Mode** → Enable

## Bot-to-Bot Communication (NUEVO)
Los bots pueden hablarse entre sí. @mystic_sdc_bot puede consultar a @sonora_digital_bot cuando un cliente pregunta algo que requiere aprobación tuya.

## Mini App sonoradigitalcorp.com
Crear Mini App que se abre desde el perfil del bot:
- Dashboard de servicios
- Facturación
- Estado fiscal
- Freemium sign-up

Esto permite que todo el ecosistema (WhatsApp + Telegram + Web) apunte a sonoradigitalcorp.com.

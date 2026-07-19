# WhatsApp wa.me Link Generator

- **MCP Server**: wacli_mcp
- **Tool**: `whatsapp_create_wa_me_link`
- **Input**: `text` (opcional), `ref_code` (opcional), `utm_source`, `utm_medium`, `utm_campaign`
- **Output**: `{link, phone, ref_code}`
- **Ejemplo**: `whatsapp_create_wa_me_link(ref_code="REF-ABC123", text="Hola, quiero mi negocio en línea")`
- **Descripción**: Genera un link wa.me para el número principal de Sonora Digital Corp (`5216623538272`). El link abre WhatsApp en el teléfono del cliente con un mensaje pre-llenado. Ideal para redes sociales, landing pages, QR codes y campañas de referidos.
- **Permisos**: no requiere autenticación de WhatsApp para generar el link
- **Endpoint**: vía MCP wacli_mcp

## Casos de uso

1. **Link de referido**: `ref_code=REF-ABC123` → `https://wa.me/5216623538272?text=REF-ABC123`
2. **Link con mensaje**: `text=Hola%20mundo` → `https://wa.me/5216623538272?text=Hola%20mundo`
3. **Link con UTM**: utm_source=instagram, utm_medium=bio → link con parámetros UTM para tracking

## Notas

- El mensaje se URL-encodea automáticamente.
- Si solo hay `ref_code`, el texto será el ref_code.
- Si hay `text` + `ref_code`, se concatenan separados por `|`.

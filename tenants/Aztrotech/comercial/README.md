# AztroTech — White-label JARVIS (Sonora Digital Corp)

**Cliente:** César Holguín · Hermosillo, Sonora  
**Plan:** Partner Pro · 500K tokens/mes  
**Estado:** ✅ Configurado · Pendiente de email de César

---

## Instancias creadas

| Instancia | Estado | Cómo acceder |
|-----------|--------|-------------|
| 🌐 **Web Chat** | ✅ Listo | `portal/chat.html` — servirlo con `python3 -m http.server 8080` |
| 🤖 **Telegram Bot** | ✅ Configurado | Bot token en `infra/.env` como `AZTROTECH_BOT_TOKEN` |
| 📱 **WhatsApp** | ✅ Contacto registrado | Número `+5216621072254` |
| 📞 **Call Agent** | ⚠️ Pendiente Twilio | Esperando credenciales Twilio |
| 🧠 **API Chat** | ✅ Endpoint listo | `POST /api/chat` con system prompt AztroTech |

---

## Marca (del Brandbook)

- **Nombre:** AztroTech — "Espiritualidad con Estructura"
- **Colores:** Cobre `#AC6D3E` · Verde Sage `#B6C08B`
- **Tipografía:** Poppins
- **Tono:** Preciso, estratégico, cercano
- **Fundador:** César Holguín · (662) 326 9692 · ventasaztrotech@outlook.com

---

## Para probar ahora mismo

```bash
# 1. Servir el chat web
cd clients/Aztrotech
python3 -m http.server 8080 --directory portal/

# 2. Abrir en el navegador
# http://localhost:8080/chat.html

# 3. Escribir cualquier mensaje
# El chat se conecta al backend JARVIS via /api/chat
```

---

## Para desplegar en producción

```bash
# 1. Configurar dominio (ej: app.aztrotech.com)
# 2. Copiar portal/ al servidor web (nginx)
# 3. Configurar reverse proxy al backend JARVIS
# 4. Ejecutar setup.sh para generar credenciales finales
```

---

## Archivos clave

| Archivo | Contenido |
|---------|-----------|
| `portal/chat.html` | Chat white-label con marca AztroTech |
| `portal/index.html` | Portal completo con header + chat |
| `branding/Brandbook_2026.pdf` | Brandbook oficial |
| `branding/Aztrotech_Logo.png` | Logo PNG |
| `branding/Aztrotech_Logo_Vector.svg` | Logo vectorial |
| `branding/speech-cesar.ogg` | Muestra de voz de César |
| `CALL-AGENT-SPEC.md` | Especificación del Call Agent |
| `SALES-ENGINE-SPEC.md` | Especificación del Sales Engine completo |
| `setup.sh` | Script de setup automatizado |
| `credenciales-aztrotech.txt` | Credenciales de prueba |

---

## Pendiente de César

- [ ] **Email de César** para activación completa del tenant
- [ ] **Número Twilio** para llamadas outbound/inbound
- [ ] **Dominio propio** (cesar.aztrotech.com) para el portal white-label
- [ ] **Redes sociales** conectar (Instagram, Facebook, LinkedIn) para que JARVIS publique

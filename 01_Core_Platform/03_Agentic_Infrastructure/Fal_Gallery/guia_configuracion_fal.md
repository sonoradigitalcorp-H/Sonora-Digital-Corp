# 🛠 Guía de Configuración: Webhook & Log Drain para fal.ai

Para asegurar que **todo** el contenido que se genere con fal.ai (desde cualquier script, agente, Hermes Desktop o el Playground de fal.ai) se descargue e indexe automáticamente en tu **Galería Privada**, sigue estos sencillos pasos:

---

## 1. Servidor de Recepción Webhook

Tu sistema de Galería fal.ai incluye el servidor `fal_webhook_receiver.py` ubicado en:
`01_Core_Platform/03_Agentic_Infrastructure/Fal_Gallery/fal_webhook_receiver.py`

- **Puerto HTTP local**: `8645`
- **Ruta Webhook**: `http://localhost:8645/webhook` (o expuesto vía Cloudflare Tunnel en `https://sonoradigitalcorp.com/webhook/fal`)

---

## 2. Configurar Webhooks Globales en fal.ai Dashboard

1. Inicia sesión en [fal.ai/dashboard](https://fal.ai/dashboard).
2. En el menú lateral izquierdo, ve a **Developer > Webhooks** (o **Developer > Log Drains**).
3. Haz clic en **Add Webhook** / **Create Log Drain**.
4. En **URL de Destino**, ingresa:
   ```text
   https://sonoradigitalcorp.com/webhook/fal
   ```
5. Guarda la configuración.

---

## 3. Uso en Peticiones API Directas

Cuando hagas llamadas directas a la API de fal.ai desde Python o cURL, puedes adjuntar el parámetro `fal_webhook` en la URL de cola para asegurar respuesta asíncrona inmediata:

```python
import urllib.request, json

FAL_KEY = "7f0473fc-..."
WEBHOOK_URL = "https://sonoradigitalcorp.com/webhook/fal"

# Enviar trabajo con webhook adjunto
url = f"https://queue.fal.run/fal-ai/flux/dev?fal_webhook={urllib.parse.quote(WEBHOOK_URL)}"
req = urllib.request.Request(
    url,
    data=json.dumps({"prompt": "A futuristic city in Sonora Mexico"}).encode(),
    headers={"Authorization": f"Key {FAL_KEY}", "Content-Type": "application/json"}
)
```

---

## 4. Acceso a la Galería Web

Puedes abrir la Galería Web en cualquier momento:
- Localmente: Abre en tu navegador `http://localhost:8645/`
- En el VPS / Dominio: `https://sonoradigitalcorp.com/fal_gallery/`

Desde la galería podrás:
- 🖼 Ver todas las imágenes, videos y audios generados.
- 🔍 Buscar por palabras clave del prompt, modelo o ID.
- 📋 Copiar el prompt original con 1 clic.
- ⬇ Descargar el archivo multimedia original en alta resolución.

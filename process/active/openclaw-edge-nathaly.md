# SPEC: OpenClaw Edge — Fourgea México (Nathaly)

**Status**: prototipo
**Target**: Laptop Windows de Nathaly (Contadora, Fourgea México SA de CV)
**Architecture**: Cliente ligero + toda la inteligencia en VPS

---

## Problema

Nathaly recibe diariamente XMLs (CFDI) y PDFs por correo (auxiliar@fourgea.com).
Actualmente los procesa manualmente: descarga, revisa, clasifica, renombra, registra en Excel.
Esto consume ~2-3 horas/día y es propenso a errores (RFC mal escritos, IVA mal calculado).

## Solución

Automatizar el pipeline completo:
- Outlook descarga automáticamente adjuntos de correos específicos
- Un cliente ligero en Windows observa la carpeta y envía archivos al VPS
- El VPS procesa con el fiscal-agent existente (validar CFDI, extraer datos, OCR)
- Resultados vuelven a la laptop como notificación

## Componentes

### 1. OpenClaw Edge Client (Windows)
- Python 3.10+ con watchdog, httpx, win10toast
- Observa `C:\OpenClaw\Inbox\`
- Envía archivos al VPS vía HTTPS POST
- Recibe resultados y muestra notificación Windows
- Mueve archivos a Procesados/Errores según resultado

### 2. Edge Receiver (VPS)
- FastAPI endpoint en el VPS
- Autenticación por API key
- Orquesta el pipeline de procesamiento
- Delega en fiscal-agent existente
- Rate limiting por dispositivo

### 3. Workflow de procesamiento
1. Recibir archivo (XML o PDF)
2. Si XML → parsear CFDI → validar estructura
3. Si PDF → OCR → buscar XML relacionado en Inbox
4. Extraer: RFC emisor/receptor, UUID, IVA, subtotal, total, cliente
5. Clasificar: ingreso/gasto, tipo de operación
6. Renombrar según convención: `{RFC}_{FECHA}_{TIPO}_{UUID[:8]}.{ext}`
7. Registrar en log estructurado (JSON)
8. Retornar resultados al edge client

### 4. Seguridad
- Solo HTTPS (TLS 1.3)
- API key única por dispositivo
- Carpeta aislada: nunca toca nada fuera de C:\OpenClaw\
- Logs de cada operación
- Rate limiting: 60 req/min
- Sin acceso a CONTPAQi ni otras apps de la laptop
- Archivos se procesan solo si son XML o PDF válidos

---

## Flujo

```
Correo (auxiliar@fourgea.com)
    │
    ▼
Regla Outlook: guardar adjuntos de remitentes autorizados
    │
    ▼
C:\OpenClaw\Inbox\{archivo}.xml
    │
    ▼ (watchdog detecta)
OpenClaw Edge Client → HTTPS POST multipart/form-data → VPS
    │
    ▼
Edge Receiver → validar API key → procesar
    │
    ├── XML → fiscal-agent.validate_cfdi()
    │         → extraer metadatos
    │         → buscar PDF relacionado (mismo UUID)
    │
    ├── PDF → OCR (Tesseract)
    │         → buscar XML relacionado
    │
    ▼
Clasificar + Renombrar + Registrar
    │
    ▼
Respuesta JSON → Edge Client → Notificación Windows
    │
    ▼
Mover archivo a Procesados/ o Errores/
```

---

## API

### POST /edge/inbox
```
Headers:
  Authorization: Bearer {EDGE_API_KEY}
  X-Device-ID: nathaly-laptop

Body: multipart/form-data
  file: archivo.xml o archivo.pdf

Response 200:
{
  "success": true,
  "file": "archivo.xml",
  "result": {
    "tipo": "cfdi_ingreso",
    "rfc_emisor": "FOURGEAMEXICO",
    "rfc_receptor": "XXXX010101XXX",
    "uuid": "12345678-1234-1234-1234-123456789abc",
    "total": 15000.00,
    "iva": 2400.00,
    "subtotal": 12600.00,
    "valid": true
  },
  "renamed_to": "FOURGEAMEXICO_2026-07-19_INGRESO_12345678.xml",
  "moved_to": "Procesados"
}
```

### GET /edge/health
```
Response: {"status": "ok", "version": "1.0.0"}
```

---

## Estructura de archivos

```
apps/openclaw-edge/
  edge_client.py        # Cliente Windows (watchdog + HTTPS + notificaciones)
  receiver.py           # Endpoint VPS (FastAPI + orquestración)
  config.example.yaml   # Configuración de ejemplo
  requirements.txt      # Dependencias
  setup.bat             # Instalador Windows

tests/openclaw-edge/
  test_edge_client.py   # Tests del cliente
  test_receiver.py      # Tests del receiver
  conftest.py           # Fixtures (XML/PDF de ejemplo)
```

## Dependencias (Edge Client)
- watchdog >= 3.0
- httpx >= 0.27
- win10toast >= 0.9  (solo Windows)
- PyYAML >= 6.0

## Dependencias (Receiver - ya instaladas en VPS)
- FastAPI
- uvicorn
- httpx (para llamar fiscal-agent)
- python-multipart

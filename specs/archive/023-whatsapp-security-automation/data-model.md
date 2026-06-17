# Data Model: WhatsApp Security and Automation Bridge

**Feature**: `023-whatsapp-security-automation` | **Date**: 2026-06-10

Deriva de las entidades del spec y de las decisiones de `research.md`. Distingue entre **configuración en archivos** (YAML/text), **estado en memoria** (runtime), y **estado de sesión persistido** (cifrado en disco).

---

## Entidades de Configuración (archivos YAML/text)

### BridgeConfig (config.yaml)

Configuración principal del bridge. Cargada al inicio y recargada con SIGHUP.

- `port: number` — puerto HTTP para healthcheck y webhook receiver (default: 3005).
- `log_level: string` — `"debug" | "info" | "warn" | "error" | "critical"` (default: "info").
- `log_dir: string` — directorio para archivos de log (default: `./logs/`).
- `auth_state_dir: string` — directorio para persistencia de sesión cifrada (default: `./config/whatsapp/auth/`).
- `api_key_path: string` — ruta al archivo de API key (default: `./config/whatsapp/api_key.txt`).
- `webhook_timeout_ms: number` — timeout para delivery a n8n (default: 30000).
- `webhook_retry_count: number` — reintentos de webhook (default: 3).
- `webhook_retry_delays_ms: number[]` — delays entre reintentos (default: [10000, 30000, 60000]).
- `max_message_size_chars: number` — máximo tamaño de mensaje de texto (default: 4096).
- `queue_max_size: number` — máximo de mensajes en cola outbound (default: 1000).

**Rate limiting** (anidado):

- `rate_limiting.per_contact.max_messages: number` — máx mensajes por contacto (default: 10).
- `rate_limiting.per_contact.window_ms: number` — ventana en ms (default: 60000).
- `rate_limiting.global.max_messages: number` — máx mensajes globales (default: 100).
- `rate_limiting.global.window_ms: number` — ventana global en ms (default: 60000).
- `rate_limiting.block_after_violations: number` — violaciones antes de bloqueo (default: 3).
- `rate_limiting.block_duration_ms: number` — duración del bloqueo en ms (default: 300000).

**Webhook targets** (anidado, array):

- `webhooks[].keyword: string` — palabra clave para ruteo (null para fallback).
- `webhooks[].url: string` — URL HTTPS del webhook n8n.
- `webhooks[].timeout_ms: number` — timeout para este webhook (opcional, override global).

### AllowlistEntry (allowlist.yaml)

- `phone: string` — número en formato E.164 (ej. `+521234567890`).
- `name: string` — nombre del contacto (opcional, para logging).
- `notes: string` — notas internas (opcional).

**Validación**: el formato E.164 se normaliza: solo dígitos y `+` al inicio. Sin espacios, guiones, paréntesis.

### ApiKey (api_key.txt / env var)

- `key: string` — string alfanumérico (64 caracteres hex, generado con `crypto.randomBytes(32).toString('hex')`).

**Reglas**:
- Se auto-genera si el archivo no existe (INFO log).
- Se puede override con `WHATSAPP_API_KEY` env var.
- Lectura en startup y en SIGHUP para rotación en caliente.
- Comparación con `crypto.timingSafeEqual`.

---

## Entidades de Estado en Memoria (runtime)

### Contact

Representa un contacto de WhatsApp que ha interactuado con el bridge.

- `phone: string` — E.164.
- `name: string | null` — nombre del contacto (de WhatsApp profile, si está disponible).
- `is_authorized: boolean` — calculado del allowlist.
- `is_blocked: boolean` — true si rate limiter bloqueó temporalmente.

**Regla**: `is_authorized` se recalcula en cada mensaje (puede cambiar si el allowlist se recarga).

### Message (inmutable)

Mensaje entrante de WhatsApp.

- `message_id: string` — ID único de WhatsApp.
- `from: string` — E.164 del remitente.
- `body: string` — contenido del mensaje (texto).
- `body_type: "text" | "image" | "video" | "audio" | "document" | "unknown"` — tipo de contenido.
- `has_media: boolean` — true si adjunta medio.
- `media_url: string | null` — URL del medio si aplica (baileys lo descarga temporalmente).
- `mimetype: string | null` — tipo MIME del medio.
- `timestamp: number` — Unix timestamp del mensaje.
- `correlation_id: string` — ID único para tracing (generado por bridge, UUIDv4).

**Ciclo de vida**:
1. Recibido por baileys → Message creado con correlation_id
2. Allowlist check → si falla: log DEBUG, descartar
3. Content filters → si fallan: log WARN, descartar
4. Rate limit check → si excede: queue o descartar
5. Forward a webhook → POST con `{ from, body, timestamp, message_id, contact_name, message_type, has_media }`
6. **Discard** → referencia a Message liberada (GC)

**Regla de privacidad (FR-008)**: El `body` del mensaje NO se almacena en ningún log por encima de DEBUG. Solo existe en memoria durante el paso 1-5.

### RateLimitState

Estado del rate limiter (in-memory, no persistido).

- `per_contact: Map<string, ContactRateState>` — key: E.164.
  - `timestamps: number[]` — timestamps de mensajes en la ventana actual.
  - `violation_count: number` — violaciones en ventana de 10 min.
  - `blocked_until: number | null` — timestamp hasta que el bloqueo expira.
- `global: GlobalRateState`
  - `timestamps: number[]` — timestamps de todos los mensajes.
- `cleanup_interval_ms: number` — intervalo de limpieza de ventanas expiradas (default: 60000).

**Reglas**:
- Ventana deslizante: se filtran timestamps fuera de `now - window_ms`.
- Violación: cuando `timestamps.length >= max_messages` en la ventana.
- Bloqueo: después de `block_after_violations` violaciones en 10 min.
- Reseteo total en reinicio del bridge.

### WebhookDeliveryState

Estado de entrega de un mensaje al webhook.

- `message_id: string`
- `correlation_id: string`
- `target_url: string`
- `attempt: number` — intento actual (1-based).
- `status: "pending" | "success" | "failed" | "timeout"`
- `last_error: string | null` — último error.
- `next_retry_at: number | null` — timestamp del próximo reintento.

### OutboundMessage

Mensaje encolado para envío a WhatsApp (respuesta desde n8n).

- `to: string` — E.164 del destinatario.
- `text: string | null` — texto del mensaje.
- `media_url: string | null` — URL del medio a enviar.
- `media_type: "image" | "audio" | "document" | "video" | null`
- `correlation_id: string` — enlaza con el mensaje entrante original.
- `created_at: number` — timestamp de encolado.

**Reglas**:
- Máximo 1000 mensajes en cola (configurable).
- Si la cola está llena, el mensaje más antiguo se descarta (tail-drop).
- Al reconectar, la cola se vacía enviando los mensajes en orden FIFO.

---

## Entidades de Sesión Persistida (disco, cifrado)

### AuthState (baileys multi-device)

Persistido por baileys automáticamente. Contiene credenciales de sesión cifradas.

Ubicación: `config/whatsapp/auth/` (gitignored, permisos 600).

**Archivos**:
- `creds.json` — credenciales de la sesión multi-device (cifrado baileys interno).
- `app-state-sync-key-*.json` — claves de sincronización de estado.

**Reglas**:
- Nunca se comitea al repositorio.
- Si se corrompe, el bridge debe eliminar el directorio y hacer un nuevo QR scan.
- Permisos del directorio: `700`.

---

## Entidades n8n (gestionadas por n8n, no por el bridge)

Estas entidades son manejadas por los workflows de n8n, no por el bridge. Se documentan aquí para claridad del flujo de datos.

### ClientProfile (n8n storage)

Perfil de cliente creado durante onboarding.

- `phone: string` — E.164.
- `name: string` — nombre.
- `email: string` — correo electrónico.
- `onboarded_at: string` — ISO timestamp.
- `status: "active" | "blocked" | "inactive"`.
- `notes: string` — notas internas.
- `workflow_id: string` — ID del workflow que lo creó.

### ContentItem (n8n storage)

Item de contenido disponible para entrega.

- `id: string` — identificador único.
- `keyword: string` — palabra clave que lo activa.
- `title: string` — título del contenido.
- `type: "audio" | "document" | "video" | "link" | "text"`.
- `url: string | null` — URL del archivo (para media).
- `body: string | null` — contenido textual.
- `permission_group: string` — grupo de permiso requerido.
- `size_bytes: number` — tamaño del archivo.
- `created_at: string` — ISO timestamp.

---

## Relaciones

```text
BridgeConfig 1──* WebhookTarget (keyword → URL mapping)
AllowlistEntry *──1 BridgeConfig (loaded at startup)

Message 1──1 Contact (from phone)
Message 1──1 RateLimitState (checked before processing)
Message 1──* WebhookDeliveryState (retry attempts)

WebhookDeliveryState 1──1 WebhookTarget (routed by keyword)

OutboundMessage 1──1 Message (response to incoming, linked by correlation_id)

AuthState 1──1 WhatsAppBridge (session persistence)

ClientProfile (n8n) *──1 Contact (created from WhatsApp number)
ContentItem (n8n) *──* ClientProfile (access control through permission groups)
```

---

## Reglas de Validación Consolidadas (testeables)

1. Todo contacto debe estar en allowlist para ser procesado (FR-005, fail-closed).
2. Allowlist vacío → todos los mensajes descartados (SC-002).
3. API key debe tener 64 caracteres hex (auto-generado por `crypto.randomBytes(32)`).
4. Comparación de API key debe usar `crypto.timingSafeEqual` (FR-012).
5. El body del mensaje nunca aparece en logs ≥ INFO (NFR-004).
6. Rate limit: violación cuando `timestamps.length >= max_messages` en ventana deslizante (FR-016).
7. Bloqueo: 3 violaciones en 10 min → bloqueo 5 min (FR-018).
8. Webhook delivery: 3 intentos con backoff, timeout 30s (NFR-008).
9. Servidor HTTP bindea a `127.0.0.1` exclusivamente (FR-002, SC-001).
10. Grupo de WhatsApp: OFF por defecto, requiere configuración explícita (FR-007).

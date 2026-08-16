# SAT — Trámites, citas y consultas (ground truth para el asistente)

> Data verificada (sat.gob.mx). El bot la usa para responder con precisión y
> capturar leads; los números/plazos exactos los confirma Nathaly.

## Trámites SAT más solicitados

1. **Constancia de Situación Fiscal** — gratis, se obtiene en línea; la piden
   bancos y contratos. Nathaly ayuda si no aparece el código postal/recolección.
2. **e.firma (ex FIEL)** — firma electrónica; se tramita en línea + acudir a
   módulo para bajar el archivo .pfx y la contraseña (vigencia 4 años).
3. **Contraseña SAT** — acceso al portal; se solicita en línea/recaudación.
4. **Cambio de domicilio fiscal** — se solicita; puede requerir cita.
5. **Solicitud de devoluciones** — de saldos a favor (IVA/ISR) en el portal.
6. **Facturación (CFDI)** — registro de CFDI hasta 4.0; complementos de pago.
7. **Buzón tributario** — el medio oficial de notificaciones del SAT; revisar
   mensualmente para evitar sorpresas.

## Consultas frecuentes de clientes

- "¿Cómo saco mi constancia de situación fiscal?" → Portal SAT → RFC → constancia.
- "No puedo facturar, me sale error" → revisar vigencia de e.firma y contraseña.
- "¿Cuándo presento la declaración?" → mensual (17 del mes siguiente) y anual.
- "No firmé el buzón tributario" → ingresar al portal una vez al año.
- "¿Qué es USO CFDI?" → clave de uso del comprobante puede variar.

## Citas SAT

- Se agendan en sitios sat.gob.mx → Cita (con e.firma o contraseña).
- Antes de la cita: llegar con identificación y RFC.
- Nathaly agenda + acompaña al contribuyente; el bot captura la solicitud.

## Trazabilidad para el bot

- Cuando el lead pida "cita SAT": capturar (fecha + hora, servicio citas_sat) →
  agenda → notifica a Nathaly → confirmación por voz (Dalia).
- Cuando pida "consulta SAT": responder con guía > ofrecer agenda consulta grat.
- Nunca consultar datos específicos del SFH sin autorización explícita.

## Reglas de oro del asistente

1. Información GENERAL sí; detalles de su caso → Nathaly.
2. Montos/plazos exactos → siempre confirmar con Nathaly (no inventar).
3. Si el cliente menciona "multa", "revancha de ley", "auditoría" → escalar a
   Nathaly con URGENCIA (notificación crítica).
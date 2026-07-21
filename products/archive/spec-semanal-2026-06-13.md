# Spec Semanal: Cerrar ABE Music + Activar Ventas

**Semana**: 13 — 19 Junio 2026
**Creado**: 2026-06-12
**Estado**: Draft

**Input**: Diagnóstico total del ecosistema + prioridad de generar ingreso vía ABE Music Inc.

---

## User Stories

### US-001: Abraham Ortega ve el sitio de ABE Music y agenda llamada (P1)

Como Abraham Ortega (CEO de ABE Music Inc), quiero ver un sitio web profesional de mi label que muestre a mis artistas con sus estadísticas reales, para poder mostrarlo a clientes y partners.

**Independent Test**: Se puede abrir https://sonoradigitalcorp-h.github.io/abe-music/ y ver: hero, roster de 3 artistas, servicios, about, formulario de contacto.

**Acceptance Scenarios**:
1. Given el sitio está online, When Abraham abre la URL, Then ve el hero con "Discovering Tomorrow's Music Stars"
2. Given el roster de artistas, When hace clic en Hector Rubio, Then ve su página individual con stats (1.2M listeners, top tracks, bio)
3. Given el formulario de contacto, When completa y envía, Then llega notificación a abraham@abemusicinc.com (vía FormSubmit)
4. Given el sitio es mobile, When abre en celular, Then se ve correctamente (responsive design)

### US-002: Hector Rubio tiene landing + booking individual (P2)

Como Hector Rubio (artista), quiero tener mi propia landing page con booking integrado, para que mis fans puedan contratarme directamente.

**Independent Test**: Se puede abrir `hector-rubio.sonoradigitalcorp.com` (o GH Pages equivalent) y ver bio + botón de booking que envía WhatsApp.

### US-003: Chatbot WhatsApp responde por ABE Music (P2)

Como fan de ABE Music, quiero escribir a un número de WhatsApp y recibir respuesta automática sobre shows, artistas, y bookings.

**Independent Test**: Se envía mensaje al número de ABE Music y se recibe respuesta automática con información de artistas.

### US-004: El sistema no se congela por RAM (P1)

Como usuario de la computadora, quiero que el sistema monitoree recursos y no intente levantar más servicios de los que la RAM permite.

**Independent Test**: `free -m` muestra >500MB disponibles después de arrancar servicios esenciales.

---

## Functional Requirements

- **FR-001**: ABE Music site MUST estar online y accesible 24/7 vía GitHub Pages
- **FR-002**: Cada artista MUST tener su landing individual con bio, stats, y enlace de booking
- **FR-003**: Sistema de booking MUST notificar vía WhatsApp/Telegram al artista
- **FR-004**: Chatbot WhatsApp MUST responder con info precisa del label y artistas
- **FR-005**: Script `deploy.sh` MUST poder desplegar landing + booking en <5 minutos
- **FR-006**: Se MUST monitorear RAM y alertar si <500MB disponible
- **FR-007**: Se MUST alimentar Qdrant con resumen de cada sesión
- **FR-008**: Se MUST generar HTML diario como artefacto de la sesión

## Success Criteria

- **SC-001**: Abraham Ortega confirma 30hrs/semana a $25/hr (ingreso: $750/semana)
- **SC-002**: Hector Rubio tiene landing individual funcional con booking
- **SC-003**: Chatbot ABE Music responde mensajes de prueba correctamente
- **SC-004**: RAM nunca baja de 500MB disponible durante operación normal
- **SC-005**: Qdrant tiene al menos 1 entrada de conocimiento por día de sesión
- **SC-006**: HTML diario se genera y queda accesible localmente

---

## Plan Diario

### Sábado 13 — Preparación

1. Crear spec semanal formal (este documento)
2. Alimentar Qdrant con resumen de sesión de hoy
3. Fix `fal_api.py` (patch _request headers)
4. Verificar puerto 80 (identificar servicio, cerrar si no se necesita)
5. Configurar monitoreo de RAM básico (script + alerta)
6. Probar generación de imagen con fal.ai post-fix

### Domingo 14 — Hector Rubio

1. Ejecutar `deploy.sh` para Hector Rubio con datos reales
2. Configurar booking con WhatsApp notifications
3. Configurar prompt de chatbot para Hector Rubio en Hermes WA API
4. Verificar landing funcional + booking + chatbot

### Lunes 15 — Jesus Urquijo + Javier Arvayo

1. Deploy landing para Jesus Urquijo
2. Deploy landing para Javier Arvayo
3. Configurar booking para ambos
4. Verificar todo funcional

### Martes 16 — Email a Abraham

1. Preparar email profesional con todos los links
2. Enviar a abraham@abemusicinc.com (usando Brevo o directo)
3. Hacer seguimiento vía WhatsApp si hay número
4. Documentar respuesta

### Miércoles 17 — Fixes + Segundo canal

1. Fix GitHub Pages productos (diagnosticar build errored)
2. Contactar Oplaai Music (Victor Zambrano) si aplica
3. Preparar template de email para outreach a otros labels

### Jueves 18 — Seguimiento

1. Dar seguimiento a Abraham si no respondió
2. Si respondió: agendar llamada, preparar propuesta formal
3. Si no: activar segundo prospecto

### Viernes 19 — Cierre

1. Generar reporte semanal
2. Alimentar Qdrant con todo lo aprendido
3. Ejecutar close-loop: memoria, limpieza, auto-mejora
4. Generar diario-2026-06-19.html

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| RAM insuficiente | Alta | Media | Monitorear, cerrar Chrome si es necesario |
| Abraham no responde | Media | Alto | Tener segundo prospecto listo |
| GitHub Pages falla | Baja | Medio | Tener alternativa (servir local con ngrok) |
| WhatsApp bot no configurable | Media | Medio | Tener Telegram como fallback |
| Se acaba la semana sin venta | Media | Alto | Insistir, bajar precio, ofrecer trial |

---

## Assumptions

- Abraham Ortega tiene acceso a internet y puede abrir el sitio web
- El número de WhatsApp de ABE Music está activo
- GitHub Pages se estabiliza (hoy está "building")
- La computadora no se apaga ni se freeze durante la semana
- Hermes API sigue funcionando (hoy responde health check ok)

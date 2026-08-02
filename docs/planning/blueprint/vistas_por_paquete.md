# VISTAS POR PAQUETE - Que Ve Cada Quien

## Resumen Ejecutivo

Este documento define exactamente que ve cada tipo de usuario segun su paquete y rol. La informacion fluye de arriba hacia abajo: Mystic (el creador) tiene visibilidad total, los clientes ven solo lo suyo, y los clientes de los clientes (prospectos) no ven plataforma alguna.

## Matriz de Acceso Completa

### Mistic (Tu) - Vista Admin Total

Mistic es el unico que ve TODO el sistema:
- Panel de todos los tenants activos (14, 50, 200...)
- Todos los agentes corriendo con estados en tiempo real
- Costos reales desglosados por componente (OpenRouter, Kokoro, Whisper, VPS)
- Latencia promedio por tenant y por agente
- Llamadas atendidas vs fallidas por tenant
- Revenue diario/semanal/mensual
- Alertas del sistema (INFO, WARNING, CRITICAL, BUDGET, VENTA)
- Panel de afiliados con comisiones globales
- Pipeline de partnership (solicitudes, entrevistas, aprobaciones)
- Acceso a todos los mundos 3D de todos los tenants
- Acceso al Evolution Engine de todos los tenants
- Facturacion y pagos de todos los clientes
- Logs de seguridad y auditoria
- Estado de la infraestructura (CPU, RAM, disco, red)

### Cliente Despertar ($299 MXN) - Vista Basica

Lo que ve Roberto (contador) en paquete Despertar:
- Dashboard 2D basico con: llamadas atendidas hoy, leads capturados, citas agendadas
- Lista de llamadas con transcripcion y duracion
- Indicador de estado del agente: icono con emoji (zZz = dormido, verde = activo, azul = en llamada)
- Resumen nocturno por WhatsApp: "Hoy tu agente atendi 5 llamadas y agend 2 citas."
- Reporte semanal por email con graficos basicos
- Seccion de configuracion basica: editar FAQ, cambiar canal, ver numero virtual
- **NO VE**: otros tenants, costos reales, metricas de latencia, dashboard 3D, evolucion engine

### Cliente Elevar ($1,499 MXN) - Vista Avanzada 2D

Todo lo de Despertar mas:
- Dashboard avanzado con metricas en tiempo real (se actualiza cada 5 segundos)
- Mapa de calor de llamadas por hora del dia
- Temperamento del prospecto con iconos de cara (feliz, neutral, preocupado, enojado)
- Transcripcion en vivo con highlight de palabras clave
- Estado del agente con indicador visual animado (no 3D, pero con CSS animations)
- Graficos interactivos (hover para detalles)
- Metricas de calidad: empatia detectada, BANT completado, conversion
- Mapa de llamadas outbound con temperatura de cada prospecto
- Seccion de embudo: cuantos en cold, warm, hot, cerrados
- Content factory: ver las 30 piezas del mes con engagement
- **NO VE**: dashboard 3D, otros tenants, costos reales, evolucion engine

### Cliente Soberano (Custom 50K+ MXN) - Vista 3D JARVIS

Todo lo de Elevar mas:
- Dashboard 3D "Hogar del Agente" con Three.js/WebGL
- Escenario 3D del rol del negocio (oficina de contador, restaurante, etc.)
- Avatar del agente con estados animados (dormido, activo, en llamada, procesando)
- HUD overlay con metricas en tiempo real sobre el mundo 3D
- Iluminacion ambiental que cambia con la actividad (oscura = dormido, brillante = activo)
- Sonido ambiente segun estado (ventilador suave = dormido, silencio = en llamada)
- Orbit controls: puede rotar la camara para ver el mundo desde diferentes angulos
- Mini-mapa si tiene multiples agentes (3 avatares en el escenario)
- Transiciones suaves entre estados (lerp)
- Carga rapida: ~200KB gzipped (Three.js + escena)
- **NO VE**: otros tenants, costos reales, evolucion engine (solo ve sus propias metricas)

### Cliente Oraculo (Invitacion) - Mundo Inmersivo + JARVIS Desktop

Todo lo de Soberano mas:
- Interaccion por voz dentro del mundo 3D: puede hablarle a su agente
- Avatar animado completo: camina, gesticula, reacciona a comandos de voz
- Notificaciones ambientales: particula dorada cuando llega un lead
- JARVIS Desktop: aplicacion Electron que corre como widget en su computadora
- Vista multi-tenant: ve los mundos 3D de todos sus sub-clientes en una cuadricula
- Modo noche/dia: la iluminacion del escenario cambia segun la hora real
- Panel de reseller: sub-clientes activos, revenue, comisiones
- Acceso al Evolution Engine de sus propios tenants (puede ver propuestas y aprobar)
- Co-branding assets y materiales de venta
- API key management para sus developers
- Facturacion automatizada de sus sub-clientes

### Prospecto (Cliente del Cliente) - No Ve Nada de Sonora

El prospecto que llama no ve la plataforma Sonora:
- Escucha la voz del agente (clon del dueño del negocio)
- Si pregunta "eres un robot?": el agente responde con honestidad: "Soy un asistente digital de [nombre del negocio], disenado para ayudarte."
- No ve dashboard, no ve Sonora, no ve branding de la plataforma
- En paquetes white-label (Soberano+): todo es marca del cliente

## Diferencias Visuales por Nicho

Cada nicho no solo tiene un escenario 3D diferente, sino toda la interfaz adaptada:

| Elemento | Contador Roberto | Restaurante Felipe | Barberia Luis |
|----------|-----------------|--------------------|--------------|
| Color primario | Azul #1e3a5f | Naranja #f97316 | Negro #111827 |
| Color acento | Blanco | Crema | Dorado |
| Terminologia | Prospectos = "fiscales" | Leads = "comensales" | Leads = "clientes" |
| Dashboard | Profesional corporativo | Calido acogedor | Vintage moderno |
| Iconografia | Grafos, tablas | Platos, mesas | Tijeras, peines |

---

*Sonora Digital Corp - Lo Que Cada Quien Ve*
# language: es
Funcionalidad: Onboarding Flow — Mensajes automáticos de bienvenida
  Como nuevo cliente
  Quiero recibir una guía paso a paso al activar mi cerebro digital
  Para aprender a usar todas mis capacidades

  Escenario: Bienvenida inmediata al activar
    Dado que acabo de activar mi cerebro digital con el código "SDC-A7F3K2"
    Cuando la activación se completa
    Entonces recibo al instante: "¡Bienvenido Juan! Soy tu asistente digital. ¿En qué puedo ayudarte?"
    Y el mensaje incluye mi nombre

  Escenario: Tutorial interactivo a los 5 minutos
    Dado que activé mi cerebro digital hace 5 minutos
    Cuando no he enviado ningún mensaje aún
    Entonces recibo: "¿Sabías que puedo crear fotos con tu cara? Envía 'foto' para probar."
    Y el mensaje incluye un botón de acción rápida

  Escenario: Primer uso guiado
    Dado que soy un cliente nuevo
    Cuando envío mi primer mensaje
    Entonces el asistente responde de forma amigable y guiada
    Y ofrece un tour rápido de las capacidades disponibles

  Escenario: Recordatorio a las 24 horas
    Dado que activé mi plan hace 24 horas
    Cuando no he usado el servicio activamente
    Entonces recibo: "¿Cómo va todo? ¿Necesitas ayuda con algo?"
    Y se ofrece asistencia personalizada

  Escenario: Reporte semanal automático
    Dado que soy un cliente activo
    Cuando se cumple 1 semana desde mi activación
    Entonces recibo: "Tu primera semana: X fotos, Y videos, Z conversaciones. Aquí tienes un resumen."

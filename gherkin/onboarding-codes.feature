# language: es
Funcionalidad: Onboarding por Código — Generación y validación
  Como partner de SDC
  Quiero generar códigos únicos para mis clientes
  Para que activen su cerebro digital con solo enviar el código por WhatsApp

  Escenario: Generar código para nuevo cliente
    Dado que el partner "aztrotech" quiere agregar al cliente "Juan Pérez"
    Cuando genero un código de onboarding
    Entonces recibo un código en formato "SDC-XXXXXX"
    Y el código tiene una validez de 6 horas
    Y el link wa.me está listo para enviar

  Escenario: Código expira después de 6 horas
    Dado un código generado hace 7 horas
    Cuando intento validarlo
    Entonces el sistema responde "Código expirado"
    Y no se activa ningún tenant

  Escenario: Código no puede usarse dos veces
    Dado un código que ya fue usado para activar un cliente
    Cuando intento validarlo de nuevo
    Entonces el sistema responde "Código ya utilizado"

  Escenario: Código inválido es rechazado
    Dado un código "INVALIDO123" que no existe en el sistema
    Cuando intento validarlo
    Entonces el sistema responde "Código no reconocido"

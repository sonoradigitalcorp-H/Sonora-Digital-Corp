# language: es
Característica: Reporte de turno RYE
  Como gerente de producción
  Quiero generar un reporte de turno con tiempos de ciclo, downtime y pendientes
  Para saber el estado real de las celdas de soldadura

  Escenario: Reporte de turno completo
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "reporte de turno celda 3"
    Entonces el bot responde con el reporte de la celda 3
    Y el reporte incluye ciclo de 45s, downtime de 12min y 120 piezas OK
    Y el reporte queda guardado en la memoria del bot

  Escenario: Reporte de turno sin datos
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "reporte de turno celda 7"
    Y la celda 7 no tiene datos registrados
    Entonces el bot pide los datos del turno
    Y ofrece un formato con los campos ciclo, downtime y pendientes

  Escenario: Turno sin especificar
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "reporte"
    Entonces el bot pregunta de qué celda y qué turno

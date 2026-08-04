# language: es
Característica: Experto FANUC
  Como programador de robots FANUC
  Quiero consultar alarmas y procedimientos de robots
  Para diagnosticar y resolver rápido en planta

  Escenario: Diagnóstico de alarma SRVO
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "alarma SRVO-075 en celda 2"
    Entonces el bot responde con el diagnóstico de SRVO-075
    Y el diagnóstico incluye causa probable y acción correctiva
    Y cita la fuente del manual FANUC si está en el conocimiento

  Escenario: Alarma desconocida
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "alarma SRVO-999"
    Y el código SRVO-999 no está en el conocimiento
    Entonces el bot admite no tener información del código
    Y sugiere consultar el manual FANUC oficial

  Escenario: Procedimiento de mantenimiento
    Dado que soy Iván y hablo con el bot
    Cuando escribo: "procedimiento de mantenimiento del R-2000iC"
    Entonces el bot responde con los pasos del mantenimiento
    Y el procedimiento se recupera del conocimiento RAG del tenant rye

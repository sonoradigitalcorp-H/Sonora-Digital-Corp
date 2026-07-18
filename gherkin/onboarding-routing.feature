# language: es
Funcionalidad: Onboarding — Routing por número de teléfono
  Como sistema SDC
  Quiero identificar automáticamente a cada cliente por su número de teléfono
  Para que reciban la experiencia correcta sin preguntar quiénes son

  Escenario: Cliente conocido es identificado automáticamente
    Dado que el número "+5216622681111" está asociado al tenant "aztrotech_cliente_1"
    Cuando el cliente envía "Hola" desde ese número
    Entonces el sistema detecta el tenant automáticamente
    Y responde con el contexto de ese cliente

  Escenario: Número desconocido recibe mensaje de bienvenida
    Dado un número "+5216622681111" que NO está registrado
    Cuando envía un mensaje al bot
    Entonces el sistema responde "¡Bienvenido! ¿Tienes un código de activación?"
    Y ofrece la opción de registrarse

  Escenario: Número bloqueado no recibe respuesta
    Dado un número que está en la lista de bloqueados
    Cuando envía un mensaje
    Entonces el sistema no responde

  Escenario: Partner identificado por su número
    Dado que el número de César está asociado al tenant partner "aztrotech"
    Cuando envía un mensaje
    Entonces el sistema carga las tools de partner
    Y puede ver el dashboard de sus clientes

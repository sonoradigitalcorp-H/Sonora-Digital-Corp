# language: es
Característica: Escenarios de fallo y cambio en robots industriales (RYE)
  Como gerente de producción RYE
  Quiero que la IA diagnostique fallas de robots, cambios de celda, piezas nuevas,
  setups y herramentales de forma correcta
  Para reducir downtime y asistir a Iván en cada escenario

  Escenario: Fallo real del robot por colisión en el hombro
    Dado que soy Iván y reporto "choque en el hombro J2 de la celda 3"
    Cuando el sistema consulta el conocimiento curado de alarmas y mantenimiento
    Entonces el sistema identifica el huérfano como posible SRVO-075 por colisión
    Y recomienda liberar el robot y revisar COLLISION.DAO y reset y home
    Y cita la fuente del manual FANUC si está en el conocimiento

  Escenario: Cambio de celda a nueva pieza
    Dado que soy Iván y digo "cambio de pieza en la celda 2 a la pieza P-450"
    Cuando el sistema consulta el manual de celdas, fixtures y herramentales
    Entonces el sistema da el procedimiento de cambio de pieza
    Y verifica fixture 3-2-1
    Y carga programa correcto
    Y alinea UFRAME/UTOOL
    Y ejecuta dry-run sin pieza
    Y realiza control de primer artículo
    Y recuerda que el fixture de la pieza nueva debe recalibrarse

  Escenario: Setup de herramental nuevo
    Dado que soy Iván y digo "setup del herramental nuevo de soldadura"
    Cuando el sistema consulta celdas y fixtures
    Entonces el sistema indica verificar locators
    Y alinear la referencia del robot
    Y validar tolerancia ±0.05mm antes de producción

  Escenario: Pieza nueva sin procedimiento registrado
    Dado que soy Iván y pregunto por una pieza nueva sin ficha de setup
    Cuando el sistema busca en el índice y en la base de datos de manuales
    Entonces el sistema admite no tener el procedimiento de esa pieza
    Y solicita planos y fixture para registrarla

  Escenario: Backup de configuración antes de intervenir
    Dado que soy Iván y voy a reparar una celda
    Cuando el sistema detecta que no hay backup reciente de parámetros
    Entonces el sistema recomienda hacer Image/File backup antes de tocar el robot
    Y guarda un registro de la intervención en la memoria

  Escenario: Configuración de TCP nuevo soldador
    Dado que soy Iván y pido "calibrar el TCP del soldador nuevo"
    Cuando el sistema consulta el manual de programación y configuración
    Entonces el sistema da el procedimiento de calibración de UTOOL
    Y aclara que un TCP mal calibrado provoca errores de posición

  Escenario: Coordenadas de soldadura desalineadas
    Dado que soy Iván y reporto "la soldadura sale desalineada"
    Cuando el sistema consulta integración IA y calidad
    Entonces el sistema sugiere verificar fixture
    Y revisar referencia UFRAME
    Y revisar calibración de visión Cognex
    Y registrar el defecto como no conformidad menor si afecta la pieza

  Escenario: Especificación técnica de tolerancia
    Dado que soy Iván y pregunto "qué tolerancia requiere la línea"
    Cuando el sistema consulta el manual de integración
    Entonces el sistema responde ±0.05mm para líneas automotrices BMW/Rivian
    Y explica que depende del fixture y calibración

  Escenario: Fallo de visión Cognex
    Dado que soy Iván y reporto "la visión Cognex deja de dar OK"
    Cuando el sistema consulta el manual de integración
    Entonces el sistema sugiere revisar la conexión Ethernet/IP
    Y revisar el timeout
    Y aclara que SRVO-104 suele preceder fallas de visión

  Escenario: Escalamiento por downtime alto
    Dado que soy Iván y reporto "la celda 1 lleva 20 min parada"
    Cuando el sistema aplica la regla de escalamiento
    Entonces el sistema notifica a supervisión (downtime > 15min)
    Y sugiere verificar si es seguridad (SRVO-105/107) para prioridad alta

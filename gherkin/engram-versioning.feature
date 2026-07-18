# language: es
Funcionalidad: Versionado Semántico de Observaciones Engram
  Como desarrollador de Sonora Digital Corp
  Quiero que cada observación tenga una versión semántica automática
  Para rastrear la evolución de decisiones y configuraciones

  Escenario: Versión inicial de un topic_key nuevo
    Dado que no existe ninguna observación con topic_key "architecture/auth-model"
    Cuando guardo una observación con ese topic_key
    Entonces la observación tiene:
      | campo     | valor |
      | version   | "v0.0.1" |
      | sequence  | 1     |
      | topic_key | "architecture/auth-model" |

  Escenario: Incremento de versión por revision_count
    Dado que existe una observación previa en "architecture/auth-model"
    Cuando guardo una nueva observación con el mismo topic_key
    Entonces revision_count se incrementa en 1
    Y version refleja el nuevo revision_count

  Escenario: Cálculo semántico major.minor.patch
    Dado revision_count = 0
    Cuando se calcula la versión
    Entonces version = "v0.0.0"

    Dado revision_count = 1
    Cuando se calcula la versión
    Entonces version = "v0.0.1"

    Dado revision_count = 10
    Cuando se calcula la versión
    Entonces version = "v0.1.0"

    Dado revision_count = 100
    Cuando se calcula la versión
    Entonces version = "v1.0.0"

    Dado revision_count = 247
    Cuando se calcula la versión
    Entonces version = "v2.4.7"

  Escenario: Diferentes topic_keys tienen secuencias independientes
    Dado que guardo obs1 con topic_key "architecture/auth-model"
    Y guardo obs2 con topic_key "git/20260718"
    Cuando consulto las secuencias
    Entonces obs1 tiene sequence = 1
    Y obs2 tiene sequence = 1
    Cuando guardo obs3 con topic_key "architecture/auth-model"
    Entonces obs3 tiene sequence = 2

# language: es
Funcionalidad: Recuperación de Contexto de Proyecto
  Como desarrollador de Sonora Digital Corp
  Quiero preguntar "qué pasó en este proyecto" y obtener un resumen estructurado
  Para retomar el trabajo rápidamente después de pausas

  Escenario: Resumen de últimos 7 días
    Dado un proyecto "sonora-digital-corp" con actividad en los últimos 7 días
    Cuando invoco "engram_context('sonora-digital-corp', days=7)"
    Entonces recibo un JSON con:
      | campo       | tipo       | descripción                    |
      | decisions   | list       | Decisiones del período         |
      | bugs_fixed  | list       | Bugs corregidos                |
      | configs     | list       | Cambios de configuración       |
      | git_activity| string     | Resumen de actividad git       |
      | env_changes | list       | Cambios de variables de entorno|
      | processes   | list       | Procesos activos relevantes    |
      | llm_summary | string     | Resumen ejecutivo en lenguaje natural |

  Escenario: Filtra por tipo de observación
    Dado actividad mixta en el proyecto
    Cuando invoco "engram_context('sonora-digital-corp', days=7, types=['decision', 'bugfix'])"
    Entonces el resultado solo contiene observaciones de tipo "decision" y "bugfix"
    Y no contiene observaciones de tipo "command" o "config"

  Escenario: Período personalizable
    Dado actividad en los últimos 30 días
    Cuando invoco "engram_context('sonora-digital-corp', days=30)"
    Entonces el resumen incluye observaciones de hasta 30 días atrás

    Dado actividad en los últimos 90 días
    Cuando invoco "engram_context('sonora-digital-corp', days=90)"
    Entonces el resumen incluye observaciones de hasta 90 días atrás

  Escenario: Proyecto sin actividad retorna vacío
    Dado un proyecto "proyecto-nuevo" sin observaciones
    Cuando invoco "engram_context('proyecto-nuevo', days=7)"
    Entonces recibo un JSON con:
      | campo       | valor     |
      | decisions   | []        |
      | bugs_fixed  | []        |
      | configs     | []        |
      | git_activity| ""        |
      | env_changes | []        |
      | processes   | []        |
      | llm_summary | "No hay actividad reciente en este proyecto." |

  Escenario: LLM genera resumen ejecutivo automático
    Dado que hay 15+ observaciones en el período
    Cuando invoco "engram_context('sonora-digital-corp', days=7)"
    Entonces "llm_summary" tiene entre 50 y 500 caracteres
    Y menciona al menos 3 eventos clave del período

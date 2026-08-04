# language: es
Característica: Gate RDD (Review-Driven Development)
  Como administrador del sistema RYE
  Quiero que cada cambio de código pase por revisión RDD antes del commit
  Para garantizar calidad y trazabilidad en el proyecto

  Escenario: Commit autorizado con recibo RDD válido
    Dado que el pipeline RDD se ejecutó sobre la feature "rye-fanuc-expert"
    Y que los 4 lentes de revisión completaron con score 85
    Y que no hay hallazgos críticos
    Cuando se genera el recibo RDD
    Entonces el recibo contiene receipt_id y aggregated_score 85
    Y el commit queda autorizado (allowed_to_commit = true)

  Escenario: Commit bloqueado por hallazgo crítico
    Dado que el pipeline RDD se ejecutó sobre la feature "rye-shift-report"
    Y que la revisión detectó un hallazgo de severidad critical
    Cuando se genera el recibo RDD
    Entonces el commit queda bloqueado (allowed_to_commit = false)
    Y el recibo indica la razón del bloqueo

  Escenario: Kill switch desactiva el gate
    Dado que el gate RDD está activo
    Cuando se activa el kill switch en emergencia documentada
    Entonces el gate queda desactivado
    Y se registra la razón y la fecha de activación

  Escenario: Commit sin recibo es rechazado
    Dado que no existe recibo RDD para la feature "rye-process-quality"
    Cuando se intenta hacer commit
    Entonces el commit es rechazado por el gate

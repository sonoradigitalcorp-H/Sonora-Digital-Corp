# language: es
Caracteristica: Evolution Engine (Auto-mejora de Prompts)
  Como sistema Sonora
  Quiero que los agentes se auto-mejoren basandose en metricas reales
  Para que cada semana sean mejores sin intervencion manual

  Escenario: Deteccion de patron de fallo y propuesta de mejora
    Dado que el agente vendedor tiene 20 llamadas en las ultimas 24 horas con score < 0.7
    Y el patron comun es: "el agente no maneja la objecion de precio correctamente"
    Cuando el Evolution Engine corre a las 2:00 AM
    Entonces analiza las 20 transcripciones fallidas
    Y detecta el patron: "objecion precio -> respuesta generica -> prospecto cuelga"
    Y genera una propuesta de mejora del prompt
    Y la envia a Mystic via Telegram con diff del prompt
    Y Mystic puede responder "aprobado" o "rechazado"

  Escenario: Test A/B aprobado y escalado
    Dado que Mystic aprobo la propuesta de mejora
    Y se inicio un test A/B con 20% de trafico al prompt variante
    Y pasan 24 horas
    Y el variante tiene conversion 22% vs control 15%
    Y la confianza estadistica es > 0.90
    Cuando el Evolution Engine analiza los resultados
    Entonces declara ganador al variante
    Y escala el variante al 100% del trafico
    Y registra la evolucion en el historial del agente
    Y la proxima noche los nuevos resultados se mediran contra la nueva base

  Escenario: Test A/B inconclusivo - no se escala
    Dado que el test A/B tiene variante 16% vs control 15%
    Y la confianza estadistica es 0.55 (< 0.90)
    Cuando el Evolution Engine analiza
    Entonces declara inconclusivo
    Y extiende el test 24 horas mas
    Y si sigue inconclusivo: descarta el cambio
    Y notifica a Mystic: "La mejora propuesta no genero impacto significativo."

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Deteccion de patron | < 120s | Analisis de 100 transcripciones |
  # | Propuesta enviada a Mystic | < 3:00 AM | Celery Beat schedule |
  # | Confianza estadistica A/B | > 0.90 | Chi-cuadrado o t-test |
  # | Tiempo de escalado ganador | < 5 min | Prompts reload |
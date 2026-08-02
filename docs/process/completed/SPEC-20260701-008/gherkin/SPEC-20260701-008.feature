Feature: Primer Agente Real con Modelo Local
  Como Luis Daniel
  Quiero que los agentes JARVIS usen deepseek-r1:7b para decidir
  Para que el sistema razone con modelos locales, no scripts lineales

  Scenario: JARVIS llama a Ollama local
    Given llm.py tiene backend Ollama configurado
    When llamo llm.ask("return 1+1", model="deepseek-r1:7b")
    Then recibo respuesta en <10s

  Scenario: AgenteMonitor publica a Redis Stream
    Given AgenteMonitor detecta container_down
    When procesa el evento
    Then Redis Stream agent:messages tiene el evento

  Scenario: AgenteHealer recibe de Redis y decide con Ollama
    Given AgenteHealer escucha Redis Stream
    When recibe container_down para sdc-neo4j
    Then consulta Neo4j por dependencias
    And consulta Ollama por decision
    And ejecuta docker restart o escala

  Scenario: AgenteNotifier envia Telegram
    Given AgenteHealer decide escalar (3 fails)
    When publica resultado critico a Redis
    Then AgenteNotifier recibe y envia Telegram

  Scenario: Decision guardada en Engram
    Given AgenteHealer ejecuta una decision
    When termina (exito o fracaso)
    Then la decision se guarda en Engram con resultado

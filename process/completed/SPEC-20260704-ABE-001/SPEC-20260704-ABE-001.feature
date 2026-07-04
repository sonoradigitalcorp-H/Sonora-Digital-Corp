Feature: SPEC-001 Cleanup + Migration ABE Music OS Foundation

  Scenario: Duplicados eliminados
    Given el proyecto en su estado actual
    When se ejecuta la limpieza de duplicados
    Then agents/agents/ no existe
    And sonora-enterprise-os/skills/vertical/ no existe

  Scenario: opencode.json reducido a 4 agentes
    Given opencode.json actualizado
    When se cuentan los agentes en la seccion "agent"
    Then hay exactamente 4 agentes: mystic, hermes, openclaw, builder
    And ningun otro agente aparece en la seccion "agent"

  Scenario: Provider opencode configurado, ollama removido
    Given opencode.json actualizado
    When se lee la seccion "provider"
    Then "opencode" existe como provider
    And "ollama" no existe como provider

  Scenario: Modelo default apunta a opencode
    Given opencode.json actualizado
    When se lee "model"
    Then es "opencode/deepseek-v4-flash-free"
    And "small_model" es "opencode/mimo-v2.5-free"

  Scenario: Todos los agentes usan modelos opencode
    Given opencode.json con 4 agentes
    When se revisa el modelo de cada agente
    Then mystic usa "opencode/deepseek-v4-flash-free"
    And builder usa "opencode/north-mini-code-free"
    And hermes no tiene modelo explicito (usa default)
    And openclaw no tiene modelo explicito (usa default)

  Scenario: Skills de proceso existen
    Given se creo skills/process/
    When se listan los archivos .skill.md
    Then existen los 8 archivos: sdd-orchestrator, sdd-spec, sdd-design, sdd-apply, sdd-verify, sdd-archive, auto-doc, gsd

  Scenario: Ollama solo tiene embeddings
    Given se eliminaron los modelos LLM locales
    When se ejecuta ollama list
    Then solo aparece nomic-embed-text como unico modelo

  Scenario: mystic responde correctamente
    Given mystic configurado con opencode/deepseek-v4-flash-free
    When se envia un mensaje de prueba
    Then responde sin errores y sin timeout

  Scenario: Commands funcionan
    Given opencode.json con la nueva configuracion
    When se ejecuta el comando /status
    Then responde sin errores

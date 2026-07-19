Feature: Próxima sesión — calidad y consistencia del sistema

  Scenario: Registry consistente
    Given agents/registry.yaml define los agentes del sistema
    When se ejecutan los evals estructurales
    Then test_cap_06_agents_have_capabilities pasa sin error
    And todos los agentes referenciados en capabilities/index.yaml existen en registry

  Scenario: CI ejecuta tests
    Given un PR a main o push a main
    When CI corre en GitHub Actions
    Then pytest tests/ evals/ memory/tests/ se ejecutan
    And ruff lint corre
    And promptfoo eval se ejecuta
    And resultados de promptfoo se suben como artifact

  Scenario: Env vars documentadas
    Given el equipo necesita configurar el proyecto desde cero
    When lee .env.example en la raíz
    Then todas las variables de entorno están listadas con secciones agrupadas
    And ninguna variable sensible tiene valor real hardcodeado

  Scenario: Export Obsidian continuo
    Given el vault Obsidian está en ~/Documents/sdc-brain-vault
    When el systemd service engram-obsidian-export está activo
    Then exporta observaciones, sesiones, proyectos, y grafos cada 5 minutos
    And el tracking incremental evita re-exportar IDs ya procesados

  Scenario: Evaluación unificada
    Given el desarrollador quiere ejecutar todas las evaluaciones
    When ejecuta make eval
    Then make eval-structural corre los 35 tests de evals estructurales
    And make eval-promptfoo corre los 12 tests de calidad LLM
    And los resultados son consistentes y reportables

Feature: Conocimiento exacto anti-alucinación (OKF)
  Scenario: Cálculo definido en concepto
    Given el tenant "Aztrotech" tiene el concepto "aztrotech.pricing"
    When el agente responde "cuánto cuesta la instalación de antena comercial"
    Then el corpus usado es "okf"
    And el contexto contiene el valor exacto 3200
    And la respuesta cita el concept_id

  Scenario: Memoria experiencial vía RAG
    Given el tenant "Aztrotech" tiene memoria en Qdrant
    When el agente responde "qué reserva pidió Aztrotech"
    Then el corpus usado es "rag"
    And el contexto se marca como aproximado

  Scenario: Aislamiento entre tenants
    Given el tenant "Nathaly_Contabilidad"
    When se listan sus conceptos
    Then "aztrotech.pricing" NO aparece

  Scenario: Contrato de honestidad
    Given ninguna capa tiene el dato pedido
    When el agente responde "MRR de Nathaly en diciembre"
    Then el corpus es "none"
    And la única respuesta permitida es "no tengo datos verificados"

# language: es
Funcionalidad: Cost Intelligence — Tracking de costos reales por tenant
  Como dueño de SDC
  Quiero saber exactamente cuánto cuesta cada cliente/tenant en tiempo real
  Para poder cobrarles de forma dinámica y mantener márgenes saludables

  Escenario: Registrar costo de LLM call
    Dado el tenant "aztrotech_cliente_1"
    Cuando se ejecuta una llamada LLM con modelo "gpt-4o-mini", 450 tokens in, 120 tokens out
    Y el costo calculado es $0.0021
    Entonces el sistema registra el costo en cost_log con tenant_id y timestamp

  Escenario: Obtener resumen de costos de un tenant
    Dado que el tenant "tenant_a" tiene operaciones registradas por $3.50
    Cuando consulto get_tenant_costs("tenant_a", 30)
    Entonces recibo total_cost_usd = 3.50
    Y el breakdown incluye llm_chat y generate_image
    Y el by_provider muestra openrouter y fal_ai

  Escenario: Calcular costo de LLM antes de ejecutar
    Dado que quiero usar "claude-3.5-sonnet" con 2000 tokens in y 1000 tokens out
    Cuando consulto calculate_llm_cost
    Entonces recibo cost_usd = 0.021
    Y puedo decidir si usar ese modelo o uno más barato

  Escenario: Alerta cuando un cliente cuesta más de lo que paga
    Dado que un cliente paga $19/mes
    Y su costo real en cost_log es $25/mes
    Cuando se ejecuta el reporte
    Entonces el sistema alerta: "Cliente X está en pérdida: $25 de costo vs $19 de ingreso"

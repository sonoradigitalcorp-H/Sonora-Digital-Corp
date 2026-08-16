# Regresión del Chat con Voz — Hermosillo Contabilidad (@HermosilloCont_bot)
# Spec-driven: Gherkin → BDD (escenarios de regresión de audio + filtros de respuesta)

Feature: Conversación con voz no se auto-repite ni hace eco
  Como cliente del orbe de Hermosillo Contabilidad
  Quiero que la conversación con voz responda UNA sola vez por consulta
  Para que los audios no se revuelvan ni el bot se conteste a sí mismo

  Background:
    Given el orbe web está servido en https://sonoradigitalcorp.com/hermosillo.html
    And el webhook /chat responde con una sola respuesta por query

  Scenario: Un solo envío por consulta (single-flight)
    Given el usuario escribe "buenas noches"
    When presiona Enter (o el botón Enviar) N veces rápidas en < 500ms
    Then SOLO se hace 1 fetch al /chat
    And SOLO se muestra 1 mensaje del bot
    And solo se reproduce 1 audio de respuesta

  Scenario: El micrófono no se escucha a sí mismo (no-loop)
    Given el micrófono está activo y el bot reproduce su respuesta de voz
    When el audio del bot termina
    Then el micrófono NO se reactiva automáticamente
    And no se envía ningún mensaje nuevo sin intervención del usuario

  Scenario: El bot no repite el texto del usuario (eco)
    Given el usuario envía "Buenas noches"
    When la respuesta del servidor es idéntica al texto del usuario
    Then se reemplaza por una respuesta de rescate ("Te escucho... ¿me cuentas más?")
    And no se muestra el eco como si fuera respuesta del bot

  Scenario: Respuestas bot duplicadas consecutivas
    Given el bot respondió "Te escucho. ¿Me cuentas un poco más...?"
    When la nueva respuesta es idéntica a la anterior texto en texto
    Then se añade el CTA de paquetes a la segunda ("¿Quieres ver los paquetes?")
    And no hay dos burbujas de bot idénticas seguidas

  Scenario: Múltiples audios nunca se solapan
    Given una respuesta de voz está reproduciéndose
    When llega una nueva respuesta
    Then el audio anterior se cancela (speechSynthesis.cancel + currentAudio.pause)
    And solo se reproduce el audio más reciente

  Scenario: Campos filtrados antes del LLM
    Given el usuario envía un mensaje con posible prompt-injection
    When pasa por sanitize_for_llm
    Then se bloquea con mensaje de seguridad
    And NO llega al clasificador LLM

  Scenario: Paquete solicitado
    Given el usuario pregunta "cuánto cuesta el paquete"
    When la lógica detecta la keyword de paquetes
    Then se muestran los 3 paquetes (Orden/Control/Crecimiento)
    And NO se inventan precios (derivan a Nathaly por WhatsApp)
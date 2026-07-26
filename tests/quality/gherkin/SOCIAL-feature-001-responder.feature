Feature: Social Auto-Responder + Chat Widget
  As a system operator
  I want respuestas automáticas contextuales en redes
  So that los leads se capturen y califiquen sin intervención

  Background:
    Given las cookies de redes sociales están en state/social/
    And el chat widget está incluido en la página

  Scenario: Detectar intent "Sonora" en mensaje
    Given el sistema recibe un mensaje con "Sonora"
    When detect_intent() procesa el texto
    Then intent = "sonora_trigger"
    And has_sonora = True

  Scenario: Responder con beneficio freemium
    Given un lead menciona "Sonora"
    When generate_response("sonora_trigger") se ejecuta
    Then la respuesta incluye "wa.me" o "sonoradigitalcorp.com"
    And se guarda el lead en state/social/leads.json

  Scenario: Chat widget conoce productos
    Given el chat widget está inicializado
    When el usuario pregunta "precio"
    Then la respuesta incluye "$" o "precio"
    And menciona al menos 2 productos

  Scenario: Voice chat disponible
    Given el navegador soporta SpeechRecognition
    When el usuario activa el micrófono
    Then el widget captura audio
    And transcribe a texto

  Scenario: Cross-platform context
    Given un lead en Instagram menciona "seguridad"
    When el auto-responder procesa
    Then la respuesta usa tono casual + emojis (contexto Instagram)
    And el lead se guarda con plataforma = "instagram"

  Scenario: Pop-up captura lead
    Given pasan 30 segundos en la página
    When el timer dispara el pop-up
    Then el pop-up se muestra con formulario
    And incluye el beneficio "Sonora"

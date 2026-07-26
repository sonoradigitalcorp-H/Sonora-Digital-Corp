Feature: Mystic Voice Ship — Asistente Personal Completo
  As a founder of Sonora Digital Corp
  I want un asistente de voz que monitoree el sistema, recuerde conversaciones y se sienta como una app nativa
  So that pueda operar SDC desde la voz sin depender de dashboards ni terminal

  Background:
    Given Mystic Voice server is running on port 8900
    And the frontend is loaded in a browser

  Scenario: Preguntar estado del sistema por voz
    Given the wake word "Hey Jarvis" is active
    When I say "Mystic, ¿cómo está el sistema?"
    Then the intent router classifies as "check_system"
    And the system monitor returns cpu, ram, disk, uptime
    And Mystic responds: "CPU al 23%, RAM al 38%, disco al 84% — todo estable"
    And TTS audio is played with the response

  Scenario: Memoria persistente al recargar página
    Given I have had a conversation with Mystic (3+ messages)
    When I reload the browser page
    And the WebSocket reconnects with the same session_id
    Then the conversation history is restored from SQLite
    And the last 10 messages appear in the chat log
    And the orb state returns to listening

  Scenario: Instalar Mystic como app de escritorio
    Given the browser supports PWA (Chrome/Edge)
    When I open the Mystic Voice page
    Then a manifest.json is served with app name "Mystic Voice"
    And a service worker is registered
    And the browser shows "Instalar" in the address bar
    When I click install
    Then Mystic opens as a standalone window without browser chrome

  Scenario: Auto wake word al cargar página
    Given I open the Mystic Voice page for the first time
    Then the 🔮 button is already active (glowing)
    And the orb shows "🔮 Wake word activado"
    And a tooltip explains "Di Hey Jarvis para activarme"
    When I allow microphone access
    Then audio streaming starts automatically

  Scenario: Alerta proactiva de CPU alta
    Given the proactive monitor is running (30s interval)
    When CPU usage exceeds 80%
    Then a notification is sent to the frontend
    And the orb pulses red briefly
    And a status message appears: "⚠️ CPU al 85% — el sistema está pesado"
    And no voice is played (non-intrusive)

  Scenario: Edge case — psutil no disponible
    Given psutil is not installed on the system
    When I ask "¿cómo está el sistema?"
    Then the system monitor returns {"error": "psutil not available"}
    And Mystic responds: "No tengo acceso al monitor del sistema en este momento"
    And no crash occurs

  Scenario: Edge case — session DB corrupta
    Given the SQLite database file is corrupted
    When the server starts
    Then the session_db module detects corruption
    And recreates the database file
    And logs a warning: "Session DB corrupted, recreating"
    And the server continues operating normally

  Scenario: Edge case — Safari/ Firefox without PWA
    Given I am using Safari or Firefox
    When I open the Mystic Voice page
    Then the manifest.json is still served
    But the service worker registration may fail silently
    And the app works normally without installation capability

Feature: Jarvis Desktop — Asistente Personal de Escritorio
  As a user of Sonora Digital Corp (founder/operator)
  I want a native desktop agent with always-on voice, screen awareness, system monitoring, and SDC integration
  So that I can interact with the entire SDC ecosystem from my laptop without opening a browser or Telegram

  Background:
    Given Jarvis Desktop is installed on the laptop
    And the system tray icon shows "connected" status
    And the voice loop is listening for wake word "Jarvis"

  Scenario: Happy path — user asks for system status via voice
    Given I am at my laptop with Jarvis running
    When I say "Jarvis, ¿cómo está el sistema?"
    Then the wake word "Jarvis" is detected in <1s
    And the voice is transcribed to text
    And Jarvis reads CPU (%), RAM (used/total), and GPU (utilización)
    And a TTS response is played: "CPU al 23%, RAM 6.2 de 16 GB, GPU al 12% — todo正常"
    And the command is logged to local SQLite

  Scenario: Happy path — create a reminder
    Given Jarvis is listening
    When I say "Jarvis, recuérdame llamar a las 3pm"
    Then a reminder is created in SQLite with due_at "15:00"
    And Jarvis responds "Recordatorio creado: llamar a las 3pm"
    And at 15:00 a native notification appears: "Recordatorio: llamar"
    And the reminder:fired event is emitted

  Scenario: Happy path — control desktop (open app and search)
    Given Jarvis is listening
    When I say "Jarvis, abre Firefox y busca SDC en Google"
    Then Firefox window is opened via xdotool
    And the URL bar is focused
    And "google.com" is typed and navigated
    And "Sonora Digital Corp" is typed in the search box
    And Enter is pressed
    And Jarvis responds "Listo, Firefox abierto con la búsqueda"

  Scenario: Happy path — execute remote SDC agent via Hermes
    Given Jarvis is connected to Hermes Gateway on VPS
    When I say "Jarvis, ejecuta el agente de ventas"
    Then a JSON-RPC message is sent via WebSocket: execute_agent("sales", {})
    And the Sales Agent processes the request remotely
    And the result is returned to Jarvis
    And the response is shown in the HUD chat panel
    And Jarvis reads the summary aloud via TTS

  Scenario: Happy path — proactive battery alert
    Given Jarvis monitor loop is running (every 30s)
    And battery level drops to 15%
    When the proactive engine evaluates context
    Then a native notification appears: "Batería al 15%. ¿Conecto el cargador?"
    And no voice is played (user may be in a meeting)
    And the jarvis:proactive:suggested event is emitted with context

  Scenario: Edge case — VPS disconnection (offline mode)
    Given Jarvis is running and connected to Hermes
    When the VPS becomes unreachable
    Then the HUD icon changes to "offline" (gray)
    And Jarvis announces "Modo offline: comandos remotos se encolarán"
    When I say "Jarvis, ejecuta el agente de ventas"
    Then the command is queued in SQLite offline_queue with status "pending"
    And Jarvis responds "Comando encolado. Se ejecutará cuando reconecte."
    When the VPS becomes reachable again
    Then the queued command is executed automatically
    And the HUD icon returns to "connected" (green)

  Scenario: Edge case — ambient noise (wake word false positive avoidance)
    Given Jarvis is listening with Porcupine wake word engine
    When a loud sound triggers the wake word accidentally
    Then the HUD shows a confirmation prompt: "¿Escuché bien?" with a 2s cancel button
    If no cancel within 2s
    Then Jarvis proceeds to listen for the command
    And if silence is detected for 3s
    Then Jarvis returns to standby without action

  Scenario: Edge case — destructive command requires PIN
    Given Jarvis is listening
    When I say "Jarvis, apaga la computadora"
    Then Jarvis responds "Comando destructivo detectado. Ingresa tu PIN de seguridad."
    And a PIN prompt appears in the HUD
    When I enter the correct PIN
    Then the shutdown command is executed
    When I say "Jarvis, borra todos los archivos"
    Then Jarvis ignores the command and responds "Comando bloqueado. Acción no permitida."

  Scenario: Edge case — locked screen
    Given the laptop screen is locked
    When the screen capture loop runs
    Then mss returns a black/captive screen
    And the OCR module detects "locked" or " bloqueada"
    And screen capture is paused automatically
    And only system monitor loop continues (CPU/RAM/battery)
    When the screen is unlocked
    Then screen capture resumes normally

  Scenario: Edge case — dual monitors
    Given I have two monitors connected (DP-1 and HDMI-0)
    When I say "Jarvis, captura la pantalla"
    Then Jarvis captures the active monitor where the mouse cursor is
    And reports the active window title and detected applications
    And the inactive monitor is not captured

  Scenario: Edge case — GPU not available
    Given the laptop has no NVIDIA GPU
    When the monitor loop starts
    Then nvidia-ml-py fails to initialize gracefully
    And GPU metrics are omitted from monitoring
    And no error is shown to the user
    And the system status response skips GPU information

  Scenario: Startup — Jarvis starts with the system
    Given the systemd service jarvis-desktop.service is enabled
    When the laptop starts and the user logs in
    Then Jarvis auto-starts
    And the HUD icon appears in the system tray
    And the voice loop begins listening for wake word
    And the WebSocket connection to Hermes is established
    And any queued offline commands are replayed

  Scenario: HUD — tray interaction
    Given Jarvis is running with system tray icon
    When I right-click the tray icon
    Then I see menu options: "Abrir Chat", "Monitoreo", "Pausar Voz", "Configuración", "Salir"
    When I click "Monitoreo"
    Then the monitor widget opens showing live CPU, RAM, GPU, and battery gauges
    When I click "Pausar Voz"
    Then the voice loop pauses and the icon changes to muted state
    When I click "Pausar Voz" again
    Then the voice loop resumes and the icon returns to normal

  Scenario: Reminder with repetition
    Given Jarvis is running
    When I say "Jarvis, recuérdame tomar agua cada hora"
    Then a reminder is created with repeat "hourly"
    And a notification fires every hour: "Tomar agua"
    When I say "Jarvis, lista mis recordatorios"
    Then the HUD shows a list of active reminders with their next fire time
    When I say "Jarvis, cancela el recordatorio de tomar agua"
    Then the recurring reminder is deleted from SQLite

  Scenario: Hermes authentication and token refresh
    Given Jarvis has a JWT stored in the system keyring
    When Jarvis connects to Hermes WebSocket
    Then the JWT is sent as a query parameter
    And the connection is authenticated
    After 15 minutes
    When the JWT approaches expiry
    Then a refresh token request is sent silently
    And the new JWT is stored in the keyring
    And the WebSocket connection persists without interruption

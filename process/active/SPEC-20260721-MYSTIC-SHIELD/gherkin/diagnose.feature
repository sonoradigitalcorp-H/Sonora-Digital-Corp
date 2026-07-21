Feature: Diagnóstico de seguridad automatizado
  As a CEO de una PyME
  I want recibir un diagnóstico completo de mi red
  So that pueda entender los riesgos de seguridad sin ser técnico

  Background:
    Given el sistema tiene acceso a la red del cliente (IP/subred)
    And el CEO tiene WhatsApp registrado

  Scenario: Diagnóstico exitoso con todos los canales
    Given el target es "192.168.1.0/24"
    And la empresa es "Fourgea México"
    And el CEO tiene WhatsApp "6622681111" y email "ceo@fourgea.com"
    When ejecuto shield_diagnose
    Then el escaneo detecta hosts en la red
    And el LLM genera análisis ejecutivo
    And se genera PDF profesional (6 slides)
    And se genera audio resumen
    And se envía WhatsApp al CEO con PDF + audio + texto introductorio
    And se envía Email con PDF adjunto
    And el reporte se guarda en state/reports/ con metadatos JSON

  Scenario: Red sin hosts activos
    Given el target es "10.0.0.0/24" (red sin equipos)
    When ejecuto shield_diagnose
    Then el resultado indica "0 hosts detectados"
    And el análisis sugiere verificar la dirección IP
    And el PDF se genera igualmente con el hallazgo

  Scenario: Sin acceso a WhatsApp (wacli no instalado)
    Given wacli no está disponible en el sistema
    When ejecuto shield_diagnose
    Then el escaneo y análisis se completan normalmente
    And el PDF y audio se generan
    And se envía solo Email (sin WhatsApp)
    And el reporte indica "WhatsApp: no disponible"

  Scenario: Fallo de OpenRouter (sin API key)
    Given OPENROUTER_API_KEY no está configurada
    When ejecuto shield_diagnose
    Then el análisis usa fallback template
    And el PDF se genera con análisis básico
    And el audio incluye el análisis limitado

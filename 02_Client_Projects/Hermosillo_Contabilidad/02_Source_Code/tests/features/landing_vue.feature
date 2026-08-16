# tests/features/landing_vue.feature
Feature: Landing dinámica Hermosillo (SDD 0008)

  Scenario: La landing carga como SPA dinámica
    Given el usuario abre https://sonoradigitalcorp.com/hermosillo.html
    Then ve el título "Nathaly · Contabilidad en Hermosillo · Asistente IA 24/7"
    And ve 6 tarjetas de servicio con botón "TOCA PARA VER"
    And ve la sección FAQ con 5 preguntas
    And ve el aviso de privacidad

  Scenario: El chat responde con texto limpio
    When el usuario escribe "qué me ofrecen de contabilidad" en el asistente
    Then la respuesta no contiene emojis, asteriscos ni signos de admiración

  Scenario: Contacto por iconos sin texto
    Given el usuario ve la sección de contacto
    Then hay iconos de WhatsApp, Telegram, correo e Instagram
    And el correo no muestra la dirección como texto (solo icono)
    And el enlace WhatsApp incluye el servicio prefilled

  Scenario: Voz con botón de detener
    Given el usuario recibe una respuesta de voz
    Then aparece un botón "■" para detener la reproducción
    And al presionarlo la voz se detiene

  Scenario: Video reel con marca
    Given el usuario ve la sección de video
    Then hay un reproductor con reel_hermosillo.mp4
    And un enlace "Quiero uno así" que abre WhatsApp
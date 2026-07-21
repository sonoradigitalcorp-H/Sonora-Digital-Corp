# language: es
Funcionalidad: Recolección conversacional de fotos y audio
  Como agente de clon publicitario
  Quiero recibir fotos y audio del cliente por WhatsApp/Telegram
  Para entrenar un modelo de IA con su identidad visual y vocal

  Escenario: Cliente envía 15 fotos y dice "terminé"
    Dado que el cliente "Juan Pérez" compró el pack de clon publicitario
    Y tiene un bucket en Supabase Storage listo
    Cuando envía 15 fotos por WhatsApp
    Y dice "terminé"
    Entonces el sistema valida que todas las fotos tengan rostro detectable
    Y confirma al cliente: "Recibí 15 fotos. ¿Puedes enviar un audio de 30 segundos?"

  Escenario: Cliente envía audio de 30 segundos
    Dado que el cliente ya envió 15 fotos válidas
    Cuando envía un audio de 35 segundos hablando natural
    Entonces el sistema valida que el audio tenga voz clara y SNR > 15dB
    Y confirma: "Audio recibido. Empiezo el entrenamiento en unos minutos."

  Escenario: Cliente envía menos fotos de las necesarias
    Dado que el cliente compró el pack
    Cuando envía solo 8 fotos
    Y dice "terminé"
    Entonces el sistema responde: "Recibí 8 fotos. Necesito al menos 15. ¿Puedes enviar 7 más?"
    Y no inicia el entrenamiento

  Escenario: Cliente envía fotos en múltiples mensajes durante horas
    Dado que el cliente compró el pack
    Cuando envía 5 fotos el lunes
    Y envía 7 fotos el martes
    Y envía 3 fotos el miércoles
    Y dice "terminé"
    Entonces el sistema confirma 15 fotos recibidas
    Y procede a validación de calidad

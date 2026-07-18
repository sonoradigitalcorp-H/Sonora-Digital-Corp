# language: es
Funcionalidad: Entrenamiento de LoRA facial y clon de voz
  Como sistema de clon publicitario
  Quiero entrenar un LoRA facial y clonar la voz del cliente
  Para generar contenido publicitario con su identidad

  Escenario: Entrenar LoRA con 15 fotos válidas
    Dado que el cliente "María García" tiene 15 fotos validadas en Supabase
    Cuando el sistema inicia el entrenamiento en FAL flux-lora-trainer
    Entonces el entrenamiento completa en menos de 15 minutos
    Y el peso del LoRA se guarda en /clients/{id}/models/lora.safetensors
    Y la face similarity contra las fotos originales es > 0.75

  Escenario: Clonar voz desde audio de 30 segundos
    Dado que el cliente tiene un audio validado de 35 segundos
    Cuando el sistema clona la voz vía MiniMax/OmniVoice
    Entonces el clon de voz se completa en menos de 2 minutos
    Y el voice ID se guarda asociado al cliente

  Escenario: Validar calidad del LoRA entrenado
    Dado que el LoRA fue entrenado
    Cuando se genera una foto de prueba con el trigger word
    Entonces la face similarity contra la foto de referencia es calculada
    Y si es > 0.75, el LoRA se marca como "activo"
    Y si es < 0.6, el LoRA se rechaza y se piden más fotos

  Escenario: Fallo de entrenamiento por fotos insuficientes
    Dado que el cliente solo tiene 12 fotos
    Cuando se intenta entrenar el LoRA
    Entonces el sistema rechaza con error: "Se requieren al menos 15 fotos"
    Y notifica al cliente que envíe más fotos

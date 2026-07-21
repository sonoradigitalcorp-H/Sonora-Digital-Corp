# language: es
Funcionalidad: Generación de contenido con identidad del cliente
  Como cliente del servicio de clon
  Quiero generar fotos, videos y audio con mi cara y voz
  Para usar en campañas de marketing y publicidad

  Escenario: Generar foto con la cara del cliente
    Dado que el cliente "Pedro López" tiene un LoRA entrenado y activo
    Cuando pide: "Quiero una foto mía en una oficina ejecutiva, traje azul"
    Entonces el sistema genera una foto vía FAL flux-lora con su LoRA
    Y la imagen se guarda en /clients/{id}/output/photos/
    Y se descuenta 1 crédito del pack

  Escenario: Generar video talking-head
    Dado que el cliente tiene LoRA y voz clonada
    Cuando pide: "Quiero un video de 15s presentando mi nuevo producto"
    Y proporciona un guion de texto
    Entonces el sistema:
      - Genera TTS con su voz clonada
      - Genera video con live portrait/lip sync
      - Sincroniza audio y video
    Y el video se guarda en /clients/{id}/output/videos/
    Y se descuentan 5 créditos

  Escenario: Generar video de cuerpo completo
    Dado que el cliente tiene fotos de cuerpo completo en su set de entrenamiento
    Cuando pide: "Quiero un video caminando por una playa, ropa casual"
    Entonces el sistema genera video vía FAL seedance/kling
    Y aplica lip sync si hay audio
    Y se guarda en /clients/{id}/output/videos/

  Escenario: Generar TTS con voz clonada
    Dado que el cliente tiene voz clonada
    Cuando pide: "Dilo en mi voz: 'Visita nuestra web y obtén 20% de descuento'"
    Entonces el sistema genera audio con su voz clonada
    Y se guarda en /clients/{id}/output/audio/
    Y se descuenta 1 crédito

  Escenario: Iterar generación con cambios
    Dado que el cliente generó una foto de oficina ejecutiva
    Cuando pide: "Cámbiale el fondo por una terraza con vista a la ciudad"
    Entonces el sistema regenera la foto con el nuevo prompt
    Y mantiene la misma identidad facial (mismo LoRA)
    Y solo descuenta 1 crédito adicional

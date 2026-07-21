# language: es
Funcionalidad: Gestión de créditos y pricing
  Como cliente del servicio de clon
  Quiero comprar packs de créditos y consumirlos con cada generación
  Para pagar solo por lo que uso

  Escenario: Comprar pack de créditos
    Dado que soy un nuevo cliente
    Cuando compro el pack "Básico" por $49 USD
    Entonces recibo:
      | Crédito | Cantidad |
      | Entrenamiento LoRA | 1 |
      | Clon de voz | 1 |
      | Foto generada | 10 |
      | Video 15s | 3 |
      | Audio TTS | 10 |
    Y el pack tiene validez de 90 días

  Escenario: Consumir crédito por generación
    Dado que tengo un pack activo con 10 créditos de foto
    Cuando genero una foto
    Entonces se descuenta 1 crédito de foto
    Y me quedan 9 créditos de foto
    Y el sistema confirma: "Foto generada. Te quedan 9 créditos de foto."

  Escenario: Renovar pack al agotarse créditos
    Dado que tengo 0 créditos de foto
    Cuando intento generar una foto
    Entonces el sistema responde: "Te quedan 0 créditos de foto. ¿Quieres comprar más?"
    Y no genera la foto hasta que se compre más créditos
    Cuando compro 10 créditos adicionales por $19 USD
    Entonces puedo generar la foto

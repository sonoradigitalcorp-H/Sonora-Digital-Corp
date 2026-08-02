# language: es
Caracteristica: Verificacion KYC
  Como nuevo cliente
  Quiero completar mi verificacion de identidad
  Para comenzar a usar los agentes de voz

  Escenario: KYC basico aprobado automaticamente (Despertar)
    Dado que Ana se registra y selecciona Despertar
    Y sube foto de su INE (frente y vuelta)
    Cuando el sistema ejecuta OCR
    Entonces extrae: nombre, fecha nacimiento, CURP, vigencia
    Y compara con los datos del registro
    Y la coincidencia es > 95%
    Y el documento no esta vencido
    Y la imagen no esta manipulada (tamper score < 0.3)
    Entonces el KYC se aprueba automaticamente en menos de 5 minutos
    Y Ana puede comenzar a configurar su agente

  Escenario: KYC requiere revision manual (Elevar)
    Dado que Roberto se registra y selecciona Elevar
    Y sube su INE pero la imagen esta borrosa
    Cuando el sistema ejecuta OCR
    Entonces la coincidencia es 82% (< 95%)
    Y el sistema marca la verificacion como "pendiente_manual"
    Y un operador de Sonora recibe la notificacion
    Y el operador aprueba manualmente en menos de 24 horas
    Y Roberto recibe notificacion por WhatsApp

  Escenario: KYC rechazado - documento manipulado
    Dado que un usuario sube un INE con evidentes signos de edicion
    Cuando el sistema ejecuta deteccion de manipulacion
    Entonces el tamper score es 0.85 (> 0.7)
    Y el KYC se rechaza automaticamente
    Y el usuario recibe email: "Documento no valido. Sube una foto clara de tu INE original."
    Y el registro permanece pero el servicio no se activa

  # Metricas:
    # | Metrica | Target | Medicion |
    # |---------|--------|----------|
    # | OCR precision | > 95% | Comparacion manual vs automatica |
    # | Tiempo KYC automatico | < 5 min | End-to-end timer |
    # | Deteccion manipulacion | > 0.7 score | Tamper detection model |
    # | Falsos positivos rechazo | < 2% | Revision manual de rechazados |
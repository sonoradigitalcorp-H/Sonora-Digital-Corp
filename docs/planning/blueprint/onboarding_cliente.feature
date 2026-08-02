# language: es
Caracteristica: Onboarding de Nuevo Cliente
  Como nuevo usuario que quiere un agente de voz
  Quiero configurar mi agente en el menor tiempo posible
  Para que empiece a atender mis clientes hoy

  Escenario: Onboarding completo paquete Despertar (auto-servicio)
    Dado que Ana se registra en sonoradigitalcorp.com
    Y selecciona el paquete Despertar (14 dias gratis)
    Cuando completa el formulario: nombre, email, telefono, negocio, giro
    Entonces recibe email de verificacion en menos de 30 segundos
    Y verifica su email haciendo click en el link
    Y sube un audio de 30 segundos para clon de voz
    Y el sistema genera el modelo de voz en menos de 5 minutos
    Y elige WhatsApp como canal de comunicacion
    Y configura 5 preguntas frecuentes de su negocio de reposteria
    Y el sistema crea su tenant con UUID unico
    Y se le asigna un numero de telefono virtual
    Y Ana realiza una llamada de prueba y el agente contesta
    Y el tiempo total de onboarding es menor a 2 horas

  Escenario: Onboarding paquete Elevar (con verificacion KYC)
    Dado que Roberto se registra y selecciona Elevar
    Cuando sube su INE para KYC
    Entonces el sistema ejecuta OCR y valida el documento
    Y compara los datos extraidos con los del registro
    Y la validacion es exitosa (coincidencia > 95%)
    Y Roberto queda en estado "pendiente_verificacion_manual"
    Cuando un operador de Sonora aprueba el KYC en menos de 24 horas
    Entonces Roberto recibe notificacion por WhatsApp: "KYC aprobado. Comienza tu configuracion."
    Y Roberto configura 3 agentes con sus personalidades
    Y sube audios para clon de voz profesional
    Y carga su knowledge base completa (servicios, precios, FAQ, objeciones)
    Y el sistema clona la voz, configura los agentes, y activa los 3 numeros virtuales
    Y el onboarding se completa en menos de 8 horas

  Escenario: Upgrade de Despertar a Elevar con datos preexistentes
    Dado que Ana lleva 2 meses en Despertar
    Y su KB, voz y configuracion ya existen
    Cuando Ana hace upgrade a Elevar
    Entonces su voz, KB y numero virtual se migran automaticamente
    Y se crean 2 agentes adicionales basados en la configuracion del primero
    Y se asignan 2 numeros virtuales nuevos
    Y el tiempo de upgrade es menor a 30 minutos
    Y no hay interrupcion del servicio durante el upgrade

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Email verificacion | < 30s | SMTP delivery time |
  # | Generacion modelo voz | < 5 min | Kokoro training time |
  # | Asignacion numero DID | < 1 min | Vonage API time |
  # | Onboarding Despertar | < 2 horas | End-to-end timer |
  # | Onboarding Elevar | < 8 horas | End-to-end timer |
  # | Upgrade Despertar-Elevar | < 30 min | Migration timer |
  # | Migracion sin interrupcion | 0s downtime | Service health check |
# language: es
Caracteristica: Sistema de Afiliados - Registro y Upgrade
  Como usuario de Sonora
  Quiero referir amigos y ganar comisiones
  Para que mi red me beneficie con la Regla del x3

  Escenario: Registro automatico como afiliado Explorador
    Dado que Roberto es cliente activo de Elevar
    Cuando Roberto hace click en "Programa de Afiliados" en su dashboard
    Entonces se activa como afiliado Nivel 1 (Explorador) automaticamente
    Y recibe un link de referido unico
    Y su link contiene utm_source con su afiliado_id
    Y recibe badge "Explorador Sonora" en su perfil
    Y ve un panel basico con: clicks, conversiones, ganancias

  Escenario: Referido completa onboarding - comision activada
    Dado que Ana hace click en el link de referido de Roberto
    Y se registra y selecciona Despertar
    Y completa su onboarding exitosamente
    Entonces Roberto recibe 15% de la primera mensualidad de Ana
    Y Roberto recibe 5 SON en su billetera
    Y Ana recibe 5% de descuento en su primer mes
    Y Roberto ve la comision en su panel de afiliados

  Escenario: Upgrade a Guardian (25+ referidos)
    Dado que Roberto tiene 25 referidos activos
    Y ha acumulado $5,200 MXN en comisiones
    Cuando el sistema detecta que alcanzo ambos criterios
    Entonces notifica a Roberto por WhatsApp: "Has subido a Guardian del Templo"
    Y su comision sube a 20% de las primeras 3 mensualidades
    Y gana 10 SON por cada nuevo onboarding completado
    Y accede al kit de venta basico
    Y su cupon de descuento para referidos sube a 10%

  Escenario: Comision de generacion 2 (Alquimista)
    Dado que Roberto es afiliado Alquimista (Nivel 3)
    Y Ana (referida por Roberto) refiere a Pedro
    Cuando Pedro completa su onboarding
    Entonces Roberto gana 8% de la primera mensualidad de Pedro (gen 2)
    Y Ana gana su comision de gen 1 completa
    Y Pedro recibe descuento de 15% por venir de un Alquimista
    Y la comision de gen 2 se registra automaticamente sin accion de Roberto

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Activacion afiliado | < 1s | DB update time |
  # | Generacion link referido | < 500ms | API response |
  # | Tracking conversion | 100% | UTM parameter persistence |
  # | Credito comision | < 24h | Cron job frequency |
  # | Deteccion upgrade nivel | < 1h | Background worker |
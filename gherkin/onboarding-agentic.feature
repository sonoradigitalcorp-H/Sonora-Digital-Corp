# language: es
Funcionalidad: Onboarding — Activación agentica
  Como sistema SDC
  Quiero activar automáticamente los skills correctos para cada cliente
  Para que tengan las capacidades que pagaron sin configuración manual

  Escenario: Cliente recibe skills básicos
    Dado que un cliente activa su plan "Pro"
    Cuando se completa la activación
    Entonces se activan los skills: clone-service, wacli, taskflow
    Y se configura Hermes para WhatsApp
    Y OpenCode puede ser invocado por el agente

  Escenario: Partner recibe skills avanzados
    Dado que un partner activa su cuenta
    Cuando se completa la activación
    Entonces se activan skills adicionales: supabase, stripe, github
    Y Hermes se configura para WhatsApp + Telegram
    Y OpenCode tiene acceso a tools de administración

  Escenario: Skills se desactivan si el plan expira
    Dado que el plan de un cliente expiró
    Cuando se verifica el estado de su suscripción
    Entonces los skills premium se desactivan
    Y solo queda el skill básico de comunicación

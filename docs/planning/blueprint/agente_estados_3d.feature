# language: es
Caracteristica: Estados del Agente en Mundo 3D
  Como cliente del paquete Soberano
  Quiero ver el estado real de mis agentes en un mundo virtual 3D
  Para saber que estan haciendo 24/7 sin leer reportes

  Escenario: Agente dormido se despierta con llamada entrante
    Dado que el agente "La Guardiana" lleva 20 minutos sin actividad
    Y el cliente Roberto abre su dashboard 3D
    Cuando observa el mundo virtual de su clinica dental
    Entonces ve el avatar del agente acostado en la silla
    Y la escena tiene iluminacion tenue (brillo 0.4)
    Y el sonido ambiente es de ventilador suave
    Y el color de acento es gris (#6b7280)

    Cuando llega una llamada entrante
    Entonces el avatar se levanta con animacion suave (1.5s)
    Y la iluminacion cambia a brillo 1.0
    Y el color de acento cambia a azul (#3b82f6)
    Y aparece indicador de onda de sonido cerca de la boca
    Y el avatar hace gestos mientras habla
    Y el sonido ambiente cambia a silencio (privacidad)
    Y la transicion total toma menos de 2 segundos

  Escenario: Agente en llamada cambia a procesando y de vuelta
    Dado que el agente esta en estado "en_llamada"
    Cuando el LLM tarda mas de 2 segundos en responder
    Entonces el avatar mira hacia arriba (estado procesando)
    Y aparece una espiral de pensamiento sobre su cabeza
    Y el color de acento cambia a amarillo (#f59e0b)
    Y el sonido ambiente es un zumbido suave
    Cuando el LLM responde
    Entonces el avatar vuelve a mirar al frente (estado en_llamada)
    Y la espiral desaparece
    Y el color de acento vuelve a azul
    Y la transicion toma menos de 300ms

  Escenario: Multiples agentes en vista multi-agente
    Dado que Roberto tiene 3 agentes activos: Guardiana, Alquimista, Sanador
    Cuando abre el mini-mapa 3D
    Entonces ve los 3 avatares en sus respectivas posiciones
    Y la Guardiana esta en estado "en_llamada" (azul, de pie)
    Y el Alquimista esta en estado "dormido" (gris, acostado)
    Y el Sanador esta en estado "despierto" (verde, sentado)
    Y cada avatar tiene su label con nombre y estado
    Y puede hacer click en cualquier avatar para ver su detalle

  Escenario: Vista del cliente vs vista de Mystic (admin)
    Dado que Roberto es cliente Soberano
    Y Mystic es el administrador del sistema
    Cuando Roberto abre su dashboard
    Entonces ve UNICAMENTE sus 3 agentes
    Y ve el escenario de clinica dental
    Y NO ve otros tenants ni sus datos
    Cuando Mystic abre el panel admin
    Entonces ve TODOS los tenants activos (14)
    Y ve TODOS los agentes corriendo (47)
    Y ve metricas de costo por tenant
    Y puede hacer click en cualquier tenant para ver su mundo 3D

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Latencia estado WS | < 500ms | WebSocket round-trip |
  # | Transicion dormido-a-llamada | < 2s | Animation timer |
  # | Transicion llamada-a-procesando | < 300ms | State change timer |
  # | FPS del mundo 3D | 60 FPS | requestAnimationFrame delta |
  # | GPU usada (integrada) | < 15% | GPU utilization |
  # | Carga inicial 3D | < 3s (200KB gzipped) | Page load + asset load |
  # | Isolacion visual entre tenants | 100% | JWT tenant check en render |
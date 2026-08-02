# language: es
Caracteristica: Configuracion White-Label
  Como cliente Soberano que quiere su propia marca
  Quiero que la plataforma muestre MI marca, no la de Sonora
  Para que mis clientes no sepan que uso un proveedor externo

  Escenario: Setup completo de white-label
    Dado que el cliente "restaurante-luna" contrata Soberano con white-label
    Y completa el formulario de branding: logo, colores, tipografia, dominio
    Cuando el sistema procesa la configuracion white-label
    Entonces genera el dominio personalizado: agentes.restauranteluna.com
    Y configura el certificado SSL via Let's Encrypt automaticamente
    Y el dashboard muestra el logo de Restaurante Luna en lugar de Sonora
    Y la paleta de colores cambia a la del restaurante (naranja, crema, madera)
    Y la tipografia cambia a la seleccionada por el cliente
    Y el footer del email muestra "Restaurante Luna" en lugar de "Sonora Digital Corp"
    Y el nombre del agente se personaliza (ej: "Luna" en lugar de "La Guardiana")
    Y los reportes por email llevan branding del restaurante
    Y la voz del agente se mantiene (es la del cliente, no se cambia)
    Y el tiempo total de setup white-label es menor a 48 horas

  Escenario: Sonora invisible para el cliente final
    Dado que el white-label esta configurado
    Cuando un prospecto llama al agente del restaurante
    Entonces el prospecto NO escucha ni ve mencion de Sonora en ningun punto
    Y si el prospecto pregunta "quien hizo este sistema?"
    Entonces el agente responde con el nombre del restaurante
    Y no menciona Sonora, Mystic, ni ningun termino de la plataforma

  Escenario: Dominio custom con SSL
    Dado que el cliente usa agentes.miclinica.com
    Cuando un prospecto accede al dashboard del agente
    Entonces el certificado SSL es valido y no muestra advertencia
    Y el certificado se renueva automaticamente cada 60 dias
    Y el redirect de HTTP a HTTPS funciona correctamente

  # Metricas:
  # | Metrica | Target | Medicion |
  # |---------|--------|----------|
  # | Setup white-label completo | < 48h | End-to-end timer |
  # | SSL auto-renewal | 60 dias | Certbot timer |
  # | Cero menciones de Sonora | 100% | Content scan |
  # | Dominio custom response | < 200ms | DNS + proxy time |
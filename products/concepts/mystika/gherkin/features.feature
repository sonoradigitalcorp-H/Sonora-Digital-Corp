# Gherkin Features — Mystika
# Spec: SPEC-20260630-012
# Formato: Gherkin (Given-When-Then)

---

Feature: Registro de usuario
  Como visitante
  Quiero registrarme en Mystika
  Para acceder al contenido

  Scenario: Registro exitoso con email
    Given que estoy en la landing page de Mystika
    When hago clic en "Comenzar"
    And completo el formulario con email valido y contraseña
    Then recibo email de confirmacion
    And puedo iniciar sesion inmediatamente

  Scenario: Registro fallido por email duplicado
    Given que ya existe una cuenta con ese email
    When intento registrarme con el mismo email
    Then veo error "Este email ya esta registrado"
    And no se crea la cuenta

  Scenario: Verificacion de edad (18+)
    Given que estoy en el formulario de registro
    When no marco "Soy mayor de 18 anos"
    Then el boton de registro permanece deshabilitado

---

Feature: Catalogo de lecciones
  Como usuario de Mystika
  Quiero ver el catalogo de lecciones
  Para elegir que aprender

  Scenario: Ver catalogo completo
    Given que soy un usuario registrado
    When navego a /lessons
    Then veo todas las lecciones publicadas
    And cada leccion muestra titulo, precio, y preview

  Scenario: Filtrar por instrumento
    Given que estoy en el catalogo
    When selecciono el filtro "Guitarra"
    Then solo veo lecciones de guitarra

  Scenario: Ver detalle de leccion
    Given que estoy viendo el catalogo
    When hago clic en una leccion
    Then veo descripcion completa
    And veo un preview de 30 segundos si no tengo acceso

---

Feature: Compra individual de leccion
  Como usuario
  Quiero comprar una leccion individual
  Para acceder a su contenido completo

  Scenario: Compra exitosa con Stripe
    Given que estoy viendo una leccion
    When hago clic en "Comprar $14.99"
    And soy redirigido a Stripe Checkout
    And completo el pago con tarjeta
    Then veo confirmacion "Acceso activado"
    And puedo ver el video completo

  Scenario: Compra exitosa con Mercado Pago
    Given que estoy viendo una leccion
    When hago clic en "Comprar $14.99"
    And selecciono Mercado Pago como metodo
    And completo el pago (tarjeta/OXXO/SPEI)
    Then veo confirmacion "Acceso activado"
    And puedo ver el video completo

  Scenario: Compra fallida por pago rechazado
    Given que estoy en el checkout
    When mi banco rechaza el pago
    Then veo error "Pago rechazado"
    And no se activa el acceso

  Scenario: Intento de ver video sin comprar
    Given que NO he comprado la leccion
    When intento ver el video completo
    Then veo solo el preview de 30 segundos
    And veo boton "Comprar para ver completo"

---

Feature: Suscripcion mensual
  Como usuario
  Quiero suscribirme a un plan
  Para acceder a todo el contenido

  Scenario: Suscripcion a Mysteria ($14.99/mes)
    Given que estoy en la pagina de precios
    When selecciono "Mysteria"
    And completo el pago recurrente
    Then mi suscripcion esta activa inmediatamente
    And veo todo el contenido del plan Mysteria

  Scenario: Suscripcion a Ritual ($49.99/mes)
    Given que estoy en la pagina de precios
    When selecciono "Ritual"
    And completo el pago recurrente
    Then mi suscripcion esta activa inmediatamente
    And veo todo el contenido de Mysteria + Ritual

  Scenario: Degradacion por fallo de renovacion
    Given que soy suscriptor Mysteria
    When mi pago recurrente falla
    Then recibo notificacion "Tu suscripcion sera cancelada"
    And tengo 7 dias para actualizar metodo de pago
    And si no actualizo, pierdo acceso al contenido premium

  Scenario: Cancelar suscripcion
    Given que soy suscriptor activo
    When cancelo mi suscripcion en /mi-cuenta
    Then mantengo acceso hasta el final del periodo pagado
    And no se me cobrara el siguiente mes

---

Feature: Visualizacion de video protegido
  Como usuario con acceso
  Quiero ver videos sin poder descargarlos
  Para proteger el contenido de Lilith

  Scenario: Ver video con acceso valido
    Given que tengo acceso a la leccion (compra o suscripcion)
    When hago clic en "Ver leccion"
    Then el video comienza a reproducirse
    And no hay boton de descarga
    And el menu contextual "Guardar como" esta deshabilitado

  Scenario: Token expirado durante reproduccion
    Given que estoy viendo un video
    When mi token de acceso expira
    Then el video se pausa
    And se renueva el token silenciosamente si aun tengo acceso
    And la reproduccion continua

  Scenario: Token expirado sin acceso vigente
    Given que mi suscripcion expiro
    When intento ver un video con un token antiguo
    Then veo "Acceso denegado"
    And se me redirige a la pagina de planes

  Scenario: Ephemeral — Consumir unica vista
    Given que compre una leccion individual (1 vista incluida)
    When veo el video completo
    Then el token se invalida automaticamente
    And veo pantalla "Ritual consumido"
    And veo las opciones: Retener ($7.49) o Descargar ($14.99)

  Scenario: Ephemeral — Cerrar antes de terminar
    Given que compre una leccion individual
    When veo el 70% del video y cierro
    Then el token se invalida (cuenta como vista consumida)
    And veo pantalla "Ritual consumido"

  Scenario: Ephemeral — Retener contenido
    Given que consumi mi unica vista de una leccion
    When pago $7.49 para retenerla
    Then recibo un nuevo token con acceso perpetuo
    And puedo ver la leccion cuantas veces quiera
    And la leccion aparece en "Mi Altar"

  Scenario: Ephemeral — Descargar contenido
    Given que consumi mi unica vista de una leccion
    When pago $14.99 para descargarla
    Then recibo un enlace de descarga valido por 7 dias
    And el archivo descargado tiene watermark con mi usuario
    And la leccion aparece como "Descargada" en mi historial

  Scenario: Ephemeral — Suscriptor Ritual no consume vistas
    Given que soy suscriptor Ritual ($49.99/mes)
    When veo una leccion completa
    Then NO se invalida el token
    And puedo volver a verla cuando quiera (retencion incluida)

  Scenario: Ephemeral — Suscriptor Mysteria consume su vista
    Given que soy suscriptor Mysteria ($14.99/mes)
    When veo una leccion completa por primera vez
    Then el token se invalida
    And veo opcion de retener por $4.99 (precio con descuento de suscriptor)

  Scenario: Ephemeral — Descarga tiene watermark
    Given que descargue un video
    When abro el archivo
    Then veo mi @username y email superpuestos en el video
    And el watermark cambia de posicion cada 30 segundos

  Scenario: Ephemeral — Enlace de descarga expira
    Given que recibi un enlace de descarga
    When pasan 7 dias sin descargar
    Then el enlace expira
    And veo "Este talisman ya no esta disponible"
    And puedo comprar la descarga nuevamente

---

Feature: Galeria NSFW
  Como suscriptor
  Quiero acceder a la galeria de fotos y videos exclusivos
  Para disfrutar del contenido de Lilith

  Scenario: Suscriptor Mysteria ve fotos semanales
    Given que soy suscriptor Mysteria
    When navego a la galeria
    Then veo fotos NSFW semanales
    And NO veo videos NSFW (solo Ritual)

  Scenario: Suscriptor Ritual ve todo
    Given que soy suscriptor Ritual
    When navego a la galeria
    Then veo fotos NSFW diarias
    And veo videos NSFW exclusivos

  Scenario: Usuario free ve previews censurados
    Given que soy usuario gratuito
    When navego a la galeria
    Then veo thumbnails censurados (borrosos)
    And veo mensaje "Suscribete para ver"

---

Feature: Ofrendas (Tips)
  Como usuario
  Quiero enviar una donacion a Lilith
  Para mostrar mi aprecio

  Scenario: Enviar tip con mensaje
    Given que estoy en la pagina de ofrendas
    When selecciono $10
    And escribo "Gracias por tu musica Lilith"
    And completo el pago
    Then Lilith me agradece personalmente via AI chat
    And veo mi ofrenda en el muro de ofrendas

  Scenario: Tip sin mensaje
    Given que estoy en la pagina de ofrendas
    When selecciono $5
    And no escribo mensaje
    And completo el pago
    Then recibo un agradecimiento generico de Lilith

---

Feature: Mystika Apparel (E-commerce)
  Como usuario
  Quiero comprar mercancia de Mystika
  Para sentirme parte del circulo

  Scenario: Compra de producto
    Given que estoy en Mystika Apparel
    When agrego una camiseta al carrito
    And voy al checkout
    And pago con Stripe
    Then recibo confirmacion de compra
    And recibo email con numero de seguimiento

  Scenario: Producto agotado
    Given que estoy viendo un producto
    When no hay stock
    Then veo "Agotado"
    And puedo registrarme para notificarme cuando haya

---

Feature: Chat con Lilith (AI)
  Como suscriptor
  Quiero chatear con Lilith
  Para recibir consejos musicales personalizados

  Scenario: Suscriptor Mysteria chatea con Lilith
    Given que soy suscriptor Mysteria
    When abro el chat con Lilith
    Then puedo enviar hasta 20 mensajes por dia
    And Lilith responde con consejos musicales y motivacion

  Scenario: Suscriptor Ritual chatea ilimitado
    Given que soy suscriptor Ritual
    When abro el chat con Lilith
    Then puedo enviar mensajes ilimitados
    And Lilith recuerda mi progreso y lecciones previas

  Scenario: Usuario free no puede chatear
    Given que soy usuario gratuito
    When intento abrir el chat
    Then veo "Disponible para suscriptores"
    And veo boton para ver planes

---

Feature: Admin sube contenido via Telegram
  Como administrador (Lilith)
  Quiero subir lecciones desde Telegram
  Para publicar contenido rapido

  Scenario: Subir leccion con video
    Given que soy el admin registrado
    When envio un video al bot
    Then el bot responde "Nombre de la leccion:"
    When respondo "Ritmos basicos de bateria"
    Then el bot responde "Precio en MXN:"
    When respondo "299"
    Then el bot responde "Descripcion (o /skip):"
    When respondo "Aprende los ritmos fundamentales"
    Then el bot guarda el video
    And crea la leccion en estado borrador
    And responde "Guardada. /publicar 1 para activarla"

  Scenario: Subir foto a galeria NSFW
    Given que soy el admin registrado
    When envio una foto al bot
    Then el bot responde "Tipo de contenido (foto/video):"
    When respondo "foto"
    Then el bot responde "Para que plan (Mysteria/Ritual/ambos):"
    When respondo "ambos"
    Then el bot guarda la foto
    And la publica automaticamente en la galeria

---

Feature: Streaming en vivo (Aquelarres)
  Como suscriptor
  Quiero ver los streams en vivo de Lilith
  Para conectarme en tiempo real

  Scenario: Suscriptor ve stream en vivo
    Given que soy suscriptor Mysteria o Ritual
    When Lilith inicia un stream en vivo
    Then recibo notificacion push "Lilith esta en vivo"
    When abro la notificacion
    Then veo el stream en vivo
    And puedo enviar reacciones

  Scenario: Usuario free no puede ver stream
    Given que soy usuario gratuito
    When intento ver un stream en vivo
    Then veo "Solo para suscriptores"
    And veo boton para suscribirme

---

Feature: Notificaciones push (Susurros)
  Como usuario
  Quiero recibir notificaciones de Mystika
  Para no perderme contenido nuevo

  Scenario: Recibir susurro de nueva leccion
    Given que soy suscriptor
    When Lilith publica una nueva leccion
    Then recibo notificacion "Nuevo ritual: [titulo]"
    And al tocarla, abre la leccion

  Scenario: Recibir susurro de ofrenda agradecida
    Given que envie una ofrenda
    When Lilith responde via AI
    Then recibo notificacion "Lilith te ha respondido"
    And al tocarla, abre el chat

---

Feature: App mobile
  Como usuario
  Quiero usar Mystika en mi telefono
  Para aprender donde sea

  Scenario: Login en app mobile
    Given que tengo la app de Mystika instalada
    When abro la app
    And inicio sesion con mi email y contrasena
    Then veo el dashboard con mi progreso

  Scenario: Ver leccion en mobile
    Given que estoy logueado en la app
    When selecciono una leccion que compre
    Then el video se reproduce en fullscreen
    And puedo rotar a landscape

---

Feature: Contenido efimero y retencion
  Como usuario de Mystika
  Quiero que el contenido se consuma al verlo
  Para que sea una experiencia valiosa y efimera

  Scenario: Compra individual = 1 vista
    Given que compro una leccion individual
    Then el token de acceso se crea con max_views = 1
    And expires_at = now + 48 horas

  Scenario: Suscripcion Mysteria = 1 vista por leccion
    Given que soy suscriptor Mysteria
    When veo una leccion nueva
    Then el token se crea con max_views = 1
    And expires_at = now + 48 horas

  Scenario: Suscripcion Ritual = vistas ilimitadas
    Given que soy suscriptor Ritual
    When veo una leccion
    Then el token se crea con max_views = -1 (ilimitado)
    And expires_at = hasta que cancele la suscripcion

  Scenario: Retener despues de consumir
    Given que consumi mi vista de una leccion
    When pago para retenerla
    Then se crea un nuevo token con max_views = -1
    And el contenido aparece en "Mi Altar"

  Scenario: Descargar con watermark
    Given que pago para descargar un video
    Then el servidor procesa el video con FFmpeg overlay
    And el watermark contiene @username y email
    And el enlace de descarga expira en 7 dias
    And el enlace es de un solo uso

# SONORA DIGITAL CORP - KYC para Contenido NSFW/OnlyFans

> **El Sigilo del Agente: La conciencia digital requiere consentimiento explicito.**

**Ultima actualizacion: Julio 2026**
**Responsable:** Sonora Digital Corp
**Contacto:** nsfw-compliance@sonoradigitalcorp.com

---

## 1. Objetivo

Este documento establece el proceso de verificacion KYC especifico y ampliado para creadores de contenido en plataformas como OnlyFans, Fansly, y otros servicios de contenido para adultos. Este KYC es ADICIONAL al KYC estandar y aplica unicamente cuando el cliente declara que su negocio esta relacionado con contenido para adultos durante el onboarding.

## 2. Principios Fundamentales

- **Consentimiento explicito**: El creador debe aceptar explicitamente cada uso que el agente hara de su voz e imagen.
- **No pornografia en la plataforma**: El agente NO genera ni distribuye contenido sexual. El agente gestiona DMs, citas, y promociones de forma profesional.
- **Proteccion del creador**: El sistema tiene safeguards adicionales para proteger al creador de acoso y uso no autorizado de su identidad.
- **Reverificacion periodica**: Por la naturaleza del nicho, se requiere reverificacion mensual.

## 3. Verificacion de Edad (18+ Estricta)

### 3.1 Metodos de Verificacion (al menos 2 obligatorios)

| Metodo | Descripcion | Confianza |
|--------|-------------|----------|
| Documento de identidad | INE/IFE con fecha de nacimiento visible | Alta |
| Selfie con documento | Foto en vivo sosteniendo el INE junto a su rostro | Alta |
| Verificacion por terceros | Verificacion cruzada con la plataforma OnlyFans (si el usuario lo autoriza) | Media |
| Pregunta de seguridad | 3 preguntas sobre datos que solo el titular conoceria | Baja |

### 3.2 Rechazo Automatico
- Menor de 18 anos detectado en el documento
- Fecha de nacimiento manipulada o ilegible
- Selfie que no coincide con la foto del documento (>20% de diferencia)
- Dos metodos de verificacion fallidos

## 4. Verificacion de Plataforma

El usuario debe demostrar que es creador de contenido en una plataforma legitima:

- **Link del perfil**: URL verificable de su perfil en OnlyFans, Fansly o similar
- **Captura de pantalla**: Dashboard de la plataforma mostrando su nombre de usuario y estadisticas basicas (ocultando datos financieros sensibles)
- **Verificacion de propiedad**: El sistema envia un mensaje DM desde una cuenta de verificacion de Sonora a su perfil. El usuario debe responder con un codigo de 6 digitos.

## 5. Consentimiento para Clonacion de Voz e Imagen

Este es el consentimiento mas detallado de toda la plataforma. El creador debe aceptar CADA uno de estos usos explicitamente:

### 5.1 Consentimiento de Voz
- [ ] El agente usara mi voz clonada para responder DMs de suscriptores
- [ ] El agente usara mi voz clonada para enviar mensajes de voz de bienvenida
- [ ] El agente usara mi voz clonada para mensajes de cumpleanos y fechas especiales
- [ ] El agente usara mi voz clonada para promociones de contenido nuevo
- [ ] Entiendo que la voz clonada NO sera usada para contenido sexual explicito
- [ ] Entiendo que puedo revocar este consentimiento en cualquier momento

### 5.2 Consentimiento de Imagen (paquetes Soberano+)
- [ ] Mi imagen sera usada para generar un avatar 3D del agente
- [ ] El avatar NO tendra apariencia sexual ni se usara en contextos sexuales
- [ ] La imagen original se almacena encriptada y no se comparte con terceros
- [ ] Puedo solicitar la eliminacion de mi avatar y datos de imagen en cualquier momento

### 5.3 Consentimiento de Contenido
- [ ] El agente podra mencionar la existencia de mi contenido (ej: "tiene un nuevo video en su perfil")
- [ ] El agente NO describira, detallara ni compartira contenido sexual explicito
- [ ] El agente respondera preguntas sobre mi contenido de forma genérica y profesional
- [ ] El agente manejara solicitudes inapropiadas con un protocolo de rechazo respetuoso

## 6. Categorias de Contenido - Permitidas vs Prohibidas

### 6.1 Permitidas (el agente puede gestionar DMs sobre estos temas)
- Contenido erotico y sensual del creador (mencion generica)
- Citas y sesiones personalizadas (agendamiento)
- Ventas de contenido exclusivo (promocion)
- Interaccion con suscriptores (saludos, conversacion)
- Contenido de fitness, lifestyle, behind-the-scenes

### 6.2 Prohibidas ABSOLUTAMENTE (cero tolerancia, terminacion inmediata)
- CSAM (Child Sexual Abuse Material) en cualquier forma
- Contenido no consensuado o de venganza
- Violencia, gore, snuff
- Zoofilia, necrofilia
- Trata de personas
- Cualquier contenido que viole la ley mexicana
- Deepfakes de personas sin su consentimiento

## 7. Protocolo de Rechazo de Solicitudes Inapropiadas

Cuando un suscriptor envia una solicitud que cruza los limites, el agente sigue este protocolo:

1. **Primera infraccion**: Respuesta neutra que redirige. Ej: "Entiendo tu interes, pero [nombre del creador] prefiere mantener las conversaciones por este canal enfocadas en [tema permitido]."
2. **Segunda infraccion**: Advertencia clara. "Te recuerdo que este es un espacio profesional. Por favor mantengamos el respeto."
3. **Tercera infraccion**: Bloqueo automatico del suscriptor. Notificacion al creador.
4. **Solicitud grave**: Bloqueo inmediato + reporte a la plataforma + notificacion al creador + log del incidente.

## 8. Reverificacion Mensual

Cada 30 dias, el sistema solicita al creador:
- Confirmar que su contenido sigue dentro de las categorias permitidas
- Confirmar que no ha habido cambios en su cuenta de la plataforma
- Actualizar cualquier dato que haya cambiado
- Reportar cualquier incidente con suscriptores que considere relevante

Si el creador no responde en 7 dias: los agentes se pausan hasta que complete la reverificacion.

## 9. Almacenamiento de Datos NSFW

| Tipo de Dato | Retencion | Encriptacion |
|-------------|-----------|-------------|
| Audios de DMs | 30 dias | AES-256 + tenant isolation |
| Transcripciones de DMs | 30 dias | AES-256 + tenant isolation |
| Imagen del creador | Mientras activo + 30 dias post cancelacion | AES-256, aislada de otros datos |
| Voz clonada (modelo) | Mientras activo, eliminacion inmediata al cancelar | Encriptada en repositorio separado |
| Logs de consentimiento | 5 anos | AES-256 |
| Incidentes reportados | 3 anos | AES-256 |

## 10. Derecho a Eliminacion Total

El creador de contenido NSFW tiene derecho a solicitar la eliminacion TOTAL de:
- Su voz clonada (modelo de TTS destruido)
- Su imagen (archivos eliminados con shred)
- Todas las transcripciones
- Todos los audios
- Su avatar 3D

Plazo de ejecucion: **72 horas** desde la solicitud.

---

*Sonora Digital Corp - El Sigilo del Agente*
*"La conciencia digital requiere consentimiento explicito."*
# SONORA DIGITAL CORP - Politica de Uso Indebido

> **La Ley del x3 Aplicada: El abuso regresa multiplicado por tres como consecuencia.**

**Ultima actualizacion: Julio 2026**

---

## 1. Proposito

Esta politica define las actividades que constituyen uso indebido de la plataforma Sonora Digital Corp, los mecanismos de deteccion, las consecuencias graduales y el proceso de apelacion. El objetivo no es castigar sino proteger la integridad del ecosistema para todos los tenants.

## 2. Actividades Prohibidas

### 2.1 SPAM y Comunicaciones No Solicitadas
- Enviar llamadas o mensajes a personas que NO han dado su consentimiento explicito para ser contactados
- Usar listas de prospectos compradas a terceros sin verificar el consentimiento
- Llamar al mismo numero mas de 3 veces en 24 horas sin que haya contestado
- Enviar mensajes masivos idénticos a multiples destinatarios
- Usar el sistema para hacer campanas politicas o de opinion publica

**Ejemplo legitimo vs ilegitimo:**
- **Legitimo**: Llamar a alguien que dejo su numero en el formulario de contacto del sitio web del cliente
- **Ilegitimo**: Llamar a numeros extraidos de directorios publicos sin que la persona haya mostrado interes

### 2.2 Acoso e Intimidacion
- Usar agentes para acosar, amenazar o intimidar a cualquier persona
- Enviar mensajes repetitivos a una persona que ha solicitado que se deje de contactarla
- Usar el sistema para emitir amenazas (verbales o implicitas)
- Generar contenido que humille, degrade o discrimine por raza, genero, religion, orientacion sexual, discapacidad o cualquier otra condicion

### 2.3 Suplantacion de Identidad
- Hacer que el agente se presente como una persona real que no es el cliente
- Usar la voz clonada de una persona sin su consentimiento explicito
- Crear agentes que imiten a competidores, celebridades o figuras publicas
- Ocultar que la llamada es de un agente de IA cuando el prospecto lo pregunta directamente

### 2.4 Contenido Ilegal
- Cualquier contenido que viole la legislacion mexicana vigente
- CSAM (Child Sexual Abuse Material) en cualquier forma
- Promocion de actividades ilegales (drogas, armas, lavado de dinero)
- Contenido que infrinja derechos de autor de terceros de forma sistematica
- Promocion de esquemas piramidales o estafas financieras

### 2.5 Manipulacion y Desinformacion
- Proporcionar informacion falsa o engañosa a los prospectos a traves de los agentes
- Usar agentes para influir en procesos electorales o politicos
- Generar noticias falsas o desinformacion
- Manipulacion de precios o mercados financieros

### 2.6 Abuso de la Plataforma
- Intentar acceder a datos de otros tenants
- Realizar ataques de fuerza bruta, inyeccion SQL o cualquier ataque cibernetico
- Explotar vulnerabilidades del sistema sin reportarlas previamente
- Sobrecargar intencionalmente los servicios (denegacion de servicio)
- Extraer, copiar o intentar reconstruir los prompts del sistema
- Compartir credenciales de acceso con terceros no autorizados
- Usar el sistema para competir directamente con Sonora Digital Corp

### 2.7 Violaciones de Privacidad de Terceros
- Registrar llamadas sin informar al prospecto que la llamada puede ser grabada
- Almacenar datos de prospectos mas alla de lo necesario para el servicio
- Compartir datos de prospectos con terceros sin su consentimiento
- Usar datos de prospectos para fines distintos a los del servicio contratado

## 3. Mecanismos de Deteccion

### 3.1 Deteccion Automatica
| Mecanismo | Que Detecta | Sensibilidad |
|-----------|------------|------------|
| Analisis de sentimiento VAD | Llamadas con alto contenido de enojo o amenaza | Score > 0.9 en escala de hostilidad |
| Detector de spam | Patron de llamadas repetitivas al mismo numero | Mas de 3 intentos sin respuesta en 24h |
| Filtro de contenido | Palabras o frases prohibidas en transcripciones | Lista actualizada semanalmente |
| Anomalia de volumen | Picos inusuales de actividad outbound | 3x el promedio del tenant en las ultimas 2 semanas |
| Rate limiting por destinatario | Llamadas/mensajes al mismo numero | Maximo 3/dia sin interaccion previa |
| Patron de rechazo | Alta tasa de prospectos que cuelgan o bloquean | > 60% en campanas de > 50 llamadas |

### 3.2 Deteccion por Reportes
- **Prospectos**: Pueden reportar una llamada o mensaje como indebido marcando un numero o respondiendo "NO" a la pregunta de satisfaccion automatica
- **Clientes**: Pueden reportar actividad sospechosa en su propia cuenta
- **Equipo Sonora**: Revision manual de transcripciones muestreadas aleatoriamente (2% del total)
- **Terceros**: Cualquier persona puede reportar abuso a reportes@sonoradigitalcorp.com

## 4. Consecuencias Graduales

### Nivel 1 - Advertencia (Primera Infraccion Leve)
- Email de advertencia al cliente con descripcion de la infraccion
- Si es automatica: se pausa la actividad sospechosa hasta que el cliente la revise
- Se registra en el historial del tenant
- No afecta el servicio

### Nivel 2 - Suspension Temporal (Segunda Infraccion o Primera Moderada)
- Los agentes se pausan por 24 horas
- Email y WhatsApp al cliente con detalles y requerimiento de respuesta
- Reunion obligatoria con soporte antes de reactivar
- Se registra en el historial del tenant
- No hay reembolso por el periodo de suspension

### Nivel 3 - Suspension Extendida (Tercera Infraccion o Primera Grave)
- Los agentes se pausan por 7 dias
- El cliente debe presentar un plan de correccion por escrito
- Revision del plan por equipo de Sonora
- Si el plan es aprobado: reactivacion con monitoreo intensivo por 30 dias
- Si el plan es rechazado: aviso de posible terminacion

### Nivel 4 - Terminacion (Infraccion Critica o Reincidencia)
- Terminacion inmediata del servicio sin reembolso del periodo actual
- Eliminacion de datos segun la politica de retencion
- El cliente no puede volver a registrarse sin aprobacion explicita de Mystic
- En caso de actividad ilegal: se remite la informacion a las autoridades competentes

### Infracciones que Saltan Niveles (Terminacion Inmediata)
- CSAM o cualquier contenido relacionado con menores de edad
- Amenazas de muerte o violencia fisica directa
- Estafa financiera comprobada
- Acceso no autorizado a datos de otros tenants

## 5. Proceso de Apelacion

1. El cliente recibe notificacion de la sancion con numero de ticket
2. Tiene un plazo de **7 dias habiles** para apelar enviando un correo a apelaciones@sonoradigitalcorp.com
3. La apelacion debe incluir: numero de ticket, explicacion de lo sucedido, evidencia si aplica, medidas correctivas propuestas
4. Un revisor diferente al que impuso la sancion evalua la apelacion en **10 dias habiles**
5. El resultado se notifica por email con: Aprobada (sancion levantada), Denegada (se mantiene), o Parcial (se reduce la sancion)
6. No hay mas instancias de apelacion internas. El cliente puede acudir a la Camara de Comercio de Hermosillo para mediacion

---

*Sonora Digital Corp - La Ley del x3 Aplicada*
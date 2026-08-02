# SONORA DIGITAL CORP - Aviso de Privacidad

> **El Sigilo del Puente: Que los datos fluyan seguros entre mundos.**

**Ultima actualizacion: Julio 2026**
**Responsable:** Sonora Digital Corp
**Contacto DPO:** privacidad@sonoradigitalcorp.com
**Domicilio:** Hermosillo, Sonora, Mexico

---

## 1. Datos Personales que Recopilamos

Sonora Digital Corp recopila los siguientes datos personales como parte esencial de la prestacion de servicios de agentes de inteligencia artificial conversacionales:

### 1.1 Datos de Identidad del Cliente
- Nombre completo o razon social
- Correo electronico
- Numero telefonico (para contacto y para el servicio de numeros virtuales)
- Identificacion oficial (INE/IFE o pasaporte) - unicamente durante proceso de verificacion KYC
- RFC (Registro Federal de Contribuyentes) - para facturacion
- Direccion fiscal - para facturacion
- Nombre comercial y giro del negocio

### 1.2 Datos de Operacion del Servicio
- Grabaciones de audio de llamadas telefonicas atendidas por los agentes
- Transcripciones textuales de dichas llamadas
- Numeros telefonicos de prospectos y clientes del cliente
- Historial de conversaciones por WhatsApp, Telegram y otros canales
- Datos de contactos subidos por el cliente (listas de prospectos para outbound)
- Conocimiento base proporcionado por el cliente (FAQs, precios, servicios, politicas)
- Archivos de audio para clonacion de voz
- Imagenes para generacion de avatar (paquetes Soberano y Oraculo)

### 1.3 Datos Tecnicos
- Direcciones IP
- Tipo de navegador y sistema operativo
- Datos de uso del dashboard (paginas visitadas, tiempo de sesion)
- Logs de interaccion con la API

### 1.4 Datos de Pago
- Metodo de pago preferido (MercadoPago, Bitso, efectivo)
- Historial de transacciones
- Datos de facturacion

## 2. Finalidad del Tratamiento de Datos

Cada dato recopilado tiene una finalidad especifica y documentada:

| Tipo de Dato | Finalidad | Base Legal (LFPDPPP) |
|-------------|-----------|---------------------|
| Identidad | Verificacion KYC, contacto, facturacion | Consentimiento, Obligacion Legal |
| Audio de llamadas | Servicio de agentes IA, transcripcion, mejora de calidad | Consentimiento, Ejecucion de Contrato |
| Transcripciones | Servicio de agentes IA, analisis de calidad, medicion | Consentimiento, Ejecucion de Contrato |
| Prospectos | Servicio de atencion al cliente del cliente | Consentimiento del Cliente |
| Voz/Imagen | Clonacion de voz e imagen para agente | Consentimiento Explicito |
| Datos tecnicos | Seguridad, monitoreo, mejora del servicio | Interes Legitimo |
| Datos de pago | Cobro del servicio, facturacion | Ejecucion de Contrato, Obligacion Legal |

## 3. Como Almacenamos y Protegemos los Datos

### 3.1 Encriptacion en Reposo
- Todos los datos sensibles se almacenan encriptados con **AES-256-GCM**
- Las claves de encriptacion se rotan cada 90 dias automaticamente
- Las claves se almacenan en HashiCorp Vault (o equivalente Docker Secrets en produccion)
- Los audios de llamadas se almacenan encriptados en disco con acceso exclusivo del servicio de voz

### 3.2 Encriptacion en Transito
- Toda comunicacion entre el cliente y nuestros servidores usa **TLS 1.3**
- Los certificados SSL se renuevan automaticamente via Certbot/Let's Encrypt
- La comunicacion interna entre microservicios tambien usa TLS mutuo (mTLS)

### 3.3 Aislamiento Multi-Tenant (El Sigilo del Tenant)
- Cada cliente (tenant) tiene su espacio de datos completamente aislado
- Se implementa **Row Level Security (RLS)** en PostgreSQL para garantizar que ningun query pueda acceder a datos de otro tenant
- Cada tenant tiene un identificador UUID unico que se usa como filtro en TODAS las consultas a base de datos
- Los caches en Redis estan prefijados por tenant_id
- Los indices en Qdrant (busqueda semantica) estan separados por tenant

### 3.4 Control de Acceso
- Autenticacion via JWT con expiracion de 1 hora
- Refresh tokens con expiracion de 7 dias
- Cada token incluye el tenant_id y los permisos del usuario
- Role-based access control (RBAC) con roles: owner, admin, agent_viewer, readonly
- API keys rotadas cada 30 dias via proceso automatizado

### 3.5 Infraestructura de Seguridad
- Firewall UFW en VPS OVH con reglas estrictas
- Fail2ban para proteccion contra fuerza bruta
- WireGuard VPN para acceso administrativo
- Nginx como WAF (Web Application Firewall) con reglas de seguridad
- Rate limiting por tenant_id
- Monitoreo 24/7 con Prometheus + Grafana + Loki

## 4. Quien Tiene Acceso a los Datos

| Rol | Datos que Puede Ver | Datos que Puede NO Ver |
|-----|--------------------|-----------------------|
| **Mystic (Owner)** | Todo: todos los tenants, metricas, costos, audios | Nada restringido |
| **Cliente (Owner del Tenant)** | Sus propios datos, sus agentes, sus llamadas | Datos de otros tenants |
| **Empleado del Cliente (admin)** | Todo del tenant del cliente | Datos de otros tenants |
| **Empleado del Cliente (readonly)** | Metricas y reportes del tenant | Audios, transcripciones completas |
| **OpenRouter (LLM)** | Solo el texto del prompt y respuesta | Audios, datos personales, datos de otros tenants |
| **MercadoPago** | Solo datos de transaccion (monto, email) | Audios, conversaciones |
| **Bitso** | Solo datos de transaccion crypto | Audios, conversaciones |
| **Sonora (equipo soporte)** | Solo del tenant asignado, con permiso temporal | Sin acceso permanente a datos de clientes |

**Regla de oro del Sigilo del Tenant:** Ningun dato del Cliente A puede ser accedido por el Cliente B, ni siquiera por Mystic sin autorizacion explicita del Cliente A (excepto en caso de orden judicial o sospecha de actividad ilegal).

## 5. Datos que Compartimos con Terceros

Sonora Digital Corp NO vende, alquila ni comparte datos personales con fines comerciales. Los unicos terceros que reciben datos son:

1. **OpenRouter** (procesamiento de LLM): Se envia unicamente el texto del prompt del agente y la respuesta. No se envian datos personales del prospecto, audios, ni metadata. OpenRouter tiene su propia politica de privacidad y no usa datos para entrenar modelos sin consentimiento.

2. **MercadoPago** (procesamiento de pagos): Se comparte monto, email de contacto y concepto de pago. No se comparten datos de conversaciones ni audios.

3. **Bitso** (procesamiento de pagos crypto): Se comparte direccion de wallet y monto. No se comparten datos personales adicionales.

4. **Proveedores de infraestructura** (OVH, Cloudflare): Alojamiento de datos encriptados. El proveedor NO tiene acceso al contenido por estar encriptado.

5. **Autoridades competentes**: Unicamente mediante orden judicial o requerimiento legal vigente en Mexico.

## 6. Derechos ARCO (Acceso, Rectificacion, Cancelacion, Oposicion)

De acuerdo con la Ley Federal de Proteccion de Datos Personales en Posesion de los Particulares (LFPDPPP), usted tiene derecho a:

### 6.1 Acceso
- Solicitar informacion sobre que datos personales tenemos sobre usted
- Respuesta en maximo **20 dias habiles**
- Medio: email a privacidad@sonoradigitalcorp.com

### 6.2 Rectificacion
- Corregir datos personales inexactos o incompletos
- Se requiere identificacion del titular
- Respuesta en maximo **20 dias habiles**

### 6.3 Cancelacion
- Solicitar la eliminacion de sus datos personales
- Los datos se eliminan de produccion en **15 dias habiles**
- Los datos se retienen en backup encriptado por **90 dias** (por seguridad y cumplimiento legal)
- Los datos anonimizados pueden usarse para mejorar el servicio (sin identificar al titular)
- Los audios de llamadas se eliminan segun la politica de retencion de su paquete (30 dias Despertar, 90 dias Elevar, 365 dias Soberano, permanente Oraculo)

### 6.4 Oposicion
- Oponerse al tratamiento de sus datos para fines especificos
- Puede revocar el consentimiento en cualquier momento
- La revocacion no afecta el tratamiento realizado antes de la misma

## 7. Retencion de Datos

| Tipo de Dato | Despertar | Elevar | Soberano | Oraculo |
|-------------|-----------|--------|----------|--------|
| Audios de llamadas | 30 dias | 90 dias | 365 dias | Permanente |
| Transcripciones | 30 dias | 90 dias | 365 dias | Permanente |
| Datos de prospectos | Mientras activo | Mientras activo | Mientras activo | Mientras activo |
| Datos de cuenta | Mientras activo + 90 dias | Mientras activo + 90 dias | Mientras activo + 1 ano | Mientras activo + 1 ano |
| Datos de pago | 5 anos (fiscal) | 5 anos (fiscal) | 5 anos (fiscal) | 5 anos (fiscal) |
| Logs tecnicos | 30 dias | 30 dias | 90 dias | 90 dias |
| Datos de KYC | Mientras activo + 3 anos | Mientras activo + 3 anos | Mientras activo + 5 anos | Mientras activo + 5 anos |

Tras el periodo de retencion, los datos se eliminan de forma segura (borrado criptografico con shred multi-paso).

## 8. Cookies y Tecnologias Similares

Usamos cookies tecnicas esenciales para el funcionamiento del dashboard:
- **session_cookie**: Autenticacion (JWT). Expira en 7 dias.
- **csrf_token**: Proteccion contra ataques CSRF. Expira en 1 dia.
- **analytics_cookie**: Metricas de uso del dashboard (anonimizadas). Expira en 1 ano.
- **preferences_cookie**: Idioma, tema visual. Expira en 1 ano.

No usamos cookies de publicidad ni de terceros (excepto Google Analytics si el cliente lo habilita).

## 9. Transferencia Internacional de Datos

Los datos se procesan y almacenan en servidores de OVH ubicados fisicamente en **Mexico y Canada**. No se transfieren datos a otros paises excepto:

- **OpenRouter**: Los prompts de texto se envian a modelos de IA que pueden procesarse en servidores internacionales. Solo se envia texto, sin datos personales identificables del prospecto final.
- Si en el futuro se requiriera almacenar datos en servidores fuera de Mexico, se notificara a los clientes y se obtendra consentimiento explicito.

## 10. Menores de Edad

Sonora Digital Corp no ofrece servicios a menores de 18 anos. Para el paquete OnlyFans/NSFW, la verificacion de edad es estricta y obligatoria (ver KYC NSFW).

## 11. Cambios a este Aviso

Este aviso puede actualizarse periodicamente. Los cambios significativos se notificaran via email con al menos 30 dias de anticipacion. La version vigente siempre esta disponible en sonoradigitalcorp.com/privacidad.

---

**Contacto para derechos ARCO y dudas de privacidad:**
Email: privacidad@sonoradigitalcorp.com
Telefono: +52 662 353 8272
Domicilio: Hermosillo, Sonora, Mexico

---

*Sonora Digital Corp - El Sigilo del Puente*
*"Que los datos fluyan seguros entre mundos."*
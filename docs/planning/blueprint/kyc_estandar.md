# SONORA DIGITAL CORP - Proceso KYC Estandar

> **El Sigilo del Puente: Verificar identidad es proteger el templo.**

**Ultima actualizacion: Julio 2026**
**Responsable:** Sonora Digital Corp
**Contacto:** compliance@sonoradigitalcorp.com

---

## 1. Objetivo

Este documento establece el proceso de Verificacion de Conocimiento del Cliente (KYC - Know Your Customer) que Sonora Digital Corp aplica a todos los usuarios que contratan cualquiera de los paquetes de servicio (Despertar, Elevar, Soberano, Oraculo). El objetivo es verificar la identidad de quien opera los agentes de IA, prevenir el uso fraudulento de la plataforma y cumplir con las obligaciones legales mexicanas aplicables.

## 2. Alcance

Este proceso aplica a:
- **Persona Fisica**: Emprendedores, profesionistas independientes, creadores de contenido
- **Persona Moral**: Empresas, sociedades, asociaciones que contratan servicios

No aplica a: prospectos que llaman a los agentes de los clientes (estos son contactos del cliente, no usuarios de Sonora).

## 3. Niveles de Verificacion por Paquete

| Paquete | Nivel KYC | Biometrico | Verificacion Negocio | Tiempo Aprobacion |
|---------|-----------|-----------|---------------------|------------------|
| Despertar | Basico | No | No | Automatico (5 min) |
| Elevar | Estandar | Opcional | Si | 24 horas |
| Soberano | Completo | Si | Si | 48 horas |
| Oraculo | Completo+ | Si | Si + Due Diligence | 72 horas + Entrevista |

## 4. Documentos Aceptados

### 4.1 Persona Fisica

**Documento principal (obligatorio, uno de los siguientes):**
- INE/IFE vigente (frente y vuelta)
- Pasaporte mexicano vigente
- Cedula profesional (solo si no se cuenta con INE)
- Cartilla del Servicio Militar (solo como complemento)

**Documento complementario (opcional pero recomendado):**
- Comprobante de domicilio reciente (no mayor a 3 meses): recibo de luz, agua, telefono, estado de cuenta bancario
- RFC con homoclave
- Constancia de situacion fiscal SAT

### 4.2 Persona Moral

**Documento principal (obligatorio):**
- Acta constitutiva vigente con poderes del representante legal
- RFC de la empresa

**Del representante legal (obligatorio):**
- INE/IFE vigente del representante legal
- Comprobante de domicilio del representante (no mayor a 3 meses)

**Documentos adicionales segun giro:**
- Clinicas/Salud: Cedula profesional, numero de cesion
- Restaurantes: Licencia de funcionamiento, sanitaria
- Servicios financieros: Autorizacion de la CNBV o SHCP
- Educacion: Reconocimiento de validez oficial (RVOE)

## 5. Flujo de Verificacion

### 5.1 Paso 1: Registro Inicial
El usuario se registra con:
- Nombre completo / Razon social
- Correo electronico (verificado por link de confirmacion)
- Numero telefonico (verificado por codigo SMS)
- Contrasena (minimo 12 caracteres, Mayuscula + minuscula + numero + especial)

### 5.2 Paso 2: Subida de Documentos
El usuario sube fotografias o PDF de los documentos requeridos. Requisitos de la imagen:
- Minimo 300 DPI de resolucion
- Archivo maximo 10MB por documento
- Formatos aceptados: JPG, PNG, PDF
- Todos los bordes del documento deben ser visibles
- Sin reflejos, sombras ni cortes

### 5.3 Paso 3: OCR y Extraccion
Un proceso automatizado extrae datos del documento:
- Se usa Tesseract OCR o equivalente para leer el texto
- Se extrae: nombre, fecha de nacimiento, CURP, RFC, domicilio, fecha de emision, fecha de vigencia
- Se valida que los datos coincidan con los proporcionados en el registro
- Se verifica que el documento no este vencido

### 5.4 Paso 4: Validacion Automatica
El sistema realiza las siguientes validaciones sin intervencion humana:
- Formato del documento valido (no es una foto de una pantalla, no esta recortado)
- Coherencia de datos (nombre del documento = nombre del registro)
- Vigencia del documento
- Deteccion de manipulacion basica (tamper detection)
- Verificacion de que la foto no sea una copia de otro usuario (hash de imagen)

### 5.5 Paso 5: Aprobacion o Revision Manual

**Caso A - Aprobacion automatica (Paquete Despertar):**
Si todas las validaciones pasan, la cuenta se activa inmediatamente. El usuario puede comenzar a configurar su agente.

**Caso B - Revision manual (Paquetes Elevar, Soberano, Oraculo):**
Un operador humano de Sonora revisa los documentos en un plazo maximo de 24 horas. Motivos de revision manual:
- Imagen borrosa o ilegible
- Datos no coinciden exactamente
- Documento con vigencia proxima a vencer (< 3 meses)
- Deteccion de patron sospechoso (multiple registros con misma IP)
- Paquete que requiere verificacion de negocio adicional

### 5.6 Paso 6: Verificacion Biometrica (Paquetes Soberano y Oraculo)

Proceso opcional pero recomendado para paquetes premium:
- El usuario se toma una selfie en vivo desde el dashboard
- Se compara el rostro de la selfie con la foto del INE/IFE usando reconocimiento facial
- Umbral de coincidencia: 85% para aprobar
- Si no alcanza el umbral: se permite reintentar 2 veces, luego va a revision manual
- Los datos biometricos se eliminan inmediatamente despues de la comparacion (no se almacenan)

## 6. Triggers de Revision Manual

Los siguientes eventos activan una revision manual obligatoria:
- Registro de mas de 3 cuentas desde la misma IP en 24 horas
- Intento de registro con documento previamente utilizado por otra persona
- Deteccion de documento manipulado (tamper score > 0.7)
- El usuario selecciona el paquete Soberano u Oraculo
- El giro del negocio esta en categoria regulada (salud, finanzas, educacion)
- El usuario indica que usara el sistema para outbound masivo

## 7. Resultados Posibles

| Resultado | Descripcion | Accion |
|-----------|-------------|--------|
| APROBADO | Documentos validos, identidad verificada | Cuenta activada |
| RECHAZADO | Documentos falsos, manipulados o identidad no verificable | Cuenta suspendida, notificacion por email |
| PENDIENTE | Informacion adicional requerida | Email al usuario solicitando documento extra |
| ESCALADO | Sospecha de actividad ilegal | Revision por equipo legal de Sonora |

## 8. Retencion de Datos KYC

| Dato | Tiempo de Retencion | Post-Retencion |
|------|--------------------|---------------|
| Fotografias de documentos | Mientras activo + 3 anos | Borrado criptografico |
| Datos extraidos por OCR | Mientras activo + 3 anos | Borrado criptografico |
| Datos biometricos | 0 (no se almacenan) | N/A |
| Historial de verificacion | Mientras activo + 5 anos | Anonimizacion |
| Logs del proceso | 90 dias | Borrado automatico |

## 9. Revision Periodica

- Cada 12 meses: Se solicita al usuario confirmar que sus datos siguen vigentes
- Si el documento de identidad vence: Se notifica al usuario para subir uno nuevo
- Si no responde en 30 dias: Se pausan los agentes hasta que actualice

## 10. Apelaciones

Si un usuario es rechazado, puede apelar en un plazo de 15 dias habiles enviando un correo a compliance@sonoradigitalcorp.com con:
- Motivo de la apelacion
- Documentacion adicional si aplica
- Numero de ticket de la verificacion original

La apelacion se resuelve en un maximo de 10 dias habiles. Durante la apelacion, la cuenta permanece suspendida pero los datos no se eliminan.

---

*Sonora Digital Corp - El Sigilo del Puente*
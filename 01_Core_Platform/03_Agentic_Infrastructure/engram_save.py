#!/opt/hermes/venv/bin/python3
import engram as em

# Grabar memoria del DUEÑO (Luis Daniel Guerrero Enciso)
em.save(
    title='Luis Daniel Guerrero Enciso - Dueño',
    type='profile',
    content='**Identificación**: Luis Daniel Guerrero Enciso\n**Rol**: Dueño / COSUDE, operador principal del sistema\n**Contexto**: Sonora Digital Corp, ecosistema multi-tenant (SDC, Nathaly, Tu Bandera)\n**Contacto**: WhatsApp 5216623538272, email sonoradigitalcorp@gmail.com\n**Telegram**: @sonora_digital_bot\n**Estado**: Activo y autenticado\n**Memoria**: Twin digital, objetivo: mejorar el sistema cada sesión',
    user_id='5216623538272',
    session_id='setup-session'
)
print('Memoria Luis Daniel guardada')

# Grabar memoria de Roberto (presidente Tu Bandera)
em.save(
    title='Roberto Elizandro Lara - Presidente Tu Bandera',
    type='profile',
    content='**Identificación**: Roberto Elizandro Lara\n**Rol**: Presidente de Tu Bandera A.C.\n**Contexto**: Centro de rehabilitación Hermosillo, adicciones, 12 pasos NA\n**Contacto**: WhatsApp 526623645186\n**Estado**: Cliente del sistema, integrado con bot @TBasistente_bot',
    user_id='526623645186',
    session_id='setup-session'
)
print('Memoria Roberto guardada')

# Grabar memoria de Nathaly
em.save(
    title='Nathaly Hermosillo - Asistente Contable',
    type='profile',
    content='**Identificación**: Nathaly Hermosillo, contadora\n**Rol**: Asistente contable del sistema SDC\n**Contexto**: Manejo de contabilidad mensual, SAT, nóminas\n**Contacto**: WhatsApp 6623498589\n**Estado**: Activo, integrado con sistema contable\n**Memoria**: Perfil contable',
    user_id='6623498589',
    session_id='setup-session'
)
print('Memoria Nathaly guardada')

# Grabar memoria de Tubandera (empresa/centro)
em.save(
    title='Tu Bandera A.C. - Datos Principales',
    type='profile',
    content='**Identificación**: Tu Bandera A.C., rehabilitación en Hermosillo\n**Rol**: Centro de rehabilitación y apoyo familiar\n**Contexto**: Apoyo en adicciones, 12 pasos de NA, seguimiento familiar\n**Contacto**: WhatsApp 526623645186 (Roberto, presidencia)\n**Estado**: Operativo, integrado con knowledgebase adicciones\n**Memoria**: 66 chunks en Qdrant sobre adicciones',
    user_id='tu-bandera',
    session_id='setup-session'
)
print('Memoria Tubandera guardada')
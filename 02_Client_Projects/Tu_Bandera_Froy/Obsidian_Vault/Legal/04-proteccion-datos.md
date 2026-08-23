# Protección de Datos Personales — LFPDPPP

## Por qué es CRÍTICO aquí
Datos de adicción/salud = **datos personales sensibles** (art. 3 fracc. VI LFPDPPP). Tratamiento requiere **consentimiento EXPRESO Y ESCRITO** (firma autógrafa, electrónica avanzada o voz).

## Obligaciones de Tu Bandera A.C.
1. **Aviso de privacidad** integral publicado en sitio web y entregado al ingreso (identidad del responsable, finalidades, ARCO, transferencias, mecanismos).
2. Consentimiento expreso para: expediente clínico, fotografías/avances (¡las fotos que Roberto envía a familiares!), comunicaciones con familiares designados.
3. **Autorización explícita por familiar** antes de compartir cualquier avance (campo `permiso` en DB tubandera.db).
4. Medidas de seguridad: acceso restringido a expedientes, contraseñas, respaldos; el bot NO comparte datos entre tenants (aislamiento tenant_id).
5. Derechos ARCO: procedimiento documentado para acceso/rectificación/cancelación/oposición en plazos de ley (20 días hábiles respuesta).
6. Designar encargado de protección de datos (puede ser el propio representante en OSC pequeñas).
7. Transferencias a terceros (instituciones médicas) solo con consentimiento o fundamento legal.

## Checklist bot IA
- [ ] Aviso privacidad accesible desde comando del bot (/privacidad)
- [ ] Log de mensajes con retención definida y purga automática (ej. 12 meses)
- [ ] Nunca enviar avance/foto a familiar sin permiso=1 registrado

# FANUC SRVO Alarm Reference (troubleshooting para RYE)

## SRVO-001
Sobrecarga del servo. Causa: fricción mecánica, carga excesiva, freno defectuoso.
Acción: verificar mecanismo del eje, lubricar, revisar el freno. Aplica a cualquier
eje del R-2000iC.

## SRVO-032
Exceso de torque del servo. Causa: resistencia mecánica, inercia mal calculada
(PARAM 1121), carga dinámica alta. Acción: recalcular inercia, verificar acoplamiento,
ajustar ganancia de torque.

## SRVO-075
Posición fuera de límite (axis position error). Causa: movimiento fuera de zona
(soft-stop / hardware limit), colisión, comando de posición inválido en la celda.
Acción: verificar workspace, revisar COLLISION.DAO, liberar la colisión, Reset,
volver a home. Recurrente en hombro J2 de celdas R-2000iC para líneas BMW/Rivian.

## SRVO-104
Error de comunicación servo. Precede con frecuencia a fallas de visión Cognex
(Ethernet/IP timeout). Acción: revisar cableado, reiniciar el controlador EIP.

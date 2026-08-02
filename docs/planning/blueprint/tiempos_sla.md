# SONORA DIGITAL CORP - Acuerdo de Nivel de Servicio (SLA)

> **La Promesa del Templo: Cada reino digital merece fiabilidad medible.**

**Ultima actualizacion: Julio 2026**

---

## 1. Disponibilidad del Servicio (Uptime)

| Paquete | Uptime Target | Credito por cada 0.1% bajo target |
|---------|--------------|---------------------------------|
| Despertar | 99.0% | 5% del mes de servicio |
| Elevar | 99.5% | 8% del mes de servicio |
| Soberano | 99.9% | 15% del mes de servicio |
| Oraculo | 99.95% | 20% del mes de servicio |

La disponibilidad se mide como: (minutos totales del mes - minutos de downtime no programado) / minutos totales del mes.

No se considera downtime: (a) mantenimiento programado comunicado con 48h de anticipacion, (b) interrupciones por fuerza mayor, (c) interrupciones causadas por el cliente (ej: exceder limites del paquete), (d) interrupciones de proveedores de telecomunicaciones externos.

## 2. Latencia de Voz

| Paquete | Latencia Max Pipeline Completo | Latencia Max Respuesta Voz |
|---------|-------------------------------|--------------------------|
| Despertar | 3.0 segundos | 3.0 segundos |
| Elevar | 2.5 segundos | 2.5 segundos |
| Soberano | 2.5 segundos | 2.0 segundos |
| Oraculo | 2.0 segundos | 1.5 segundos |

La latencia se mide desde que el audio del prospecto llega al FreeSWITCH hasta que la respuesta de voz sale del Kokoro TTS. No incluye la latencia de la red telefonica (PSTN).

Si la latencia promedio mensual excede el target en mas del 20%, el cliente recibe un credito del 10% del mes.

## 3. Tiempos de Soporte

| Paquete | Canal | Tiempo Primera Respuesta | Tiempo Resolucion |
|---------|-------|-------------------------|------------------|
| Despertar | Email | 24 horas | 72 horas |
| Elevar | WhatsApp | 4 horas | 24 horas |
| Soberano | Dedicado | 1 hora | 8 horas |
| Oraculo | Linea directa Mystic | 15 minutos | 2 horas |

**Niveles de severidad:**
- **Critica**: Todos los agentes caidos o datos expuestos. Respuesta inmediata para Soberano/Oraculo.
- **Alta**: Un agente caido o funcionalidad principal rota. Respuesta segun tiempos de tabla.
- **Media**: Funcionalidad secundaria afectada. Doble del tiempo de tabla.
- **Baja**: Consulta general o solicitud de feature. Tiempo normal de tabla.

## 4. Ventanas de Mantenimiento

- **Menor (sin downtime)**: Domingos 02:00-06:00 CST. Rolling updates, no afecta servicio.
- **Mayor (hasta 30 min downtime)**: Domingos 02:00-08:00 CST. Aviso 48h antes.
- **Emergencia**: Sin ventana fija. Aviso via Telegram/WhatsApp lo antes posible.

Por ano no se excedera: 12 maintenances mayores y 52 maintenances menores.

## 5. Compensacion por Incumplimiento de SLA

El cliente debe solicitar el credito dentro de los 15 dias posteriores al mes afectado enviando un email a soporte@sonoradigitalcorp.com con el numero de tenant y la metrica afectada.

Los creditos se aplican como descuento en el siguiente mes de facturacion. No son reembolsables en efectivo ni transferibles.

El credito maximo acumulable en un periodo de 12 meses es del 50% del costo anual del paquete del cliente.

## 6. Recuperacion ante Desastre (DR)

| Paquete | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|---------|-------------------------------|-------------------------------|
| Despertar | 24 horas | 24 horas |
| Elevar | 8 horas | 12 horas |
| Soberano | 2 horas | 4 horas |
| Oraculo | 30 minutos | 1 hora |

RTO = tiempo maximo para restaurar el servicio. RPO = maximo de datos perdidos aceptable.

## 7. Exclusiones

No generan credito de SLA: problemas causados por el cliente, problemas de red del cliente, ataques DDoS contra el cliente especifico (no contra Sonora), uso de features en beta, problemas de proveedores externos (Telcel, OpenRouter, etc.) por mas de 4 horas.

---

*Sonora Digital Corp - La Promesa del Templo*
# Lecciones — SPEC-20260701-005

## Lo que funciono bien

1. **Protocolo de reparacion sistematica**: Diagnosticar → Fixear → Verificar — cada bug se trato como caso clinico, sin saltar pasos.
2. **Neo4j diagnosis**: Se encontro que el entrypoint personalizado ignoraba NEO4J_ env vars. Fix en Dockerfile fue permanente.
3. **War Room**: Tener un inventario visible de broken items evita que se olviden.
4. **CI verde como barrera**: 4 verdes consecutivos demostraron que el proceso funciona.
5. **Monitor de containers**: Systemd timer + events es suficiente para saber cuando algo muere.

## Lo que no funciono

1. **Neo4j volume perdido**: Al hacer fresh start se perdieron los datos anteriores del grafo. Falta backup de volumes Docker.
2. **B904 lint errors**: 10 archivos con raise from incorrecto. Pasaron desapercibidos porque ruff no los auto-fixea.
3. **Dashboards service usando system Python**: La primera vez que corrio, fallo porque no tenia pydantic. Habria que detectarlo en desarrollo.
4. **Firewall no verificado**: Se asumio que abrir puertos en ufw era suficiente, pero ABE Service escuchaba solo en 127.0.0.1.

## Proxima vez

1. Verificar B904 con ruff --select B904 antes de commit (no esperar a CI)
2. Hacer backup de volumes Docker antes de borrarlos (docker volume backup script)
3. Verificar que un servicio responde desde IP publica antes de darlo por terminado
4. Escribir mock tests para scrapers ANTES de agregar el siguiente provider
5. No cerrar CI sin antes verificar que la siguiente iteracion tiene menos broken items

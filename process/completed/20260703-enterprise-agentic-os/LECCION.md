# LECCION — Enterprise Agentic OS (M1, M2, M4)

| Campo | Valor |
|-------|-------|
| **Spec** | SPEC-20260703-004 |
| **Fecha** | 2026-07-03 |
| **Autor** | Mystic |

## Qué salió bien

- **age encryption** (M4): Instalación e implementación trivial en ambos equipos. `file *.age` confirma cifrado X25519. `decrypt-env.sh` funciona correctamente tanto con `source` como directo.
- **Nginx gateway** (M2): Se encontraron 6 servicios expuestos y se movieron todos a 127.0.0.1. SSL certs arreglados con `chmod 755`. nginx recargado sin errores.
- **fleet.yml como SSOT**: Se creó con servicios, secrets, networking, health targets. Válido YAML, desplegado en VPS.
- **Truth Guardian** (M1): Drift scanner detecta servicios faltantes/extra. Status API funciona. Health checker reporta 7/11 servicios saludables. 0 drifts actualmente.

## Qué falló

- **Systemd service stuck**: `systemctl start` colgó cuando el proceso ya estaba corriendo en estado "deactivating". Toca matar con `kill -9` y `reset-failed`.
- **Drift scanner ciclo infinito**: El primer intento no manejaba `port: {http: 7474, bolt: 7687}`. Corregido con isinstance check.
- **Log PermissionError**: systemd creó guardian.log como root, Python no pudo escribir. Solución: manejar PermissionError en logging y caer a stdout.
- **SSH timeout**: Varios comandos largos (systemctl + curl + python) timeoutaron porque systemctl se colgó.

## Qué aprender para la próxima

1. **Siempre probar edge cases en drift_scanner** — puertos como dict rompen set comprehension
2. **No confiar en systemctl restart cuando el servicio está stuck** — kill -9 primero
3. **SSH commands deben ser cortos y con timeout** — cadenas largas de pipes timeoutan
4. **Docker container names incluyen prefijo sdc-** — fleet.yml debe usar nombres reales de docker ps
5. **HOST vs HOSTNAME en Next.js** — Next.js 16 usa `-H` flag, no `HOST` env var

## Próximos pasos

- **M3**: Prometheus + Grafana + node_exporter
- **M5**: Qdrant collections por tenant
- **M6**: LLM gateway
- **M7**: Agent registry
- **M8**: Config unification (autogenerar TRUTH.md desde fleet.yml)

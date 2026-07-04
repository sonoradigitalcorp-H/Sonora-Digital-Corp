# LECCION — Cognitive Kernel Full Session

## Qué salió bien

1. **Arquitectura en fases**: A→B→C permitió entregar valor en cada paso sin esperar a todo listo
2. **Truth YAML**: 11 archivos, 46 reglas, validación automática — reemplaza TRUTH.md monolítico
3. **Event Bus unificado**: 462 eventos legacy migrados a un solo stream
4. **Agent Registry**: 9 agentes con capabilities explícitas, deny-all por defecto
5. **Economics Kernel**: Por primera vez sabemos cuánto cuesta cada operación ($1.65 spec vs $105 review)
6. **Config Unification**: fleet.yml genera configs de servicios automáticamente

## Qué falló

1. **SSH timeouts**: Comandos largos con pipes + systemctl timeoutan consistentemente. Solución: comandos cortos, separados
2. **systemctl restart**: Se cuelga cuando el servicio está en "deactivating". Solución: kill -9 + reset-failed
3. **Python import con guiones**: agent-metrics no es importable en Python (debe ser agent_metrics)
4. **auto-doc.py limitado**: No soporta --author ni --events. Toca generar docs manualmente

## Qué aprender para la próxima

1. Nombres de directorio Python: usar underscores, no guiones
2. systemd: kill -9 + reset-failed antes de restart
3. Descomposición grande funciona mejor: ~130 tasks en 3 fases fluyeron bien
4. SSH + systemd = timeout frecuente. Usar `nohup` y verificar después

# memory-guard — Protección contra freeze (laptop 3.3GB RAM)

## Cuándo usar
- PC lenta/congelada o al detectar RAM crítica (empatar con `free -m`)
- Al arrancar sesión si no hay guardia corriendo

## Guardia automático (ya instalado)
```bash
crontab -l | grep memory-guard   # verificar que existe */5
bash 01_Core_Platform/04_Automations_and_Workflows/memory-guard.sh
tail -5 /tmp/memory-guard.log
```

## Diagnóstico rápido (orden)
```bash
free -m | head -2          # RAM <400MB disponible = crítico
ss -tlnp | grep 18789      # pids únicos en gateway (debe ser 1)
ps aux --sort=-%mem | head -8
swapon --show              # swap USED alto = swap-thrash
```

## Reglas NO NEGOCIABLES (laptop 3.3GB)
1. NUNCA correr LLM local — siempre VPS OVH (OLLAMA_ENDPOINT, openclaw ollama.baseUrl)
2. NUNCA spawn procesos duplicados (openclaw gateway = 1 solo, el de systemd)
3. Matar accesorios (chrome-devtools-mcp, filesystem-mcp) cuando RAM<400MB
4. Un cambio atómico a la vez; verificar con guard después

## Gotchas
- `ss -tlnp` lista IPv4+IPv6 = 2 líneas por MISMO pid → contar pids únicos (`sort -u | wc -l`)
- openclaw spawnea gateway duplicados tras crash-loop breaker — matar extras sin tocar el systemd
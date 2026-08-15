# Skill: Conectividad Remota (VPS / servidores)

Diagnóstico ordenado cuando un servidor remoto (VPS OVH, producción, etc.) parece "caído" o inaccesible. Evita falsos negativos y bloqueos de ruta local.

## Cuándo usar
- `ssh` da timeout / connection timed out
- ping no responde
- curl a puertos HTTP no responde
- Usuario reporta servidor "caído" o "descomunicado"

## Protocolo (en orden)

### 1. NO declarar caída con solo tools locales
Ping/curl/SSH desde tu máquina prueban TU ruta, NO el servidor. El ISP local puede bloquear rutas a ciertos rangos (ej. OVH 149.56.x.x) de forma intermitente.

### 2. Verificar con port checker EXTERNO (lo primero)
```bash
curl -s "https://portchecker.io/api/v1/query" -X POST -H "Content-Type: application/json" \
  -d '{"host":"<IP>","ports":[22,2222,80,443,11434,8643]}'
```
- `status: true` → el puerto está ABIERTO desde internet → **el servidor está VIVO**, el problema es tu ruta local.
- `status: false` → puerto cerrado → posible firewall o servicio caído.

### 3. Si el checker externo dice ABIERTO pero tú no llegas → problema de ruta local
- Fuerza IPv4: `ssh -4 -o ConnectTimeout=15 host` o añade a `~/.ssh/config`:
  ```
  AddressFamily inet
  ConnectTimeout 20
  ```
- Mi salida IPv4 puede estar bloqueada hacia ese rango (los checkers de IP pueden devolver IPv6 → confunde). Verifica tu IP IPv4 real: `curl -4 -s https://api.ipify.org`
- La ruta puede ser INTERMITENTE: conecta a ratos, timeout a ratos. Reintenta en bucle:
  ```bash
  for i in 1 2 3 4 5; do
    out=$(timeout 40 ssh -o BatchMode=yes ovh 'echo CONECTADO' 2>&1)
    [ $? -eq 0 ] && echo "$out" && break
    sleep 8
  done
  ```
  OJO: al capturar con `$(...)` + `$?`, el exit code es del comando dentro del subshell — funciona. No uses pipe a head (rompe el exit code).

### 4. Si checker externo dice CERRADO
- Firewall (ufw/iptables/fail2ban) en el servidor
- Servicio no escuchando (docker caído, systemd failed)
- Servidor realmente apagado → requiere panel del proveedor (OVH/Hostinger API)

## Datos conocidos del ecosistema
- **VPS OVH `ovh`**: 149.56.46.173, user ubuntu, port 2222, key `~/.ssh/id_ed25519_sdc`. Docker: ollama (11434) + sdc-nginx (80/443). Modelos ollama: qwen3:4b, qwen2.5vl:3b, qwen2.5:3b, all-minilm, nomic-embed-text.
- **VPS producción**: 187.124.85.191 (a menudo realmente inalcanzable).
- **Dominio**: sonoradigitalcorp.com → 149.56.46.173 (DNS Hostinger, ns dns-parking.com).
- No hay credenciales OVH API locales (no se puede encender el VPS por API).

## Trampas
- `api.ipify.org`/`ifconfig.me` pueden devolver IPv6 → verificar con `curl -4`
- El VPS OVH no tiene hostname en known_hosts a veces → usar `-o StrictHostKeyChecking=no` en primera conexión
- La ruta al VPS OVH es NOTORIAMENTE intermitente desde este ISP — reintentar, no asumir caída
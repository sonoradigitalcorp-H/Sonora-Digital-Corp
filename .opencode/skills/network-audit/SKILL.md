# Network Audit Skill

Herramientas de diagnóstico de red sin nmap.

## Herramientas disponibles

```
ping         — verificar conectividad
python3      — escaneo de puertos TCP
arp-scan     — descubrimiento de hosts LAN (si instalado)
ip/ifconfig  — info de interfaces
```

## Escaneo de hosts vivos

```bash
for i in $(seq 1 254); do
  ping -c 1 -W 1 192.168.1.$i 2>/dev/null | grep 'bytes from' | awk '{print $4}' | tr -d ':'
done
```

## Escaneo de puertos TCP (Python)

```python
python3 -c "
import socket
def scan(ip, port):
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except: return False

targets = ['192.168.1.X', ...]
ports = [22,80,135,139,445,1433,3389,9047,3306,443,8080]
for ip in targets:
    open_ports = [str(p) for p in ports if scan(ip, p)]
    if open_ports: print(f'{ip}: {','.join(open_ports)}')
"
```

## Diagnóstico rápido de red

```bash
# Gateway
ping -c 2 $(ip route | grep default | awk '{print $3}')

# DNS
nslookup google.com 8.8.8.8

# Internet
ping -c 2 8.8.8.8

# ARP table
arp -a

# Interfaces
ip addr show
```

## Reporte de auditoría

Generar PDF con fpdf2 en formato landscape oscuro.

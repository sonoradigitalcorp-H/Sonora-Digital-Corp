# FreeSWITCH + SIP Trunk — Setup Rápido

## Prerequisitos
- VPS con Docker (✅)
- Cuenta Telnyx (https://telnyx.com) — $10 crédito inicial
- Número telefónico MX (~$0.85/mes)

## 1. Docker Compose

```yaml
# infra/docker-compose.freeswitch.yml
version: '3.8'
services:
  freeswitch:
    image: signalwire/freeswitch:latest
    container_name: sdc-freeswitch
    network_mode: host
    volumes:
      - freeswitch_config:/etc/freeswitch
      - freeswitch_db:/var/lib/freeswitch/db
      - freeswitch_recordings:/var/lib/freeswitch/recordings
      - ./freeswitch/scripts:/usr/share/freeswitch/scripts
    environment:
      - SIP_TRUNK_HOST=sip.telnyx.com
      - SIP_TRUNK_USER=your-username
      - SIP_TRUNK_PASS=your-password
      - SIP_TRUNK_NUMBER=+526621072254
    restart: unless-stopped
    mem_limit: 512m

volumes:
  freeswitch_config:
  freeswitch_db:
  freeswitch_recordings:
```

## 2. Config SIP Trunk (Telnyx)

```bash
# En Telnyx Portal:
# 1. Comprar número MX (~$0.85/mes)
# 2. Crear credential SIP (usuario + contraseña)
# 3. Configurar outbound SIP trunk

# En FreeSWITCH, configurar gateway:
cat > freeswitch/sip_profiles/external/telnyx.xml << 'EOF'
<include>
  <gateway name="telnyx">
    <param name="username" value="$${telnyx_username}"/>
    <param name="password" value="$${telnyx_password}"/>
    <param name="realm" value="sip.telnyx.com"/>
    <param name="proxy" value="sip.telnyx.com"/>
    <param name="register" value="true"/>
    <param name="register-transport" value="udp"/>
    <param name="caller-id-in-from" value="true"/>
  </gateway>
</include>
EOF
```

## 3. Llamada de Prueba

```bash
# Entrar a FreeSWITCH CLI
docker exec -it sdc-freeswitch fs_cli

# Llamada saliente a celular
fs_cli -x "originate {ignore_early_media=true}sofia/gateway/telnyx/526621072254 &playback(/tmp/saludo.wav)"

# Llamada entrante (recibir)
# Configurar inbound route en Telnyx → apunta a tu VPS:5060
```

## 4. Integración con IA (Whisper + LLM + Kokoro)

```bash
# FreeSWITCH → WebSocket → Whisper STT → deepseek → Kokoro TTS → FreeSWITCH
# Usando mod_websocket o script externo

# Script de ejemplo:
cat > freeswitch/scripts/ai_agent.py << 'PYEOF'
import websocket
import json
# Conectar a FreeSWITCH WebSocket
# Recibir audio → Whisper STT → deepseek → Kokoro TTS → enviar audio
PYEOF
```

## Costos

| Concepto | Costo |
|----------|-------|
| FreeSWITCH | $0 (open source) |
| Telnyx crédito inicial | $10 |
| Número MX | $0.85/mes |
| Minuto llamada MX | $0.003 |
| **Setup total** | **~$10 USD** |

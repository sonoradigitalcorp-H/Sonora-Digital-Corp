# FreeSWITCH + SIP Trunk — Setup para SDC
## Preparado para deploy cuando VPS reconecte

Comandos para cuando tengas SSH. Copia y pega en orden.

---

### 1. Levantar FreeSWITCH en Docker

```bash
# En el VPS:
docker run -d --name freeswitch \
  --restart unless-stopped \
  --network sdc-network \
  -p 5060:5060/udp -p 5060:5060/tcp \
  -p 5080:5080/udp -p 5080:5080/tcp \
  -p 7443:7443 -p 8021:8021 \
  -v freeswitch_conf:/etc/freeswitch \
  -v freeswitch_db:/var/lib/freeswitch/db \
  -v freeswitch_recordings:/recordings \
  signalwire/freeswitch:latest

# Verificar que corre:
docker logs freeswitch --tail 5
docker exec freeswitch fs_cli -x "status"
```

### 2. SIP Trunk (Telnyx)

```bash
# Registrarse en telnyx.com (~$10 crédito inicial)
# Comprar número MX (~$0.85/mes)
# Obtener credenciales SIP

# Configurar trunk en FreeSWITCH:
docker exec -it freeswitch bash
cat > /etc/freeswitch/sip_profiles/external/telnyx.xml << 'EOF'
<gateway name="telnyx">
  <param name="username" value="TWILIO_USERNAME"/>
  <param name="password" value="TWILIO_PASSWORD"/>
  <param name="realm" value="sip.telnyx.com"/>
  <param name="from-user" value="TU_NUMERO"/>
  <param name="from-domain" value="sip.telnyx.com"/>
  <param name="proxy" value="sip.telnyx.com"/>
  <param name="register" value="true"/>
</gateway>
EOF

# Recargar config:
docker exec freeswitch fs_cli -x "sofia profile external restart"
docker exec freeswitch fs_cli -x "sofia status gateway telnyx"
```

### 3. Probar llamada

```bash
# Llamar a un celular real:
docker exec freeswitch fs_cli -x \
  "originate {ignore_early_media=true}sofia/gateway/telnyx/526621072254 &playback(/etc/freeswitch/music.wav)"

# Si escuchas música → el trunk funciona ✅
```

### 4. Conectar con la IA (Whisper → deepseek → Kokoro)

```bash
# FreeSWITCH → WebSocket envía audio a nuestra app
# apps/twilio-voice/server.py ya tiene el pipeline listo
# Solo apuntar FreeSWITCH al WebSocket:

python3 -m apps.twilio_voice.server --mode freeswitch
```

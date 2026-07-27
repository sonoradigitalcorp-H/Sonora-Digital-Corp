# MVP — SDC Platform (Local Edition)

## Lo que funciona HOY sin VPS

```
✅  GRIMOIRE 3D (∞ + stickers + avatar + cámara)
    → apps/grimoire/dist/ — build listo
    → python3 -m http.server 9090 → localhost:9090

✅  VOZ (edge-tts)
    → "Hola, prueba local." → genera audio MP3
    → pip install edge-tts → funciona

✅  ENGRAM (memoria)
    → engram.db — sesión guardada
    → layer 4 (business), importance 3 (high)

✅  COST TRACKER
    → data/cost_tracker.db — inicializado con sample data

✅  PARTNER DASHBOARD
    → apps/grimoire/src/lib/PartnerDashboard.svelte
    → Precios que partner define
    → Comisión SDC oculta (10%)
    → Falta integrar en el build

✅  SDD SPEC KIT
    → process/active/sdd-kit-ecosystem/
    → 17 FRs, 20 escenarios, score 65

✅  ROUTER INTELIGENTE 80/20
    → core/router_inteligente.py
    → 80% local gratis, 20% cloud $0.00026
```

## Lo que necesita VPS (cuando SSH responda)

```
⬜  FREESWITCH + SIP TRUNK
    → Llamadas telefónicas reales
    → Docker run + Telnyx config

⬜  KOKORO TTS (82M params, necesita GPU/CPU con más RAM)
    → En VPS ya está instalado
    → En laptop no, pero edge-tts funciona como fallback

⬜  PRODUCCIÓN (ngixn + SSL + dominio)
    → grimorio.sonoradigitalcorp.com
    → voice.sonoradigitalcorp.com
    → api.sonoradigitalcorp.com

⬜  TWILIO VOICE BRIDGE
    → apps/twilio-voice/server.py
    → Necesita credenciales Twilio
```

## Cómo probar el MVP local ahora

```bash
# 1. Servir Grimoire
cd ~/Escritorio/sonora-digital-corp/apps/grimoire
python3 -m http.server 9090
# Abrir: http://localhost:9090

# 2. Probar voz
pip install edge-tts
python3 -c "
import asyncio, edge_tts
async def t(): await edge_tts.Communicate('Hola mundo', 'es-MX-DaliaNeural').save('/tmp/test.mp3')
asyncio.run(t())
print('✅ Audio en /tmp/test.mp3')
"

# 3. Ver memoria engram
python3 -c "
import sqlite3
conn = sqlite3.connect('engram.db')
for r in conn.execute('SELECT key, layer, importance, created_at FROM memories ORDER BY created_at DESC'):
    print(f'  [{r[2]}] {r[0]} (layer {r[1]}, {r[3]})')
"

# 4. Ver costos
python3 -c "
import sqlite3
conn = sqlite3.connect('data/cost_tracker.db')
total = conn.execute('SELECT SUM(cost) FROM operations').fetchone()[0]
print(f'💰 Costo total registrado: \${total:.6f}')
"
```

## Próximo paso cuando VPS esté listo

```
1. bash ops/runbooks/deploy-grimoire.sh
2. docker run -d --name freeswitch signalwire/freeswitch:latest
3. python3 -m apps.twilio_voice.server
4. Configurar Telnyx SIP Trunk
5. Probar primera llamada real
```

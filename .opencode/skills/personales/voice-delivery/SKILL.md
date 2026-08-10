# Voice Delivery Pipeline — SKILL

## Pipeline SIMPLE y ligero (SIN XTTS, SIN modelos pesados)
Método comprobado (memorias #308, #365, #432, #498): 
`texto → edge-tts MP3 → ffmpeg imageio → OGG opus → Telegram sendVoice / wacli send --ptt`

## COMANDO UNIFICADO (recomendado)
Script `01_Core_Platform/03_Agentic_Infrastructure/voice_reply.py`
```bash
# Enviar voz a Telegram (texto → TTS → OGG → sendVoice)
python3 voice_reply.py --bot aztroc --chat 5738935134 --text "Hola"
python3 voice_reply.py --bot rye --chat 5738935134 --text "Hola" --voice es-MX-DaliaNeural

# Enviar un audio ya existente
python3 voice_reply.py --bot aztroc --chat 5738935134 --file /ruta/audio.ogg
```

### Bots configurados
| --bot | token | voz default |
|-------|-------|-------------|
| aztroc | telegram-aztroc.token (@Aztro_tech_bot, César) | es-MX-JorgeNeural (masc. mexicana) |
| rye | telegram-rye.token (@RyE_production_bot, Iván) | es-MX-DaliaNeural (fem. mexicana) |

## Cómo responder con voz a un mensaje que llegó al bot
1. El usuario pide audio / envía nota de voz
2. El agente genera texto de respuesta (via openclaw agent)
3. Se manda ese texto por voice_reply.py → bot envía audio

## ffmpeg estático (cuando el del sistema falla: libva)
```
/home/mystic/.local/lib/python3.10/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2
```

## Voces edge-tts (ligeras, sin modelo local, instantáneas)
| Voz | Tipo | Uso |
|-----|------|-----|
| es-MX-DaliaNeural | Femenino mexicano | default rye |
| es-MX-JorgeNeural | Masculino mexicano | default aztroc (cercano a César) |

## Errores conocidos
- ffmpeg del sistema: `libva error` → usar imageio_ffmpeg
- wacli contacts: vacío → usar números directos
- Chat id Telegram: de getUpdates del bot
- Kokoro (em_alex) NO es voz clonada real — es voz sintética EN. Usar edge-tts es-MX para español mexicano.

## REGLA CRÍTICA: NO cargar modelos ML en laptop <=4GB RAM
- NO instalar/usar XTTS/TTS(elcoquai) — congela la laptop (3.3GB RAM con opencode+antigravity+openclaw)
- edge-tts = sin modelo local = ligero y rápido. Usarlo siempre.
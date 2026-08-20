# Skill: youtube-video-analisis

Analiza videos de YouTube: transcripción → resumen → aprendizajes clave → memoria Engram → (opcional) crear skill específico del tema.

## Cuándo usar

Cuando el Jefe pida: "analiza este video", "transcribe este video", "aprende de este video", "crea skill de este video", o pase una URL de YouTube.

## Paso 1 — Transcribir (SIEMPRE ruta ligera primero, $0)

```bash
# Script canónico del skill media-retrieval (acepta URL corta, embed, shorts, ID)
python3 ~/.hermes/skills/media/media-retrieval/scripts/fetch_transcript.py "URL" --language es,en --timestamps
# Salida: JSON con full_text + segment_count + duration
```

**Fallbacks en orden (NO saltar):**
1. `--language es,en` (español primero — el Jefe ve contenido en español)
2. Sin `--language` (cualquier transcript disponible)
3. Si NO hay transcript (video sin subtítulos) → **whisper local** (ya instalado: `faster-whisper` 1.2.1):
   ```bash
   yt-dlp -f "bestaudio" -o /tmp/video_audio.%(ext)s "URL"
   python3 -c "
   from faster_whisper import WhisperModel
   m = WhisperModel('small', device='cpu', compute_type='int8')
   segs, _ = m.transcribe('/tmp/video_audio.mp3', language='es')
   print(''.join(s.text for s in segs))
   "
   ```
   ⚠️ Whisper local = carga media en laptop 3.3GB RAM → solo si es imprescindible, modelos `small`/`base` (NUNCA `large`).

## Paso 2 — Guardar transcript

```bash
mkdir -p "01_Core_Platform/05_SelfImprovement/learning/youtube"
python3 ~/.hermes/skills/media/media-retrieval/scripts/fetch_transcript.py "URL" --language es --text-only \
  > "01_Core_Platform/05_SelfImprovement/learning/youtube/<VIDEO_ID>_<tema>_transcript.txt"
```

## Paso 3 — Analizar (yo, el LLM, hago esto — no otro modelo)

Con el transcript en contexto, extraer SIEMPRE:
1. **Tema central** — 1 frase
2. **Quién habla** — autor/canal, credibilidad
3. **Duración + idioma**
4. **Key takeaways** — 5-10 aprendizajes accionables con evidencia del video
5. **Oportunidades para Sonora Digital Corp** — qué se puede vender/aplicar (AEO, agentes, monetización, etc.)
6. **Discrepancias/riesgos** — qué dudoso o a verificar

## Paso 4 — Guardar en memoria

```bash
mem_save  # type=learning, title="Video: <tema>"
```
Content: Qué aprendimos, de quién, takeaways top, dónde se guardó el transcript.

## Paso 5 — Skill específico del tema (si el Jefe lo pide o el tema es accionable)

Crear `~/.hermes/skills/<categoria>/<tema>-<algo>/SKILL.md` con:
- Qué es el tema (resumen del video)
- Herramientas/aplicación práctica para SDC
- Pipeline si aplica
- Referencias al transcript

## Ejemplo verificado (2026-08-20)

- URL: `https://www.youtube.com/watch?v=qT784npVXF4`
- Canal: Juanpe Navarro / Divisual Project
- Tema: Cloudflare + IA — cómo cambia internet (AI Crawler Control, Agent Readiness, PayPerCrawl/HTTP 402, MPP, AEO)
- Transcript: `01_Core_Platform/05_SelfImprovement/learning/youtube/qT784npVXF4_cloudflare_ia_transcript.txt` (4023 palabras)
- Skill resultante: `~/.hermes/skills/sdc/cloudflare-ia-internet/SKILL.md`

## Costo

$0 (youtube-transcript-api gratis). Whisper local solo si no hay subtítulos (CPU, gratis).
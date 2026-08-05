# Aztrotech César Digital Twin — SDD v1.0

## 1. Arquitectura General

```
[Clientes] ──TG/WA──→ César DT (deepseek-v4-flash + RAG + Voz clonada)
                           │
                    ┌──────┼──────────┐
                    ▼      ▼          ▼
                 MinIO   Qdrant     Neo4j
              (archivos) (vectores) (grafos)
                    │
              FAL AI (imágenes)
```

## 2. Infraestructura (VPS 149.56.46.173)

| Servicio | Puerto | Tipo | Estado |
|----------|--------|------|--------|
| Telegram Bot | — | systemd | ✅ |
| WhatsApp Bot | — | systemd | ✅ |
| MinIO (S3) | 9000/9001 | Docker | ✅ |
| Qdrant | 6333/6334 | Docker | ✅ |
| Neo4j | 7687/7474 | Docker | ✅ |
| Postgres | 5432 | Docker | ✅ |
| Redis | 6379 | Docker | ✅ |
| wacli | — | local | ✅ |

## 3. Bots

### 3.1 Telegram Bot (`bot.py`)
- **ID**: @Aztro_tech_bot → @AztrotechCesarDT
- **Token**: `AZTROTECH_BOT_TOKEN`
- **LLM**: deepseek-v4-flash via opencode.ai/zen/go/v1
- **TTS**: Qwen3-TTS (voz clonada de César)
- **RAG**: Obsidian vault indexado en Qdrant
- **Handler**: texto, fotos, audio, video, documentos → MinIO

### 3.2 WhatsApp Bot (`whatsapp_bot.py`)
- **WA JID**: 5216623538272@s.whatsapp.net
- **Polling**: cada 10s via wacli
- **César JID**: 5216621072254@s.whatsapp.net

## 4. Voz Clonada

- **Modelo**: Qwen3-TTS-12Hz-0.6B-Base
- **Referencia**: `skills/voice/cesar/processed/cesar-ref-short.wav`
- **Output**: WAV 24kHz, convertido a MP3 para Telegram
- **Pipeline**: text → Qwen3TTSModel.generate_voice_clone() → WAV → bytes

## 5. Imagen Clonada

- **API**: FAL AI (fal-client)
- **Modelo**: fal-ai/flux-pro/v1.1 con reference_type=identity
- **Fotos referencia**: MinIO bucket astrotech/photos/ (15 fotos de César)
- **Output**: URL pública de FAL, copiada a MinIO bucket cesar/

## 6. Almacenamiento (MinIO)

| Bucket: astrotech | Descripción |
|-------------------|-------------|
| /photos/ | Fotos de clientes y César |
| /audio/ | Audios de voz |
| /videos/ | Videos |
| /documents/ | Documentos PDF, DOCX |
| /cesar/ | Generated assets de César |

## 7. RAG Pipeline

- **Fuente**: Obsidian vault (~/Documents/sdc-brain-vault/)
- **Chunker**: skills/rag/chunker.py — split por headings
- **Embeddings**: all-MiniLM-L6-v2 (384-dim)
- **Vector DB**: Qdrant colección "obsidian-vault" (158 chunks)
- **Retriever**: top-5 chunks por similitud coseno

## 8. Personalidad (prompt-cesar.md)

César Holguín, fundador CEO de AztroTech.
- Habla en primera persona
- Estilo directo, cálido, mexicano
- NO es IA ni bot
- Servicios: Empleado Digital, Ventas Autónomo, Dev a Medida, 90 Días, Socio Estratégico

## 9. Comandos

```bash
# Deploy
rsync -avz --checksum tenants/astrotech/ ovh:path/

# Logs
ssh ovh 'journalctl -u sdc-aztrotech-telegram -n 50 --no-pager'
ssh ovh 'journalctl -u sdc-aztrotech-whatsapp -n 50 --no-pager'

# Restart
ssh ovh 'sudo systemctl restart sdc-aztrotech-telegram'
ssh ovh 'sudo systemctl restart sdc-aztrotech-whatsapp'

# MinIO
http://149.56.46.173:9001 (admin/minioadmin123)

# VPS
ssh ovh
```

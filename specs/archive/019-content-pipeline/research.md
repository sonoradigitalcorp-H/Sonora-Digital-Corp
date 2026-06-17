# Research: Content Pipeline

**Spec**: spec.md

## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| Fal.ai | Video/Imagen rápido, API | Costo por uso | ✅ Generación principal |
| ComfyUI | Local, gratuito | GPU requerida | ⚠️ Pendiente |
| Edge-TTS | Gratuito, voces realistas | Solo 1 voz | ✅ TTS principal |
| ElevenLabs | Voces ultra realistas | Costo | ⚠️ Opcional |
| NotebookLM | Investigación profunda | Sin API pública | ❌ No disponible |

## Decisión: Pipeline Autónomo sin NotebookLM
- NotebookLM no tiene API. Usaremos DeepSeek V4 + Engram para investigación similar.
- Contenido generado localmente y distribuido multi-canal.

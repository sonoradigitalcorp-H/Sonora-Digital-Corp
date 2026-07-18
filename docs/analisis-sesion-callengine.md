# Análisis de Sesión: Call Engine Eval

## Resumen
Logramos que las evaluaciones de prompts del Call Engine funcionaran al 100% (6/6)
y expandimos el sistema a 5 nichos de industria con manejo de objeciones basado en
Brian Tracy (Seminario Fénix).

---

## Errores y Aprendizajes

### 1. Depender de `openclaw infer`
- **Qué pasó**: Intenté usar `openclaw infer model run` en 4+ ocasiones.
  Siempre colgaba o devolvía "No models found".
- **Tiempo perdido**: ~15 min
- **Lección**: `openclaw infer` no funciona para este caso de uso.
  No volver a intentarlo sin verificar primero que el catálogo de modelos
  esté disponible con `openclaw models list`.

### 2. `opencode run --format json --auto` no produce output
- **Qué pasó**: Intenté obtener JSON estructurado. El comando
  devuelve `UnknownError` sin output utilizable.
- **Tiempo perdido**: ~10 min
- **Lección**: `opencode run <mensaje>` sin flags es la única variante
  que funciona programáticamente. stdout = respuesta, stderr = metadatos.

### 3. `opencode run --auto` cuelga
- **Qué pasó**: El flag `--auto` hace que el comando nunca termine.
- **Tiempo perdido**: ~15 min probando con/sin `--auto` y `--pure`
- **Lección**: No usar `--auto`. Correr sin flags. El comando
  funciona en modo interactivo y devuelve la respuesta por stdout igual.

### 4. `--pure` activa validación de schema del config
- **Qué pasó**: `opencode run --pure` validó el `opencode.json`
  y falló por la llave `fallbackProvider` que era inválida.
- **Tiempo perdido**: ~10 min
- **Lección**: `--pure` no es "solo ignorar plugins" — también
  valida el schema del config contra una versión estricta.
  Si falla, revisar el config.

### 5. SSH tunnel IPv6 vs IPv4
- **Qué pasó**: SSH tunnel escuchaba en `[::1]:11434` (IPv6)
  pero curl apuntaba a `127.0.0.1:11434` (IPv4 → Ollama local).
- **Tiempo perdido**: ~5 min
- **Lección**: Verificar siempre con `ss -tlnp` qué interfaz
  está escuchando cada proceso.

### 6. VPS Ollama llama3.2:3b timeout en prompts complejos
- **Qué pasó**: El modelo de 3B funcionaba para queries simples
  pero timeout en prompts de objection handler (contexto largo).
- **Tiempo perdido**: ~10 min debugueando timeouts
- **Lección**: Modelos pequeños (3B) en CPU no son confiables
  para prompts complejos de ventas con contexto multi-turno.

### 7. Output parsing incorrecto
- **Qué pasó**: Primera versión de `ask_llm()` buscaba la frase
  "deepseek" en stdout para encontrar la respuesta. La respuesta
  REAL está directa en stdout sin prefijos.
- **Tiempo perdido**: ~5 min
- **Lección**: Probar primero el output crudo con `repr()` antes
  de diseñar parsing.

### 8. Eval_niches.py timeout por llamadas secuenciales
- **Qué pasó**: Cada test llama a `opencode run` (~30-60s).
  Con 8+ tests por nicho, un nicho completo toma ~8 min.
  Con 5 nichos son ~40 min.
- **Tiempo perdido**: N/A (aún sin resolver)
- **Lección**: Necesito paralelizar las llamadas o reducir
  el número de tests por nicho para uso rápido.

---

## Aciertos

### 1. `opencode run <mensaje>` sin flags
- **Qué es**: La única forma de inferencia programática que funciona.
  stdout = respuesta limpia. ~30-60s por call.
- **Por qué funcionó**: No requiere TTY, no valida schema,
  no usa plugins. Es el modo más básico y robusto.

### 2. Estructura de Nichos (5 industrias)
- **Qué es**: `promptfoo/niches/{music,agencies,real_estate,ecommerce,prof_services}/`
- **Por qué funciona**: Cada nicho tiene prompts y tests
  independientes. Se pueden evaluar por separado o todos juntos.
- **Archivos**: 15 prompts + 15 test files = 30 archivos

### 3. Objection Handler basado en Brian Tracy
- **Qué es**: Método de 5 pasos del Seminario Fénix:
  1. Escucha completa
  2. Pausa (3 segundos)
  3. Valida + "¿A qué te refieres exactamente?"
  4. Responde (Feel → Felt → Found)
  5. Confirma + Cierra
- **Por qué funciona**: Es un framework probado de ventas,
  no inventado. Cada paso tiene un propósito psicológico específico.

### 4. Eval runner con --niche flag
- **Qué es**: `python3 scripts/eval_niches.py --niche music`
  o sin flag para todos los nichos.
- **Por qué funciona**: Permite evaluar incrementalmente
  sin esperar 40 min por todos los nichos.

### 5. Limpieza del config
- **Qué es**: Se eliminó la llave inválida `fallbackProvider`
  del `/home/mystic/sonora-digital-corp/opencode.json`.
- **Por qué funcionó**: Permitió que `opencode run` no fallara
  al leer el config (aunque no uses `--pure`).

---

## Estado de la Memoria (Engram)

### Lo que está guardado
- Session summaries (2): sesión actual y anterior
- Bugfix: eval scripts fixed
- Milestones: Clone Service, Prompt evals, Test Suite
- Architecture: costos, ecosistema SDC, Digital Brain
- Config: Obsidian vault, OmniVoice agent

### Lo que FALTA guardar
- [ ] Estructura de nichos (5 industrias) — ARCHITECTURE
- [ ] Objection handler Brian Tracy framework — DECISION
- [ ] Eval runner eval_niches.py — PATTERN
- [ ] Lista de errores/aprendizajes de esta sesión — LEARNING
- [ ] Comando `opencode run` sin flags como estándar — PATTERN

### Recomendación de secciones
```
project/ (raíz, proyecto actual)
├── bugfix/        → errores corregidos
├── decision/      → decisiones arquitectónicas
├── pattern/       → patrones que funcionan
├── learning/      → descubrimientos y lecciones
├── milestone/     → hitos completados
├── config/        → configuraciones
├── architecture/  → diseño del sistema
└── session_summary/ → resúmenes de sesión

sonora-digital-corp/
├── ... (paralelo para trabajo en directorio real)
```

# Lecciones — SPEC-20260701-008

## Lo que funciono bien
1. ask_local() en llm.py funciona con Ollama local — respuesta en ~45s (primera carga)
2. Los 3 agentes (monitor, healer, notifier) se comunican via Redis Stream correctamente
3. El patron de consumer groups en Redis permite que cada agente tenga su propia cola

## Lo que no funciono
1. La primera llamada a Ollama es lenta (~45s) porque carga el modelo en memoria
2. mock de `playwright.sync_api` requiere import dinamico — no se puede mockear como atributo del modulo

## Proxima vez
1. Usar qwen3:4b-64k para decisiones rapidas y deepseek para razonamiento complejo
2. Documentar el patron de mock para playwright en tests

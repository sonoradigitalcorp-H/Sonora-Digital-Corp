# AGENTS MANIFEST - Sonora Digital Corp (AI Agentic Native)
## REGLAS DE CONTEXTO PARA CUALQUIER IA (OpenCode, OpenHands, Claude)

Cualquier agente de IA que opere en este directorio DEBE leer y obedecer este manifiesto. 
Sonora Digital Corp es una empresa Agentic Native. No programamos desde cero si ya tenemos herramientas instaladas.

### 1. Reglas de Estructura (CERO DESORDEN)
- La creación de carpetas está PROHIBIDA sin autorización explícita.
- Código de clientes -> `02_Client_Projects/[Cliente]/02_Source_Code/`
- Prompts/Skills de voz -> `02_Client_Projects/[Cliente]/05_Agentic_Skills/`
- Pruebas temporales -> `03_Sandbox_and_RnD/`

### 2. Stack Agentic Native (HERRAMIENTAS DISPONIBLES)
Si te piden automatizar algo, USA estas herramientas. NO instales npm/pip innecesarios.
- **Motor LLM Local:** Ollama (Modelos uncensored/dolphin corriendo localmente).
- **Memoria Persistente (MCP):** Engram. Conectado a bases de datos locales. Úsalo para dar contexto a los bots.
- **Voz a Texto (STT):** Whisper CLI. Úsalo para transcribir audios de clientes.
- **Texto a Voz (TTS):** Motores locales instalados. Úsalo para agentes de voz.
- **Orquestación:** OpenClaw y n8n.

### 3. Flujo de Trabajo Agentic (AUTOMATIZACIÓN)
Cuando se pida un nuevo bot o agente:
1. Definir requisitos en `01_Discovery/`.
2. Crear el código conector en `02_Source_Code/`.
3. Configurar los prompts/voz en `05_Agentic_Skills/`.
4. Registrar la automatización en `01_Core_Platform/04_Automations_and_Workflows/`.

### 4. Rutas de Orquestación (Workflows)
Cuando construyas una automatización, su código base va a:
- `01_Core_Platform/04_Automations_and_Workflows/01_Telegram_Bots/` (Para bots de chat)
- `01_Core_Platform/04_Automations_and_Workflows/02_Voice_Agents/` (Para agentes de voz como Aztrotech)
- `01_Core_Platform/04_Automations_and_Workflows/03_Accounting_Agents/` (Para bots de contabilidad como Nathaly)
Recuerda que las bases de datos y la memoria se gestionan vía los enlaces en `03_Agentic_Infrastructure/`.
# SYSTEM MANIFEST - Sonora Digital Corp
## Reglas de Automatización y IAs (OpenCode / OpenHands)

Cualquier agente de IA, script de automatización o desarrollador DEBE seguir esta estructura. 
La creación de carpetas NO está permitida sin autorización. Trabaja en el contexto de las carpetas existentes.

### Estructura de Clientes (Multitenant)
Cada cliente tiene 4 capas estrictas:
1. `01_Discovery/` -> Requisitos, .md, briefs, prompts base.
2. `02_Source_Code/` -> Código fuente (.py, .js, .feature). Sub-carpetas: /Skills, /Bots, /Agentes.
3. `03_Media_Assets/` -> Recursos visuales y de audio (.mp3, .png, .wav).
4. `04_Deployment/` -> Bases de datos en vivo (.db, .sqlite), variables de entorno (.env) de producción.

### Reglas de la IA (STRICT)
- Si te piden crear un Bot para Aztrotech, el código va a: `02_Client_Projects/Aztrotech/02_Source_Code/Bots/`
- Si te piden crear una Skill de voz, el código va a: `02_Client_Projects/Aztrotech/02_Source_Code/Skills/`
- El Sandbox `03_Sandbox_and_RnD/` es el ÚNICO lugar donde puedes crear carpetas temporales si estás haciendo pruebas. Nunca ensucies la raíz del cliente.
- PROHIBIDO inicializar `npm install` o `pip install` en la raíz de un cliente sin antes crear una carpeta `node_modules` local controlada.

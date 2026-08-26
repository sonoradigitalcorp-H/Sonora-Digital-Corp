# language: es

Característica: Sistema Sonora Digital Corp end-to-end — verificación sin mentiras
  Como dueño del ecosistema SDC
  Quiero verificar que TODOS los componentes funcionan de verdad (no autoengaños)
  Para confiar en que el sistema opera 24/7 con costo $0 (Ollama local)

  Regla de negocio: "Sin mentiras" significa que cada test consulta el estado REAL
  (SSH al VPS, HTTP real, SQL real, no mocks ni aserciones de código estático).

  @infra @fume-free
  Escenario: El VPS está vivo con 7 servicios y Ollama local responde
    Dado el VPS 149.56.46.173 accesible por SSH
    Cuando consulto los servicios systemd y docker
    Entonces los 7 servicios críticos están "active" o "Up"
    Y Ollama responde en 127.0.0.1:11434 con modelos locales

  @modelos @gratis
  Escenario: Los modelos locales $0 existen y generan embeddings
    Dado Ollama corriendo en el VPS
    Entonces "qwen3:4b" está disponible para LLM
    Y "nomic-embed-text" genera vectores de 768 dimensiones
    Y "all-minilm" genera vectores de 384 dimensiones

  @apikeys
  Escenario: Las API keys configuradas son válidas
    Dado el entorno ~/.hermes/.env en el VPS
    Entonces OPENROUTER_API_KEY responde (o falla limpio sin bloquear)
    Y OLLAMA_ENDPOINT apunta a 127.0.0.1:11434 (local, no pública)

  @hermes
  Escenario: Hermes gateway y AI server responden con modelo local
    Dado el gateway Hermes en :8642 y AI server en :8643
    Entonces /health responde 200 en ambos
    Y la config.yaml usa "custom:ollama-local" con qwen3:4b

  @mcp
  Escenario: El túnel MCP expone gateway+api+ollama en local
    Dado el servicio hermes-tunnel activo en la laptop
    Entonces localhost:8642, :8643 y :11434 responden 200

  @cowork
  Escenario: La conexión cowork entre agentes funciona (MCP hermes-agents)
    Dado el MCP hermes_agents_mcp.py
    Entonces lista los agentes registrados sin skills fantasma
    Y cada agente tiene persona, skills y composio_toolkits coherentes

  @metadata
  Escenario: La colección de metadata por tenant está poblada
    Dado Qdrant en el VPS
    Entonces la colección "tubandera_kb" tiene 66+ puntos con vectores 768d
    Y el tenant_id de cada punto es trazable

  @rag
  Escenario: La inyección RAG por tenant_id aísla la memoria
    Dado un tenant_id válido (TB-<chat_id>)
    Entonces la búsqueda semántica devuelve chunks del dominio correcto
    Y no mezcla chunks de otros tenants

  @bases
  Escenario: Las bases de datos sirven y están pobladas
    Dado las BDs SQLite en /opt/hermes
    Entonces citas_sdc.db tiene 3 citas
    Y tubandera.db tiene 2 usuarios
    Y leads_hermosillo_cont.db tiene 1 lead y 36 conversaciones
    Y tu_bandera_leads.db tiene 8 reportes_y_leads

  @wacli
  Escenario: WACLI está autenticado y con keepalive 24/7
    Dado wacli instalado en /home/mystic/wacli
    Entonces AUTHENTICATED es true y LINKED_JID es 5216623538272
    Y el servicio wacli-keepalive está active y "Connected"

  @composio
  Escenario: Composio está disponible para los agentes
    Dado el binario composio en el VPS
    Entonces composio --version responde
    Y las conexiones activas son consultables

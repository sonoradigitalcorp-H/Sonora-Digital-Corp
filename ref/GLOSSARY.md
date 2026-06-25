# GLOSARIO — Sonora Digital Corp
## Terminos y Definiciones Oficiales

---

### A
- **ABE Music**: Producto de management musical. Artistas: Hector Rubio, Jesus Urquijo, Javier Arvayo.
- **ADK**: Agent Development Kit. Framework para crear agentes AI.
- **Agile**: Metodologia de desarrollo iterativa e incremental (Manifesto for Agile Software Development, 2001).

### B
- **BDD**: Behavior-Driven Development. Metodo agil donde el comportamiento esperado se define en formato Given-When-Then antes de codificar (North, 2006).
- **BGE-M3**: Modelo de embeddings multilingue de BAAI. Soporta 100+ idiomas. 569M parametros.

### C
- **Certbot**: Cliente ACME de Let's Encrypt para certificados SSL automaticos.
- **COCOMO**: Constructive Cost Model. Modelo de estimacion de costos de software (Boehm, 1981).
- **Cron**: Programador de tareas en Unix/Linux.

### D
- **Docker**: Plataforma de contenedores. Version 29.6.0 en VPS.
- **DNS**: Domain Name System. Hostinger apunta `sonoradigitalcorp.com` a 149.56.46.173.
- **DPO**: Direct Preference Optimization. Tecnica de RL para alinear LLMs.

### E
- **EDD**: Event-Driven Development. Desarrollo impulsado por eventos donde los componentes se comunican asincronamente (Fowler, 2017).
- **EDA**: Event-Driven Architecture. Patron arquitectonico de comunicacion por eventos.

### G
- **Gherkin**: Lenguaje de dominio especifico para BDD. Formato: Given-When-Then.
- **GRPO**: Group Relative Policy Optimization. Tecnica de RL usada en Qwen2.5.

### H
- **Hermes**: Framework de agente AI autonomo de Nous Research. Se ejecuta como sistema de puerta de enlace.
- **Hostinger**: Proveedor de DNS para `sonoradigitalcorp.com`.

### J
- **JARVIS**: Just Another Robust Versatile Intelligence System. Orquestador de agentes AI de SDC.
- **JBehave**: Framework de BDD para Java creado por Dan North (2003).

### L
- **LLM**: Large Language Model. Modelo de lenguaje grande.
- **Let's Encrypt**: Autoridad certificadora gratuita que provee SSL via certbot.

### M
- **MCP**: Model Context Protocol. Protocolo para conectar modelos de lenguaje con herramientas externas.
- **MTEB**: Massive Text Embedding Benchmark. Benchmark estandar para evaluar modelos de embeddings.
- **MoE**: Mixture of Experts. Arquitectura de modelo que activa solo un subconjunto de parametros.

### N
- **n8n**: Plataforma de automatizacion de workflows self-hosted. Corre en VPS en puerto 5678.
- **Neo4j**: Base de datos de grafos. Usada como ontologia del ecosistema SDC.
- **nginx**: Servidor web y proxy inverso. Sirve SSL, ABE Music API, n8n.
- **nomic-embed-text**: Modelo de embeddings de 137M parametros. 768-dim, 274MB.

### O
- **ODD**: Ontology-Driven Development. Desarrollo impulsado por ontologias formales (Pan et al., 2013).
- **Ollama**: Runtime local para LLMs. "Docker para modelos de lenguaje" (Ollama, 2023).
- **OMEGA**: Operational Methodology for Engineered Growth and Autonomy. Pipeline VDD-EDD-PDD-ODD-SDD-BDD-TDD.
- **OpenClaw**: CLI de ingenieria de software asistida por AI. Version 2026.6.1.
- **OpenCode Go**: API de inferencia cloud gratuita. Modelo deepseek-v4-flash.
- **OVH**: Proveedor de VPS. Servidor SDC en 149.56.46.173.

### P
- **PDD**: Plan-Driven Development. Desarrollo guiado por plan (Boehm, 1986).
- **Phi-4-Mini**: SLM de 3.8B parametros de Microsoft. MIT license. Mejor small reasoning.
- **PostgreSQL**: Base de datos relacional. Corre en contenedor Docker en VPS.

### Q
- **Qdrant**: Base de datos vectorial. Almacena embeddings en coleccion `jarvis_knowledge` (768-dim, Cosine).
- **Qwen2.5**: Familia de LLMs de Alibaba. Modelo 1.5B usado para chat local en VPS.

### R
- **Redis**: Cache en memoria. Corre en contenedor Docker.
- **RUP**: Rational Unified Process. Metodologia plan-driven clasica.

### S
- **SDC**: Sonora Digital Corp. Cliente principal del sistema OMEGA.
- **SDD**: Specification-Driven Development. Desarrollo impulsado por especificaciones. Implementado via SpecKit de GitHub (2025).
- **SLM**: Small Language Model. Modelo de lenguaje pequeno (<10B params).
- **SpecKit**: Toolkit de GitHub para SDD. Flujo: /specify -> /plan -> /tasks.
- **SSL**: Secure Sockets Layer. Certbot + Let's Encrypt para HTTPS.

### T
- **TDD**: Test-Driven Development. Desarrollo guiado por pruebas: Red-Green-Refactor (Beck, 2002).
- **Telegram**: Plataforma de mensajeria. Bot token: 8665900402:AAG0PW36xvlXybG7Heyu-TK9CUFeiVhAa0U.

### U
- **UFW**: Uncomplicated Firewall. Puertos: 22/80/443.
- **Ubuntu 26.04**: Sistema operativo del VPS.

### V
- **VDD**: Value-Driven Design. Diseno maximizando valor del sistema (Collopy & Hollingsworth, 2011).
- **VPS**: Virtual Private Server. OVH, 11GB RAM, 96GB SSD.

### W-Z
- **Workflow**: Automatizacion en n8n. 47 workflows pendientes de migrar.
- **nomic-embed-text**: Modelo de embeddings principal. 274MB, 768-dim.
- **qwen2.5:1.5b**: Modelo de chat local. ~1.1GB Q4_K_M.
- **deepseek-v4-flash**: Modelo cloud de fallback via OpenCode Go.

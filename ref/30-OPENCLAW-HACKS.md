# 30+ OPENCLAW/OPENCODE HACKS
## Como usar OpenClaw al maximo — Para Danny
## 2026-06-25

---

### HACKS DE PRODUCTIVIDAD DIARIA

**1. Atajo mental: `/skill`**
```bash
/skill nombre-del-skill
# Carga cualquier skill en medio de la conversacion sin reiniciar
```

**2. Plan mode toggle**
```bash
# Cuando quieras que solo lea y planee sin ejecutar:
"entra en plan mode"
# Para que ejecute:
"adelante", "go", "exit plan mode", "ejecuta"
```

**3. Modo bala (urgencia)**
```bash
# Cuando necesites algo YA:
"RAPIDO: [tu pedido]"
"URGENTE: [tu pedido]"
"FABOR: [tu pedido]"
# -> OpenClaw salta toda planeacion y ejecuta directo
```

**4. Sesiones continuas (no perder contexto)**
```bash
# Cada sesion carga automaticamente:
# 1. rules.json (18 reglas duras)
# 2. BOOT.md (quick reference)
# 3. AGENTS.md (config)
# No necesitas repetir contexto
```

**5. Output minimalista**
```bash
# OpenClaw por defecto da respuestas largas.
# Si quieres solo el resultado:
"resumido", "directo", "sin explicacion"
# Se activa R-019: una linea por resultado
```

**6. Debug rapido de errores**
```bash
# Cuando un comando falla:
"fix: [el error que viste]"
# OpenClaw busca en learning loop si ya resolvio esto antes
```

**7. Preview de HTML antes de desplegar**
```bash
# Cuando creo una pagina:
"abrela en mi pantalla"
# -> abre Chrome fullscreen con el HTML
```

---

### HACKS DE INFRAESTRUCTURA

**8. Estado completo del sistema**
```bash
"status"
# -> Muestra: RAM, disco, Docker, Ollama, n8n, SSL, servicios systemd
```

**9. Deploy instantaneo**
```bash
"deploy"
# -> rsync archivos estaticos + recarga nginx + verificacion HTTP 200
```

**10. Logs de cualquier servicio**
```bash
"logs:abe"     # ABE Music API
"logs:n8n"     # n8n workflows
"logs:ollama"  # Ollama inference
"logs:nginx"   # nginx access/error
```

**11. Importar workflows a n8n**
```bash
"n8n:import [archivo.json]"
# -> sanitiza formato, llama API, verifica importacion
```

**12. Backup manual rapido**
```bash
"backup"
# -> dump PostgreSQL + export Neo4j + snapshot Qdrant
```

**13. Git auto-sync**
```bash
"push"
# -> git add -A + commit mensaje IA + git push
```

**14. Ver certificados SSL**
```bash
"ssl:check"
# -> muestra dias restantes para cada dominio
```

---

### HACKS DE DISENO

**15. Pagina Apple instantanea**
```bash
"crea landing Apple-style para [X]"
# -> TailwindCSS + Apple design system + CTAs + despliegue
```

**16. Dashboard de datos**
```bash
"dashboard: [tema]"
# -> genera HTML con graficos, tablas, status
```

**17. Pagina de comparacion**
```bash
"compara [X] vs [Y]"
# -> tabla responsiva con colores, badges, recomendacion
```

**18. Landing con variante de nicho**
```bash
"variante: [producto] para [nicho]"
# -> reencuadre psicologico + landing + 3 ads copy
```

---

### HACKS DE CONTENIDO

**19. Generar contenido para redes**
```bash
"contenido: [tema]"
# -> LLM escribe + humanizer quita AI-isms + fal.ai imagen
```

**20. Repurpose (1 video → 10 piezas)**
```bash
"repurpose: [URL o tema]"
# -> blog post + 5 tweets + LinkedIn thread + 3 Instagram + newsletter
```

**21. Humanizar texto**
```bash
"humaniza: [texto]"
# -> quita 29 patrones AI: "en el mundo actual", "sin embargo", etc.
```

**22. Generar imagen con fal.ai**
```bash
"imagen: [prompt en espanol]"
# -> flux-dev, 1 imagen, alta calidad
```

---

### HACKS DE VENTAS

**23. Calificar lead**
```bash
"lead: [mensaje del prospecto]"
# -> fit_score + intent_score + recomendacion de accion
```

**24. Generar propuesta comercial**
```bash
"propuesta para [cliente] con [plan]"
# -> HTML Apple-style + precio + casos de exito + CTA
```

**25. Contrato simple**
```bash
"contrato: [cliente] por [plan] a [precio]"
# -> genera documento listo para firmar
```

**26. Plan de cobranza**
```bash
"cobranza: [cliente] debe [monto] desde [fecha]"
# -> calcula recargos + genera mensaje de cobro + schedule follow-ups
```

---

### HACKS DE APRENDIZAJE

**27. Capturar leccion aprendida**
```bash
# Despues de un error:
"aprendizaje: [que paso] → [solucion]"
# -> Se guarda en events.jsonl para nunca repetirlo
```

**28. Ver progreso de mejora**
```bash
"mejora:status"
# -> muestra: eventos capturados, reglas activas, confidence scores
```

**29. Forzar promocion de leccion a regla**
```bash
"promote: [leccion]"
# -> convierte leccion en regla MUST/NEVER/PREFER
```

**30. Auto-auditoria semanal**
```bash
"audit"
# -> learning loop self-audit: 23 checks de salud del sistema
```

---

### HACKS DE DESARROLLO

**31. Crear skill desde proceso**
```bash
"crea skill para [proceso que repetimos]"
# -> skill-creator genera SKILL.md con scripts, referencias, assets
```

**32. Buscar en todo el sistema**
```bash
# En vez de preguntarme "donde esta X":
"encuentra: [archivo o config]"
# -> busca en todo el filesystem y devuelve ruta exacta
```

**33. Generar tareas (SpecKit)**
```bash
"/sdd-new [feature]"
# -> spec → plan → tasks → implement
```

**34. Ver arquitectura del sistema**
```bash
"mapa"
# -> muestra grafo de servicios, dependencias, puertos
```

---

### HACKS DE MONITOREO

**35. Watchdog en tiempo real**
```bash
"watchdog:on"
# -> activa monitoreo cada 5 min, auto-fix si algo cae
```

**36. Reporte diario**
```bash
"reporte"
# -> leads nuevos + ventas + contenido publicado + errores
```

**37. Clientes en riesgo**
```bash
"churn:check"
# -> clientes con baja actividad, ultima interaccion, score de salud
```

**38. Estado de workflows n8n**
```bash
"n8n:status"
# -> lista todos los workflows, activos/inactivos, ultima ejecucion
```

---

### HACKS DE COMUNICACION

**39. Enviar mensaje a Noel/CEO**
```bash
"notifica: [mensaje]"
# -> envia por Telegram al CEO
```

**40. Compartir avance**
```bash
"comparte con Noel: [resumen]"
# -> push a GitHub + Telegram con resumen
```

**41. Resumen de sesion**
```bash
"summary"
# -> que se hizo, que falta, que sigue
```

**42. Preguntar sin que pregunte**
```bash
# Si no entiendes que quiero:
"te entiendo. Esto es lo que voy a hacer: [plan]. ¿Confirmas?"
# -> valida antes de ejecutar
```

---

### HACK AVANZADO: FLUJO COMPLETO EN UNA LINEA

```bash
# Mañana: "buenos dias. status. reporte. que sigue de la sesion anterior. arranca."
# Esto carga reglas + estado del sistema + pendientes + ejecuta
```

### HACK AVANZADO: PREGUNTA CUANTICA

```bash
# Cuando no sepas que pedir:
"que deberia pedirte que no se me haya ocurrido?"
# -> OpenClaw analiza el sistema y propone mejoras no obvias
```

---

### RESUMEN: LOS 10 COMANDOS QUE MAS USARAS

| Comando | Que hace |
|---|---|
| `status` | Estado completo del sistema |
| `deploy` | Publicar cambios en VPS |
| `push` | Git commit + push |
| `lead: [mensaje]` | Calificar prospecto |
| `contenido: [tema]` | Generar post para redes |
| `imagen: [prompt]` | Generar imagen con fal.ai |
| `humaniza: [texto]` | Quitar patrones AI |
| `variante: [prod] para [nicho]` | Product variant generator |
| `aprendizaje: [error] → [fix]` | Capturar leccion |
| `summary` | Resumen de sesion |

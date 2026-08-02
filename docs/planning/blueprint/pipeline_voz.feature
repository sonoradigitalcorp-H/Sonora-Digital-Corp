# language: es
Caracteristica: Pipeline de Voz Completo
  Como prospecto que llama por telefono
  Quiero ser atendido por un agente de voz inteligente
  Para que mi consulta sea resuelta de forma natural y rapida

  Antecedentes:
    Dado que el sistema esta operativo
    Y el tenant "clinica-dental-smile" esta activo en el paquete Elevar
    Y el agente "La Guardiana" esta configurado con knowledge base de odontologia
    Y el numero DID +52-662-XXXX esta asignado al tenant
    Y el modelo Whisper-large-v3 esta cargado en memoria
    Y el modelo Kokoro TTS esta cargado con la voz clonada del Dr. Martinez
    Y el modelo Claude via OpenRouter esta disponible

  Escenario: Llamada entrante de nuevo prospecto - flujo completo feliz
    Cuando llega una llamada al numero +52-662-XXXX
    Entonces FreeSWITCH contesta en menos de 300 milisegundos
    Y el sistema identifica el tenant "clinica-dental-smile" en menos de 100ms
    Y busca historial del caller ID en Redis en menos de 200ms
    Y el resultado es NEW_LEAD (primera vez)

    Cuando Maria dice "Hola, buenas tardes, quisiera informacion sobre sus servicios de limpieza dental"
    Entonces Whisper transcribe el audio en menos de 800 milisegundos
    Y la transcripcion es: "Hola, buenas tardes, quisiera informacion sobre sus servicios de limpieza dental"
    Y el analizador de energia detecta: {tono: "curioso", velocidad: "normal", volumen: "medio", sentimiento: "positivo"}
    Y el Context Retriever etiqueta como NEW_LEAD con confidence 0.95

    Cuando el Orquestador decide asignar a "La Guardiana" en modo educativo
    Entonces envia al LLM el system prompt + contexto del prospecto + medidas de energia
    Y el LLM genera respuesta en menos de 1500 milisegundos
    Y la respuesta incluye: saludo con nombre del negocio "Clinica Dental Smile"
    Y la respuesta incluye: informacion sobre servicios de limpieza dental
    Y la respuesta NO incluye: tacticas de FOMO o manipulacion

    Cuando Kokoro convierte la respuesta a voz
    Entonces la voz suena como el Dr. Martinez (similitud > 0.85)
    Y la velocidad de voz se ajusta al tono del prospecto (tranquila = voz tranquila)
    Y la conversion toma menos de 500 milisegundos

    Cuando FreeSWITCH envia la voz de vuelta
    Entonces la latencia total del pipeline es menor a 2.5 segundos
    Y Maria escucha una respuesta coherente y natural

    Y se registra en PostgreSQL: {tenant_id, caller_id, duracion, transcripcion, sentimiento, agente_asignado}
    Y se almacena en Qdrant el embedding de la conversacion para busqueda semantica
    Y se envia alerta por Telegram al Dr. Martinez: "Nuevo lead calificado: limpieza dental"

    # Metricas de este escenario:
    # | Metrica | Target | Medicion |
    # |---------|--------|----------|
    # | Contestacion FreeSWITCH | < 300ms | Redis timestamp delta |
    # | Transcripcion Whisper | < 800ms | Timer entre audio in y text out |
    # | Analisis de energia | < 300ms | Timer del pipeline VAD |
    # | Context retrieval | < 200ms | Redis cache hit time |
    # | Generacion LLM | < 1500ms | OpenRouter response time |
    # | Conversion TTS | < 500ms | Kokoro inference time |
    # | Latencia total pipeline | < 2500ms | End-to-end measurement |
    # | Similitud de voz | > 0.85 | Cosine similarity score |
    # | Sin FOMO detectado | 100% | Prompt eval classifier |
    # | Registro en BD | < 100ms | INSERT query time |

  Escenario: Prospecto con tono de urgencia
    Dado que el sistema esta operativo
    Y el prospecto Juan llama con voz aguda y rapida
    Cuando Juan dice "URGENTE, me duele mucho una muela, tienen cita hoy?"
    Entonces el analizador de energia detecta: {tono: "agudo", velocidad: "rapida", volumen: "alto", sentimiento: "negativo", urgencia: "alta"}
    Y el Orquestador asigna a "La Guardiana" en modo urgencia
    Y el agente responde con voz energica y calma
    Y el agente ofrece cita inmediata si hay disponibilidad
    Y se envia alerta CRITICA por Telegram al Dr. Martinez

  Escenario: Llamada de prospecto recurrente
    Dado que Maria llamo hace 3 dias y pregunto por blanqueamiento
    Cuando Maria llama nuevamente
    Entonces el Context Retriever carga su historial completo desde Redis
    Y el agente dice "Hola Maria, como sigue tu interes en el blanqueamiento dental?"
    Y Maria NO tiene que repetir informacion previa
    Y el tiempo de contexto retrieval es menor a 200ms

  Escenario: Llamada fuera de horario
    Dado que son las 10:00 PM y la clinica cierra a las 8:00 PM
    Cuando un prospecto llama
    Entonces el agente atiende normalmente (24/7)
    Y el agente informa que la clinica esta cerrada pero ofrece agendar para el dia siguiente
    Y el agente envia confirmacion por WhatsApp al prospecto
    Y el prospecto no detecta que es una IA (naturalidad > 0.8 en encuesta post-llamada)
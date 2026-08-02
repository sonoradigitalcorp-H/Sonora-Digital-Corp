#!/usr/bin/env python3
"""Poblar Qdrant con conocimiento RAG-first de AstroTech.

Añade documentos al collection sdc_knowledge para que el bot responda
con contexto real del catálogo, proceso de ventas, y objeciones comunes.
"""

import sys
import os
import uuid
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

QDRANT_URL = "http://localhost:6333"
COLLECTION = "sdc_knowledge"

DOCUMENTS = [
    {
        "text": """# Proceso de Ventas — AstroTech

## Flujo conversacional del bot
1. **Detección de dolor**: El bot pregunta a qué se dedica el negocio del cliente y qué problema tiene.
2. **Educación**: Explica CÓMO la tecnología resuelve el problema, sin vender.
3. **Diagnóstico**: Identifica si el cliente necesita Empleado Digital, Sistema de Ventas, o Desarrollo a Medida.
4. **Conexión**: Cuando el lead es HOT, ofrece conectar con César para una llamada personalizada.

## Tipos de leads
- **COLD** (0-30): Solo explora. El bot educa, no presiona.
- **WARM** (31-69): Tiene interés. El bot pregunta más sobre su negocio.
- **HOT** (70+): Listo para comprar. El bot ofrece llamada con César inmediatamente.

## Anti-venta (NUNCA violar)
- NUNCA dar precios. Solo "César te da cotización personalizada en llamada."
- NUNCA presionar. Educar antes que vender.
- NUNCA revelar que existe Sonora Digital Corp. El bot es de AstroTech.
""",
        "tags": ["ventas", "proceso", "flujo", "leads", "anti-venta"],
    },
    {
        "text": """# Empleado Digital — Servicio estrella de AstroTech

## Qué es
Agente de IA 24/7 que atiende clientes en WhatsApp, Instagram, Facebook, Telegram.
Responde preguntas, agenda citas, capta leads, y cierra ventas preliminares.

## Cómo funciona
1. Se conecta a los canales del cliente (WhatsApp Business, Instagram, Facebook)
2. Usa RAG ( Retrieval-Augmented Generation) con el catálogo del cliente
3. Aprende de cada conversación (memoria emergente)
4. Clasifica leads automáticamente (cold, warm, hot)
5. Notifica al dueño cuando hay un lead hot

## Diferenciadores
- **RAG-first**: No alucina, responde con datos reales del catálogo
- **Multi-idioma**: Español, inglés, portugués, francés
- **Voz local**: STT con Whisper, TTS con DaliaNeural
- **Memoria emergente**: Recuerda a cada cliente entre sesiones
- **Anti-venta**: Educa antes de vender, nunca presiona

## Para quién es
- Negocios que reciben muchos mensajes y no pueden responder rápido
- Emprendedores que quieren captar leads 24/7 sin contratar personal
- Empresas que quieren profesionalizar su atención al cliente
""",
        "tags": ["empleado-digital", "servicio", "ia", "whatsapp", "rag"],
    },
    {
        "text": """# Sistema de Ventas Autónomo — AstroTech

## Qué es
CRM + agentes de IA + scoring automático que convierte conversaciones en ventas.

## Componentes
1. **CRM**: Base de datos de leads con scoring automático
2. **Agentes IA**: Conversación, seguimiento, y cierre
3. **Scoring**: Clasificación automática cold/warm/hot basada en señales
4. **Notificaciones**: Alertas al dueño cuando hay leads hot
5. **Seguimiento**: Follow-up automático con leads que no respondieron

## Cómo se integra
- Se conecta con el Empleado Digital
- Cada conversación alimenta el scoring
- Los leads hot se notifican inmediatamente
- El follow-up es automático y personalizado

## Resultados esperados
- 3x más leads captados (24/7 vs horario laboral)
- 50% menos tiempo de respuesta
- 2x tasa de conversión con follow-up automático
""",
        "tags": ["sistema-ventas", "crm", "scoring", "leads", "autonomo"],
    },
    {
        "text": """# Desarrollo de Software a la Medida — AstroTech

## Qué es
Desarrollo de ERPs, apps móviles, APIs, y sistemas a la medida del cliente.

## Stack
- **Backend**: Python (FastAPI), Go, Node.js
- **Frontend**: React, Next.js, Flutter
- **Base de datos**: PostgreSQL, Redis, Qdrant
- **IA**: OpenRouter, DeepSeek, GLM, Kimi
- **Infra**: Docker, systemd, self-hosted

## Proceso
1. **Diagnóstico**: Entender el problema del negocio
2. **Diseño**: Arquitectura y prototipo
3. **Desarrollo**: Iteraciones rápidas (2 semanas)
4. **Entrega**: Deploy + capacitación
5. **Soporte**: Mantenimiento y mejoras continuas

## Para quién es
- Empresas que no encuentran software que se ajuste a su proceso
- Negocios que quieren automatizar tareas manuales
- Startups que necesitan un MVP rápido
""",
        "tags": ["desarrollo", "software", "erp", "apps", "medida"],
    },
    {
        "text": """# Empresa 90 Días — AstroTech

## Qué es
Mentoría intensiva de 90 días con César Holguín para transformar tu negocio con IA.

## Incluye
- **Semana 1-2**: Diagnóstico profundo del negocio
- **Semana 3-4**: Implementación de Empleado Digital
- **Semana 5-8**: Sistema de Ventas Autónomo
- **Semana 9-12**: Optimización y escalado

## Para quién es
- Emprendedores que quieren resultados rápidos
- Negocios que están estancados y necesitan un cambio
- Empresarios que quieren adoptar IA pero no saben cómo

## Resultado
Al final de 90 días, el negocio tiene:
- Atención 24/7 automatizada
- Sistema de captación de leads funcionando
- Proceso de ventas optimizado
- Dashboard de métricas en tiempo real
""",
        "tags": ["empresa-90-dias", "mentoria", "cesar", "transformacion"],
    },
    {
        "text": """# Socio Estratégico — AstroTech

## Qué es
Relación de largo plazo donde AstroTech se convierte en el brazo tecnológico del negocio.

## Incluye
- Acc prioritario a nuevas tecnologías
- Consultoría mensual con César
- Mantenimiento y mejora continua de todos los sistemas
- Capacidad para desarrollar nuevas funcionalidades
- Soporte 24/7

## Para quién es
- Empresas que quieren un partner tecnológico de largo plazo
- Negocios que saben que la tecnología es una ventaja competitiva
- Empresarios que no quieren contratar un equipo de desarrollo interno

## Modelo
- Retainer mensual + variable según proyecto
- Incluye todos los servicios de AstroTech
- Revisión trimestral de resultados
""",
        "tags": ["socio", "estrategico", "largo-plazo", "partner"],
    },
    {
        "text": """# Objeciones comunes y cómo manejarlas

## "Es muy caro"
- **Respuesta**: "Entiendo. Lo importante es que veas el valor, no el costo. Un Empleado Digital atiende 24/7 sin que pagues sueldo, IMSS, ni vacaciones. ¿Te parece si vemos juntos cuánto te cuesta hoy no tener respuesta automática? César te puede dar una cotización personalizada."

## "No tengo tiempo de implementar"
- **Respuesta**: "Para eso existimos. Nosotros nos encargamos de todo: implementación, configuración, capacitación. Tú solo nos dices qué quieres lograr y nosotros lo construimos."

## "Ya tengo un sistema"
- **Respuesta**: "Genial. ¿Y cómo te está funcionando? Lo que hacemos no es reemplazar, es complementar. Si ya tienes algo funcionando, lo integramos para que sea aún mejor."

## "No confío en la IA"
- **Respuesta**: "Totalmente comprensible. La IA no reemplaza a las personas, las potencia. Nuestro Empleado Digital no toma decisiones por ti, solo atiende las conversaciones repetitivas para que tu equipo se enfoque en lo importante. ¿Quieres ver una demostración de cómo funciona?"

## "Dame el precio"
- **Respuesta**: "Los mejores precios te los da César en una llamada, porque cada negocio es diferente. ¿Te parece si le pido que te contacte? Así te da una cotización personalizada."
""",
        "tags": ["objeciones", "ventas", "manejo", "respuestas"],
    },
    {
        "text": """# Tecnologías de AstroTech

## IA y LLMs
- **DeepSeek V4 Flash**: Modelo principal del bot (rápido, económico)
- **GLM-5.2**: Razonamiento complejo
- **Kimi K3**: Tareas de código premium
- **FastEmbed MiniLM**: Embeddings locales (384 dim)

## Infraestructura
- **PostgreSQL**: Base de datos principal
- **Qdrant**: Vector database para RAG
- **Redis**: Cache de sesiones
- **Docker**: Contenedores para servicios
- **systemd**: Servicios 24/7 con auto-restart

## Canales
- **Telegram**: Bot principal (@AztroTechBot)
- **WhatsApp**: wacli (sandbox)
- **Voz**: Whisper STT + edge-tts DaliaNeural TTS

## Memoria
- **Engram**: Memoria emergente (SQLite, por capas)
- **Qdrant**: RAG knowledge base
- **Postgres**: Conversaciones y métricas persistentes
""",
        "tags": ["tecnologias", "stack", "ia", "infraestructura"],
    },
]


def get_embedding(text: str) -> list:
    """Genera embedding local con FastEmbed."""
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        embeddings = list(model.embed([text[:2000]]))
        return embeddings[0].tolist()
    except Exception as e:
        print(f"FastEmbed error: {e}")
        import random
        return [random.uniform(-0.1, 0.1) for _ in range(384)]


def upsert_point(point_id: str, text: str, tags: list):
    """Inserta un punto en Qdrant."""
    vector = get_embedding(text)
    payload = {"text": text, "tags": ", ".join(tags), "source": "catalog"}
    resp = requests.put(
        f"{QDRANT_URL}/collections/{COLLECTION}/points",
        json={"points": [{"id": point_id, "vector": vector, "payload": payload}]},
        timeout=30,
    )
    if resp.status_code == 200:
        print(f"  ✅ {point_id}: {tags}")
    else:
        print(f"  ❌ {point_id}: {resp.status_code} {resp.text[:100]}")


def main():
    print(f"📚 Poblando Qdrant collection '{COLLECTION}'...")
    for doc in DOCUMENTS:
        point_id = str(uuid.uuid4())
        upsert_point(point_id, doc["text"], doc["tags"])
    print(f"\n✅ {len(DOCUMENTS)} documentos añadidos a Qdrant")


if __name__ == "__main__":
    main()
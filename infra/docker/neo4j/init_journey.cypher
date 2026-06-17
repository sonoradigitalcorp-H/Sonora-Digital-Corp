// JARVIS Neo4j Schema Init
// Run this script to initialize the Neo4j database for JARVIS

// ========== CONSTRAINTS ==========
// Session
CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.id IS UNIQUE;

// Message
CREATE CONSTRAINT message_id_unique IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE;

// Persona
CREATE CONSTRAINT persona_id_unique IF NOT EXISTS FOR (p:Persona) REQUIRE p.id IS UNIQUE;

// Proyecto
CREATE CONSTRAINT proyecto_id_unique IF NOT EXISTS FOR (p:Proyecto) REQUIRE p.id IS UNIQUE;

// Tarea
CREATE CONSTRAINT tarea_id_unique IF NOT EXISTS FOR (t:Tarea) REQUIRE t.id IS UNIQUE;

// Concepto
CREATE CONSTRAINT concepto_id_unique IF NOT EXISTS FOR (c:Concepto) REQUIRE c.id IS UNIQUE;

// ========== INDEXES ==========
// Session indexes
CREATE INDEX session_title_fulltext IF NOT EXISTS FOR (s:Session) ON (s.title);
CREATE INDEX session_project IF NOT EXISTS FOR (s:Session) ON (s.project);
CREATE INDEX session_tags IF NOT EXISTS FOR (s:Session) ON (s.tags);
CREATE INDEX session_pinned IF NOT EXISTS FOR (s:Session) ON (s.pinned);
CREATE INDEX session_archived IF NOT EXISTS FOR (s:Session) ON (s.archived);
CREATE INDEX session_created_at IF NOT EXISTS FOR (s:Session) ON (s.created_at);
CREATE INDEX session_updated_at IF NOT EXISTS FOR (s:Session) ON (s.updated_at);

// Message indexes
CREATE INDEX message_timestamp IF NOT EXISTS FOR (m:Message) ON (m.timestamp);
CREATE INDEX message_role IF NOT EXISTS FOR (m:Message) ON (m.role);

// Persona indexes
CREATE INDEX persona_nombre IF NOT EXISTS FOR (p:Persona) ON (p.nombre);

// Proyecto indexes
CREATE INDEX proyecto_nombre IF NOT EXISTS FOR (p:Proyecto) ON (p.nombre);

// ========== FULL-TEXT SEARCH ==========
CREATE FULLTEXT INDEX session_ft IF NOT EXISTS
FOR (n:Session)
ON EACH [n.title];

CREATE FULLTEXT INDEX message_ft IF NOT EXISTS
FOR (n:Message)
ON EACH [n.content];

// ========== SAMPLE SESSION ==========
CREATE (s:Session {
    id: randomUUID(),
    title: "Bienvenido a JARVIS",
    pinned: true,
    project: "JARVIS",
    tags: ["demo", "welcome", "first"],
    archived: false,
    created_at: datetime(),
    updated_at: datetime(),
    token_count: 0,
    cost: 0.0
})
RETURN s;

CREATE (m:Message {
    id: randomUUID(),
    role: "assistant",
    content: "¡Hola! Soy JARVIS, tu asistente de IA. ¿En qué puedo ayudarte?",
    tokens: 15,
    timestamp: datetime()
});

MATCH (s:Session), (m:Message)
WHERE s.project = "JARVIS" AND m.content CONTAINS "Hola"
CREATE (s)-[:CONTAINS]->(m)
RETURN s, m;

// ========== SAMPLE ENTITIES ==========
CREATE (p:Persona:Entity {
    id: randomUUID(),
    nombre: "Usuario",
    rol: "developer",
    idioma: "es-MX",
    tema: "cyberpunk"
});

CREATE (pr:Proyecto:Entity {
    id: randomUUID(),
    nombre: "JARVIS",
    status: "active",
    descripcion: "Asistente de IA con memoria persistente"
});

CREATE (c:Concepto:Entity {
    id: randomUUID(),
    nombre: "Graph RAG",
    definicion: "Retrieval-Augmented Generation con base de datos de grafos"
});

MATCH (p:Persona {nombre: "Usuario"}), (pr:Proyecto {nombre: "JARVIS"})
CREATE (p)-[:TRABAJA_EN]->(pr);

MATCH (pr:Proyecto {nombre: "JARVIS"}), (c:Concepto {nombre: "Graph RAG"})
CREATE (pr)-[:UTILIZA]->(c);

// ========== VERIFICATION ==========
// Check that everything was created
MATCH (n)
RETURN labels(n) as type, count(n) as count
ORDER BY count DESC;

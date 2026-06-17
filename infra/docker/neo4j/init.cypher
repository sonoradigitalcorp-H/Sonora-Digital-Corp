// Neo4j Schema Initialization for JARVIS
// Ejecutar en Neo4j Browser o via cypher-shell

// Crear constraints para IDs únicos
CREATE CONSTRAINT conversation_id IF NOT EXISTS
FOR (c:Conversation) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT project_id IF NOT EXISTS
FOR (pr:Project) REQUIRE pr.id IS UNIQUE;

CREATE CONSTRAINT task_id IF NOT EXISTS
FOR (t:Task) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT concept_id IF NOT EXISTS
FOR (co:Concept) REQUIRE co.id IS UNIQUE;

// Crear índices para búsqueda rápida
CREATE INDEX conversation_timestamp IF NOT EXISTS
FOR (c:Conversation) ON (c.timestamp);

CREATE INDEX conversation_text IF NOT EXISTS
FOR (c:Conversation) ON (c.text);

CREATE INDEX person_name IF NOT EXISTS
FOR (p:Person) ON (p.name);

CREATE INDEX project_name IF NOT EXISTS
FOR (pr:Project) ON (pr.name);

CREATE INDEX task_title IF NOT EXISTS
FOR (t:Task) ON (t.title);

CREATE INDEX concept_name IF NOT EXISTS
FOR (co:Concept) ON (co.name);

// Full-text index para búsqueda de texto completo
CALL db.index.fulltext.createNodeIndex("conversationText", ["Conversation"], ["text"]);

CALL db.index.fulltext.createNodeIndex("personName", ["Person"], ["name"]);

CALL db.index.fulltext.createNodeIndex("projectName", ["Project"], ["name"]);

// Crear nodos iniciales de ejemplo
CREATE (jarvis:Person {
    id: 'jarvis-001',
    name: 'JARVIS',
    role: 'AI Assistant',
    created_at: datetime()
})

CREATE (luis:Person {
    id: 'luis-001',
    name: 'Luis',
    role: 'Owner',
    created_at: datetime()
})

CREATE (jarvisProject:Project {
    id: 'project-jarvis',
    name: 'JARVIS AI System',
    status: 'active',
    start_date: date(),
    description: 'Sistema de IA avanzado con memoria persistente'
})

CREATE (neo4jConcept:Concept {
    id: 'concept-neo4j',
    name: 'Neo4j',
    category: 'database',
    description: 'Base de datos de grafos'
})

CREATE (qdrantConcept:Concept {
    id: 'concept-qdrant',
    name: 'Qdrant',
    category: 'database',
    description: 'Base de datos vectorial'
})

CREATE (mcpConcept:Concept {
    id: 'concept-mcp',
    name: 'MCP',
    category: 'protocol',
    description: 'Model Context Protocol'
})

// Crear relaciones
MATCH (luis:Person {id: 'luis-001'})
MATCH (jarvis:Person {id: 'jarvis-001'})
CREATE (luis)-[:OWNS]->(jarvis)

MATCH (luis:Person {id: 'luis-001'})
MATCH (project:Project {id: 'project-jarvis'})
CREATE (luis)-[:DEVELOPS]->(project)

MATCH (jarvis:Person {id: 'jarvis-001'})
MATCH (project:Project {id: 'project-jarvis'})
CREATE (jarvis)-[:IS_PART_OF]->(project)

MATCH (project:Project {id: 'project-jarvis'})
MATCH (neo4j:Concept {id: 'concept-neo4j'})
MATCH (qdrant:Concept {id: 'concept-qdrant'})
MATCH (mcp:Concept {id: 'concept-mcp'})
CREATE (project)-[:USES]->(neo4j)
CREATE (project)-[:USES]->(qdrant)
CREATE (project)-[:USES]->(mcp)

// SDC Business Layer — Customer y Subscription
CREATE CONSTRAINT customer_id IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT subscription_id IF NOT EXISTS
FOR (s:Subscription) REQUIRE s.id IS UNIQUE;

CREATE INDEX customer_email IF NOT EXISTS
FOR (c:Customer) ON (c.email);

CREATE INDEX customer_plan IF NOT EXISTS
FOR (c:Customer) ON (c.plan);

// ABE MUSIC — Artist, Label, Release
CREATE CONSTRAINT artist_id IF NOT EXISTS
FOR (a:Artist) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT release_id IF NOT EXISTS
FOR (r:Release) REQUIRE r.id IS UNIQUE;

CREATE INDEX artist_name IF NOT EXISTS
FOR (a:Artist) ON (a.nombre);

CREATE INDEX artist_genre IF NOT EXISTS
FOR (a:Artist) ON (a.genero);

CREATE INDEX release_title IF NOT EXISTS
FOR (r:Release) ON (r.titulo);

// Retornar resumen
MATCH (n) RETURN labels(n) as type, count(n) as count

# language: es
Funcionalidad: Onboarding — Memoria persistente
  Como sistema SDC
  Quiero guardar cada activación en Engram, Qdrant y Neo4j
  Para que el agente tenga contexto completo del cliente

  Escenario: Engram guarda la activación
    Dado que un cliente activa su cuenta
    Cuando se completa la activación
    Entonces se guarda una observación en Engram con tipo "milestone"
    Y el contenido incluye: "Cliente X activado via onboarding código Y"

  Escenario: Qdrant indexa el perfil del cliente
    Dado que un cliente se activa
    Cuando se completa el onboarding
    Entonces se crea un vector en Qdrant con el perfil del cliente
    Y se puede buscar por "cliente" + "nombre"

  Escenario: Neo4j crea relaciones del cliente
    Dado que un cliente se activa
    Cuando se completa el onboarding
    Entonces se crea un nodo "Cliente" en Neo4j
    Y se crea una relación "CLIENTE_DE" con el partner
    Y se crea una relación "TIENE_PLAN" con su plan

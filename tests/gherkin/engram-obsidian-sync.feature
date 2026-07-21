# language: es
Funcionalidad: Export Obsidian Live para Engram
  Como desarrollador de Sonora Digital Corp
  Quiero que las observaciones de Engram se exporten automáticamente a Obsidian
  Para visualizar el grafo de conocimiento y decisiones

  Escenario: Export inicial genera estructura de vault
    Dado un vault Obsidian vacío en "/obsidian-vault"
    Cuando ejecuto "engram obsidian-export --vault /obsidian-vault"
    Entonces se crean los directorios:
      | directorio               |
      | /obsidian-vault/Observations |
      | /obsidian-vault/Sessions  |
      | /obsidian-vault/Projects  |
      | /obsidian-vault/Graph     |
      | /obsidian-vault/Canvas    |

  Escenario: Cada observación se exporta como .md con frontmatter
    Dado una observación con:
      | campo       | valor                     |
      | title       | "JWT auth middleware"     |
      | type        | "decision"                |
      | project     | "sonora-digital-corp"     |
      | topic_key   | "architecture/auth-model" |
      | version     | "v1.2.3"                  |
      | content     | "**What**: Switched from sessions to JWT" |
    Cuando ejecuto el export
    Entonces existe "/obsidian-vault/Observations/JWT auth middleware.md"
    Y el archivo contiene frontmatter YAML con:
      | campo     | valor                     |
      | title     | "JWT auth middleware"     |
      | type      | decision                  |
      | project   | sonora-digital-corp       |
      | topic_key | architecture/auth-model   |
      | version   | v1.2.3                    |
      | tags      | [engram, decision]        |

  Escenario: Export incremental solo procesa cambios
    Dado que ya se exportaron 10 observaciones
    Cuando agrego 3 observaciones nuevas
    Y ejecuto el export nuevamente
    Entonces solo se procesan las 3 nuevas
    Y las 10 existentes no se re-escriben

  Escenario: Graph de relaciones entre observaciones
    Dado que la obs A "supersedes" a la obs B
    Y la obs A "related" a la obs C
    Cuando ejecuto el export
    Entonces "/obsidian-vault/Graph/relationships.md" contiene:
      | contenido                                 |
      | "A -> supersedes -> B"                    |
      | "A -> related -> C"                       |

  Escenario: Archivos son compatibles con Dataview
    Dado un archivo exportado "Observations/test.md"
    Cuando se analiza con Dataview
    Entonces el frontmatter es parseable como YAML válido
    Y contiene al menos los campos: title, type, project, created_at

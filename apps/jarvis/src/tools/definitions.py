TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Ejecutar un comando en el sistema (whitelist: ls, pwd, date, cat, find, grep, python, docker ps, git status, pip list, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Comando a ejecutar"},
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout en segundos (default: 30)",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Leer el contenido de un archivo del proyecto",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo (relativa al proyecto)",
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Máximo de líneas a leer (default: 100)",
                        "default": 100,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Escribir o modificar un archivo del proyecto. CUIDADO: Sobrescribe el archivo existente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del archivo (relativa al proyecto)",
                    },
                    "content": {
                        "type": "string",
                        "description": "Contenido completo del archivo",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Listar archivos y directorios en una ruta del proyecto",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio (relativa al proyecto, default: '.')",
                        "default": ".",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Filtro glob (ej: '*.py', '**/*.md')",
                        "default": None,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Ejecutar tests del proyecto con pytest",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta de tests a ejecutar (default: 'tests/')",
                        "default": "tests/",
                    },
                    "verbose": {
                        "type": "boolean",
                        "description": "Output verbose (default: false)",
                        "default": False,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Buscar texto en el código del proyecto",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Patrón de búsqueda (regex)",
                    },
                    "path": {
                        "type": "string",
                        "description": "Ruta donde buscar (default: '.')",
                        "default": ".",
                    },
                    "include": {
                        "type": "string",
                        "description": "Filtro de archivos (ej: '*.py')",
                        "default": "*.py",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "docker_build",
            "description": "Construir una imagen Docker desde un Dockerfile",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del directorio con Dockerfile",
                        "default": ".",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Tag de la imagen (ej: 'jarvis/my-service:latest')",
                        "default": "jarvis/service:latest",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "docker_deploy",
            "description": "Desplegar un contenedor Docker (docker compose up -d)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Ruta del docker-compose.yml (default: '.')",
                        "default": ".",
                    },
                    "service": {
                        "type": "string",
                        "description": "Nombre del servicio a desplegar (opcional, todos si no se especifica)",
                        "default": None,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_semantic",
            "description": "Buscar información en la memoria semántica de JARVIS (RAG vectorial). Devuelve fragmentos relevantes con score de similitud.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Texto a buscar"},
                    "limit": {
                        "type": "integer",
                        "description": "Máximo de resultados",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rag_store",
            "description": "Guardar un fragmento de información en la memoria semántica de JARVIS (RAG vectorial). Útil para recordar algo importante.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto a guardar"},
                    "source": {
                        "type": "string",
                        "description": "Fuente del texto (ej: 'conversación', 'documento', 'código')",
                        "default": "conversación",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ask_user",
            "description": "Preguntar algo al usuario cuando necesitas más información",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Pregunta para el usuario",
                    }
                },
                "required": ["question"],
            },
        },
    },
]

ALLOWED_COMMANDS = [
    "ls",
    "pwd",
    "date",
    "whoami",
    "uptime",
    "uname",
    "id",
    "cat",
    "head",
    "tail",
    "wc",
    "echo",
    "sort",
    "uniq",
    "find",
    "grep",
    "rg",
    "ag",
    "ack",
    "python3",
    "python",
    "pip",
    "pip3",
    "docker ps",
    "docker images",
    "docker compose ps",
    "git status",
    "git log",
    "git diff",
    "git branch",
    "systemctl status",
    "df",
    "free",
    "du",
    "ps",
    "pytest",
    "black",
    "flake8",
    "pylint",
    "which",
    "type",
    "file",
    "stat",
    "mkdir",
    "cp",
    "mv",
    "rm",
]

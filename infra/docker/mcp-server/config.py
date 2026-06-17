"""
JARVIS MCP Server Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "jarvis2026")

# Qdrant Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# MCP Server Configuration
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

# Allowed commands for jarvis_execute
ALLOWED_COMMANDS = [
    "ls",
    "pwd",
    "date",
    "whoami",
    "uptime",
    "docker ps",
    "systemctl status",
    "df",
    "free",
]

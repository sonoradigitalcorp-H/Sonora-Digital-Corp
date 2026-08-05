# Wrapper para Engram MCP - Sonora Digital Corp
import subprocess
import sys
import json

def search_memory(query, client_name="Unknown", limit=10):
    """
    Busca en la memoria persistente de Engram para un cliente específico.
    """
    print(f"[Hermes Tool] Buscando memoria para {client_name}: {query}")
    try:
        result = subprocess.run(
            ['engram', 'search', query, '--limit', str(limit)],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error en búsqueda de memoria: {e}"

def save_memory(title, message, client_name="Unknown", memory_type="conversation"):
    """
    Guarda una observación en Engram para un cliente específico.
    """
    print(f"[Hermes Tool] Guardando memoria para {client_name}: {title}")
    try:
        result = subprocess.run(
            ['engram', 'save', title, message, '--type', memory_type, '--project', client_name],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error al guardar memoria: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "search":
            query = sys.argv[2]
            client = sys.argv[3] if len(sys.argv) > 3 else "Unknown"
            limit = int(sys.argv[4]) if len(sys.argv) > 4 else 10
            print(search_memory(query, client, limit))
        elif cmd == "save":
            title = sys.argv[2]
            message = sys.argv[3]
            client = sys.argv[4] if len(sys.argv) > 4 else "Unknown"
            mtype = sys.argv[5] if len(sys.argv) > 5 else "conversation"
            print(save_memory(title, message, client, mtype))

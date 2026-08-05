import os
import sys
import json

BASE_PATH = "02_Client_Projects"
TEMPLATE = ["01_Discovery", "02_Source_Code", "03_Media_Assets/Audio", "03_Media_Assets/Visual", "04_Deployment", "05_Agentic_Skills"]

def onboard(client_name):
    client_path = os.path.join(BASE_PATH, client_name)
    if os.path.exists(client_path):
        print(f"El cliente {client_name} ya existe.")
        return
    
    for folder in TEMPLATE:
        os.makedirs(os.path.join(client_path, folder), exist_ok=True)
    
    # Crear manifiesto del cliente
    manifest = {
        "client_name": client_name,
        "status": "active",
        "infrastructure": {"llm": "hermes", "memory": "engram", "vector_db": "qdrant"}
    }
    with open(os.path.join(client_path, "client_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"✅ Cliente {client_name} onboarded con éxito en {client_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        onboard(sys.argv[1])
    else:
        print("Uso: python onboard_client.py [Nombre_Cliente]")

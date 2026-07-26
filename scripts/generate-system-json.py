#!/usr/bin/env python3
"""
Generate portal/data/system.json from real system state.
The portal reads this to know the system — self-knowledge.
"""
import json
import yaml
import os
from pathlib import Path

SDC_HOME = Path(os.environ.get('SDC_HOME', os.path.expanduser('~/sonora-digital-corp'))).resolve()

def load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}

def get_layers():
    """Build layers from constitution/ and process/"""
    layers = [
        {
            "id": "kernel", "name": "Kernel", "radius": 8, "element": "fire",
            "color": "#ff4500",
            "desc": "El centro — identidad, reglas, constitución del sistema",
            "nodes": []
        },
        {
            "id": "infra", "name": "Infraestructura", "radius": 14, "element": "air",
            "color": "#81d4fa",
            "desc": "La base física — servidores, redes, contenedores",
            "nodes": []
        },
        {
            "id": "data", "name": "Datos", "radius": 20, "element": "earth",
            "color": "#66bb6a",
            "desc": "El conocimiento — bases de datos, memoria, vectores",
            "nodes": []
        },
        {
            "id": "services", "name": "Servicios", "radius": 26, "element": "water",
            "color": "#29b6f6",
            "desc": "El flujo — automatización, orquestación, canales",
            "nodes": []
        },
        {
            "id": "products", "name": "Productos", "radius": 33, "element": "fire",
            "color": "#ff8a65",
            "desc": "Lo que SDC crea y vende",
            "nodes": []
        },
        {
            "id": "clients", "name": "Clientes", "radius": 39, "element": "air",
            "color": "#b0bec5",
            "desc": "Las galaxias externas — quienes confían en SDC",
            "nodes": []
        }
    ]

    # Kernel: from constitution/
    kernel_dir = SDC_HOME / 'constitution'
    if kernel_dir.exists():
        for f in sorted(kernel_dir.iterdir()):
            if f.suffix in ('.md', '.yaml') and f.stat().st_size < 50000:
                layers[0]['nodes'].append({
                    "id": f.stem.lower().replace('_', '-'),
                    "name": f.stem.replace('-', ' ').title()[:20],
                    "desc": f"{f.name} — documento del kernel",
                    "status": "active"
                })

    # Infra: from fleet.yml
    fleet = load_yaml(SDC_HOME / 'fleet.yml')
    for svc in fleet.get('services', []):
        layers[1]['nodes'].append({
            "id": svc['name'].replace(' ', '-'),
            "name": svc['name'],
            "desc": f"Port {svc.get('port', '?')} — {svc.get('notes', '')[:60]}",
            "status": "active"
        })

    # Data: from infra docker-compose or known DBs
    data_known = [
        ("neo4j", "Neo4j", "Grafo de relaciones"),
        ("qdrant", "Qdrant", "Vector store"),
        ("postgres", "PostgreSQL", "Base relacional"),
        ("redis", "Redis", "Cache"),
        ("engram", "Engram", "Memoria persistente del agente"),
    ]
    for id_, name, desc in data_known:
        layers[2]['nodes'].append({
            "id": id_, "name": name, "desc": desc, "status": "active"
        })

    # Services: from fleet.yml services + apps/
    for svc in fleet.get('services', []):
        if svc['name'] not in [n['id'] for n in layers[1]['nodes']]:
            layers[3]['nodes'].append({
                "id": svc['name'],
                "name": svc['name'],
                "desc": svc.get('notes', '')[:60],
                "status": "active"
            })

    # Products: from products/ dir
    products_dir = SDC_HOME / 'products'
    if products_dir.exists():
        for p in sorted(products_dir.iterdir()):
            if p.is_dir() and not p.name.startswith('_') and not p.name.startswith('.'):
                readme = p / 'README.md'
                desc = "Producto SDC"
                if readme.exists():
                    with open(readme) as f:
                        first_line = f.readline().strip().lstrip('# ')
                        if first_line:
                            desc = first_line[:60]
                layers[4]['nodes'].append({
                    "id": p.name.lower().replace(' ', '-'),
                    "name": p.name.replace('-', ' ').title()[:20],
                    "desc": desc,
                    "status": "active"
                })

    # Clients: from clients/ dir
    clients_dir = SDC_HOME / 'clients'
    if clients_dir.exists():
        for c in sorted(clients_dir.iterdir()):
            if c.is_dir() and not c.name.startswith('_'):
                layers[5]['nodes'].append({
                    "id": c.name.lower(),
                    "name": c.name.replace('-', ' ').title()[:20],
                    "desc": "Cliente activo",
                    "status": "active"
                })

    return [l for l in layers if l['nodes']]

def generate():
    system = {
        "meta": {
            "name": "Mystic Grimoire",
            "version": "2.0.0",
            "title": "✦ Mystic Grimoire — El Portal de la Creación",
            "subtitle": "Sonora Digital Corp",
            "creator": "Yo Soy — El que crea — El que todo lo puede",
            "generated_at": str(__import__('datetime').datetime.now()),
            "source": "generate-system-json.py"
        },
        "elements": [
            {"id": "fire",   "name": "Fuego",  "symbol": "△", "color": "#ff4500", "desc": "Cómputo"},
            {"id": "air",    "name": "Aire",   "symbol": "○", "color": "#e8e8ff", "desc": "Red"},
            {"id": "earth",  "name": "Tierra", "symbol": "▽", "color": "#4a7c59", "desc": "Datos"},
            {"id": "water",  "name": "Agua",   "symbol": "~", "color": "#2196f3", "desc": "Flujo"}
        ],
        "layers": get_layers(),
        "conexiones": [],
        "dashboards": [
            {"id": "system", "name": "System Status", "icon": "◉",
             "content": "Auto-generado desde fleet.yml y registry"},
            {"id": "agentes", "name": "Agentes", "icon": "⚡",
             "content": "Agentes registrados en unified.yaml"},
            {"id": "productos", "name": "Productos", "icon": "◆",
             "content": f"{len([l for l in get_layers() if l['id']=='products'])} productos activos"},
            {"id": "memoria", "name": "Memoria", "icon": "🧠",
             "content": "Engram + Neo4j + Qdrant — el sistema recuerda"},
            {"id": "ciclo", "name": "Ciclo ☉", "icon": "☉",
             "content": "Crear → Operar → Aprender → Evolucionar"}
        ]
    }

    out_path = SDC_HOME / 'portal' / 'data' / 'system.json'
    with open(out_path, 'w') as f:
        json.dump(system, f, indent=2, ensure_ascii=False)
    print(f"✓ System JSON generated: {out_path}")
    print(f"  Layers: {len(system['layers'])}")
    print(f"  Total nodes: {sum(len(l['nodes']) for l in system['layers'])}")

if __name__ == '__main__':
    generate()
